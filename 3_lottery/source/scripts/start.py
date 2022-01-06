from brownie import Lottery
from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts.useful.tools import get_account


def start_lottery(lottery: Contract, account: Account = get_account()):
    tx = lottery.startLottery({"from": account})
    if tx.confirmations == 0:
        tx.wait(1)
    print(f"Lottery at address {lottery.address} has started.")


def main():
    start_lottery()
