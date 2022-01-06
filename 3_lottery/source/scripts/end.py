import time

from brownie import Lottery, network
from brownie import config
from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts.useful.tools import get_account, fund_with_link


def end_lottery(lottery: Contract, account: Account = get_account()):
    # Grab current active network
    current_network = network.show_active()
    # Fund lottery contract with enought link to generate random
    fund_with_link(
        contract_address=lottery.address,
        from_account=account,
        amount=config["networks"][current_network]["link_fee"],
        wait_tx=True,
    )
    tx = lottery.endLottery({"from": account})
    if tx.confirmations == 0:
        tx.wait(1)
    time.sleep(60)
    print(f"Lottery at address {lottery.address} has ended.")
    print(f" --- Winner : {lottery.m_Winner()}")


def main():
    end_lottery()
