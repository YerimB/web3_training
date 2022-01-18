import pytest

from brownie import exceptions
from brownie.network.transaction import TransactionReceipt

from scripts.deploy import deploy_lottery
from scripts.useful.tools import get_account, wait_for_tx_confs
from tests.tools import only_local, LotteryState


def test_owner_can_start_lottery():
    only_local()

    # Init
    owner = get_account(0)
    contract = deploy_lottery(account=owner)

    # Core / Assert
    # --- Check lottery is closed
    assert contract.m_LotteryState() == LotteryState.CLOSED.value
    # Open lottery
    tx = TransactionReceipt(contract.startLottery({"from": owner}).txid)
    if tx.confirmations == 0:
        tx.wait(1)
    # --- Check lottery is opened
    assert contract.m_LotteryState() == LotteryState.OPENED.value


def test_unknown_cannot_start_lottery():
    only_local()

    # Init
    owner = get_account(0)
    bad_actor = get_account(1)
    contract = deploy_lottery(account=owner)

    # Core / Assert
    # --- Check lottery is closed
    assert contract.m_LotteryState() == LotteryState.CLOSED.value
    # Expecting failure
    with pytest.raises(exceptions.VirtualMachineError):
        wait_for_tx_confs(contract.startLottery({"from": bad_actor}).txid)
    # --- Check lottery is still closed
    assert contract.m_LotteryState() == LotteryState.CLOSED.value


def test_cannot_start_lottery_in_progress():
    only_local()

    # Init
    owner = get_account()
    contract = deploy_lottery(account=owner)

    # Core
    # --- Start lottery once
    wait_for_tx_confs(contract.startLottery({"from": owner}).txid)
    # --- Start lottery twice : Should fail.
    with pytest.raises(exceptions.VirtualMachineError):
        wait_for_tx_confs(contract.startLottery({"from": owner}).txid)
