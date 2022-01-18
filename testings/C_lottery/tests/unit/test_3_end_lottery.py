import pytest

from brownie import exceptions

from scripts.deploy import deploy_lottery
from scripts.useful.tools import (
    get_account,
    wait_for_tx_confs,
    fund_with_link,
    get_contract,
)
from tests.tools import only_local, LotteryState


def test_owner_can_end_lottery():
    only_local()

    # Init
    owner = get_account(0)
    contract = deploy_lottery(account=owner)
    wait_for_tx_confs(contract.startLottery({"from": owner}).txid)
    wait_for_tx_confs(
        contract.enter({"from": owner, "value": contract.getEntranceFee()}).txid
    )

    # Core
    fund_with_link(contract, from_account=owner)
    wait_for_tx_confs(contract.endLottery({"from": owner}).txid)

    # Assert
    # --- If passes : Means lottery ending process is in progess
    assert contract.m_LotteryState() == LotteryState.CALCULATING_WINNER.value


def test_not_owner_cannot_end_lottery():
    only_local()

    # Init
    owner = get_account(0)
    bad_actor = get_account(1)
    contract = deploy_lottery(account=owner)

    # Core
    # --- Opens lottery
    wait_for_tx_confs(contract.startLottery({"from": owner}).txid)
    # --- Enter lottery
    wait_for_tx_confs(
        contract.enter({"from": owner, "value": contract.getEntranceFee()}).txid
    )
    fund_with_link(contract, from_account=owner)

    # Assert
    with pytest.raises(exceptions.VirtualMachineError):
        wait_for_tx_confs(contract.endLottery({"from": bad_actor}).txid)
    # --- Check lottery state
    assert contract.m_LotteryState() not in [
        LotteryState.CLOSED.value,
        LotteryState.CALCULATING_WINNER.value,
    ], "Invalid lottery state"


def test_can_pick_winner_correctly():
    only_local()

    # Init
    STATIC_RNG = 368286
    owner = get_account(0)
    contract = deploy_lottery(account=owner)
    lottery_entrance_fee = contract.getEntranceFee()
    wait_for_tx_confs(contract.startLottery({"from": owner}).txid)
    # --- 3 participants entering
    wait_for_tx_confs(
        contract.enter({"from": owner, "value": lottery_entrance_fee}).txid
    )
    wait_for_tx_confs(
        contract.enter(
            {"from": get_account(index=1), "value": lottery_entrance_fee}
        ).txid
    )
    wait_for_tx_confs(
        contract.enter(
            {"from": get_account(index=2), "value": lottery_entrance_fee}
        ).txid
    )

    # Core
    fund_with_link(contract, from_account=owner)
    owner_initial_balance = owner.balance()
    lottery_balance_before_gambling = contract.balance()
    # --- End lottery
    tx = wait_for_tx_confs(contract.endLottery({"from": owner}).txid)
    # --- Simulating callback
    requestId = tx.events["RandomnessRequested"]["requestId"]
    vrf_coordinator = get_contract("vrf_coordinator")
    # --- Dummy the callback to get instance response
    vrf_coordinator.callBackWithRandomness(
        requestId, STATIC_RNG, contract.address, {"from": owner}
    )

    # Assert
    # --- 368286 % 3 == 0 (owner wins)
    assert contract.m_Winner() == owner.address
    assert contract.balance() == 0
    assert owner.balance() == owner_initial_balance + lottery_balance_before_gambling
    assert contract.m_LotteryState() == LotteryState.CLOSED.value
