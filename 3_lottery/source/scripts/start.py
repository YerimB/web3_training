from brownie import Lottery
from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts.useful.tools import get_account, wait_for_tx_confs


def start_lottery(lottery: Contract, account: Account = None):
    if account == None:
        account = get_account()
    wait_for_tx_confs(lottery.startLottery({"from": account}).txid)
    print(f"Lottery at address {lottery.address} has started.")


def main():
    start_lottery()
