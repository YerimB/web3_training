import pytest
from brownie import exceptions
from web3 import Web3

from scripts.deploy import deploy_lottery
from scripts.useful.tools import (
    get_account,
    wait_for_tx_confs,
)
from tests.tools import only_local, LotteryState


def test_get_entrance_fee():
    only_local()

    # Init
    # Set lottery entrance fee to 50 $USD
    contract = deploy_lottery(entrance_fee=50)
    # 50 $USD == 0.025 $ETH when 1 $ETH == 2000 $USD
    expected_entrance_fee = Web3.toWei(0.025, "ether")

    # Core
    # --- Get entrance fee from contract
    entrance_fee = contract.getEntranceFee()

    # Assert
    assert entrance_fee == expected_entrance_fee


def test_cannot_enter_when_lottery_closed():
    only_local()

    # Init
    contract = deploy_lottery()
    # Will try to enter the lottery before it starts
    bad_actor = get_account()

    # Core / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        wait_for_tx_confs(
            contract.enter({"from": bad_actor, "value": contract.getEntranceFee()}).txid
        )


def test_cannot_enter_lottery_with_lower_fee():
    only_local()

    # Init
    owner = get_account(0)
    bad_actor = get_account(1)
    contract = deploy_lottery(account=owner)
    entrance_fee = contract.getEntranceFee()
    # --- Start lottery
    wait_for_tx_confs(contract.startLottery({"from": owner}).txid)

    # Core / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        wait_for_tx_confs(
            contract.enter({"from": bad_actor, "value": entrance_fee - 1}).txid
        )


def test_can_start_and_enter_lottery():
    only_local()

    # Init
    owner = get_account(0)
    player = get_account(1)
    contract = deploy_lottery(account=owner)
    entrance_fee = contract.getEntranceFee()

    # Core / Assert
    # --- Start lottery
    wait_for_tx_confs(contract.startLottery({"from": owner}).txid)
    # --- Assert lottery is opened
    assert contract.m_LotteryState() == LotteryState.OPENED.value

    # --- Owner can enter lottery
    wait_for_tx_confs(contract.enter({"from": owner, "value": entrance_fee}).txid)
    # --- Owner has entered lottery
    assert contract.m_PlayerToHasEntered(owner.address) == True

    # --- Player can enter lottery
    wait_for_tx_confs(contract.enter({"from": player, "value": entrance_fee}).txid)
    # --- Player has entered lottery
    assert contract.m_PlayerToHasEntered(player.address) == True


def test_cannot_enter_lottery_twice():
    only_local()

    # Init
    owner = get_account()
    contract = deploy_lottery(account=owner)
    entrance_fee = contract.getEntranceFee()

    # Core
    wait_for_tx_confs(contract.startLottery({"from": owner}).txid)
    # --- Assert lottery is opened
    assert contract.m_LotteryState() == LotteryState.OPENED.value
    # --- Enter once
    wait_for_tx_confs(contract.enter({"from": owner, "value": entrance_fee}).txid)
    # --- Try entering twice : Should fail.
    with pytest.raises(exceptions.VirtualMachineError):
        wait_for_tx_confs(contract.enter({"from": owner, "value": entrance_fee}).txid)
