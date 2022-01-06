import pytest

from brownie import network, exceptions, accounts
from web3 import Web3

from scripts.deploy import deploy_lottery
from scripts.useful.tools import get_account
from scripts.useful.tools import LOCAL_BLOCKCHAIN_ENVIRONMENTS

def check_local():
    # Skip test if not on local environment.
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Not on local environment.")


def test_get_entrance_fee():
    check_local()

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


def test_enter_lottery():
    # Init
    lottery_owner = get_account(0)
    contract = deploy_lottery(lottery_owner)
    player1 = get_account(1)
    player2 = get_account(2)
    lottery_entrance_fee = contract.getEntranceFee()

    # Core
    # --- Confirm no one has entered the lottery.
    # assert contract.

    contract.enter({'from': player1, 'value': lottery_entrance_fee})
    contract.enter({'from': player2, 'value': lottery_entrance_fee})
