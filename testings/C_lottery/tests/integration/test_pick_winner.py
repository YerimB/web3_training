import time

from scripts.useful.tools import (
    get_account,
    wait_for_tx_confs,
    fund_with_link,
)
from scripts.deploy import deploy_lottery
from tests.tools import skip_local, LotteryState


def test_can_pick_winner_correctly():
    skip_local()

    # Init
    owner = get_account()
    contract = deploy_lottery(account=owner)
    lottery_entrance_fee = contract.getEntranceFee()
    wait_for_tx_confs(contract.startLottery({"from": owner, "required_confs": 0}).txid)
    print("Lottery started !")
    # --- Participants entering (Add more if wanted)
    wait_for_tx_confs(
        contract.enter({"from": owner, "value": lottery_entrance_fee}).txid
    )
    print(f"{owner.address} entered the lottery !")

    # Core
    # --- End lottery
    print("Funding lottery with $LINK... ", end="", flush=True)
    fund_with_link(contract, from_account=owner)
    print("Done !")

    wait_for_tx_confs(contract.endLottery({"from": owner}).txid)
    print("Lottery ending : waiting for gamble to process... ", end="", flush=True)
    owner_initial_balance = owner.balance()
    lottery_balance_before_gambling = contract.balance()
    # --- Wait for randomness to come
    timeout = time.time() + 5 * 60  # Set timeout at 5 minutes
    while time.time() < timeout:
        if contract.m_GambleDone() == True:
            print("Done !")
            break
        time.sleep(1)

    # Assert
    assert contract.m_Winner() == owner.address
    assert contract.balance() == 0
    assert owner.balance() == owner_initial_balance + lottery_balance_before_gambling
    assert contract.m_LotteryState() == LotteryState.CLOSED.value
