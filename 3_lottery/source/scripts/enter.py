from brownie import Lottery
from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts.useful.tools import get_account


def enter_lottery(lottery: Contract, account: Account = get_account(), **kwargs):
    # Get entrance fee from contract if not precised in kwargs
    entrance_fee = kwargs.get("entrance_fee", lottery.getEntranceFee())

    # Enter the lottery
    tx = lottery.enter({"from": account, "value": entrance_fee})
    if tx.confirmations == 0:
        tx.wait(1)
    print(f"Address {account.address} has entered the lottery !")


def main():
    enter_lottery()
