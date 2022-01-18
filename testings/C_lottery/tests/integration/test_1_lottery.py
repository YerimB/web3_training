import time

from brownie.network.transaction import TransactionReceipt

from scripts.useful.tools import (
    get_account,
    fund_with_link,
)
from scripts.deploy import deploy_lottery
from tests.tools import skip_local, LotteryState
from classes.event_subscriber import EventSubscriber


def test_can_pick_winner_correctly():
    skip_local()

    # Init
    owner = get_account()
    contract = deploy_lottery(account=owner)
    lottery_entrance_fee = contract.getEntranceFee()
    tx = TransactionReceipt(
        contract.startLottery({"from": owner, "required_confs": 0}).txid
    )
    if tx.confirmations == 0:
        tx.wait(1)
    # --- Participants entering (Only one for testing purpose)
    tx = TransactionReceipt(
        contract.enter({"from": owner, "value": lottery_entrance_fee}).txid
    )
    if tx.confirmations == 0:
        tx.wait(1)
    # Fund lottery with link to get random number
    fund_with_link(contract, from_account=owner)

    # Core
    # --- Set callback on RandomnessRequested & RandomnessReceived
    randomness_was_requested = False
    randomness_was_received = False

    def _callback1(_, event_data):
        nonlocal randomness_was_requested
        randomness_was_requested = True

    def _callback2(_, event_data):
        nonlocal randomness_was_received
        randomness_was_received = True

    randomness_requested_callback = EventSubscriber(
        contract, event_name="RandomnessRequested", callback=_callback1
    ).enable(delay=0.5)
    randomness_received_callback = EventSubscriber(
        contract, event_name="RandomnessReceived", callback=_callback2
    ).enable(delay=1)

    # --- End lottery
    tx = TransactionReceipt(contract.endLottery({"from": owner}).txid)
    if tx.confirmations == 0:
        tx.wait(1)
    # All transactions done, getting balance for assertion phase
    owner_initial_balance = owner.balance()
    lottery_balance_before_gambling = contract.balance()
    if randomness_was_requested == False:
        randomness_requested_callback.wait(1, timeout=10)
    # --- Wait for randomness to come
    if randomness_was_received == False:
        randomness_received_callback.wait(1, timeout=300)  # 5 minutes time out

    # Assert
    assert contract.m_Winner() == owner.address
    assert contract.balance() == 0
    assert owner.balance() == owner_initial_balance + lottery_balance_before_gambling
    assert contract.m_LotteryState() == LotteryState.CLOSED.value
