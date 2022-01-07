from brownie import Lottery
from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts.useful.tools import get_account, wait_for_tx_confs


def enter_lottery(lottery: Contract, account: Account, **kwargs):
    # Get entrance fee from contract if not precised in kwargs
    entrance_fee = kwargs.get("entrance_fee", lottery.getEntranceFee())

    # Enter the lottery
    wait_for_tx_confs(
        lottery.enter({"from": account, "value": entrance_fee}).txid, conf_nb=1
    )
    print(f"Address {account.address} has entered the lottery !")


def main():
    enter_lottery()
