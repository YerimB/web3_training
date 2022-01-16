from brownie import Lottery
from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts.deploy import deploy_lottery
from scripts.useful.tools import get_account, wait_for_tx_confs


def start_lottery(lottery: Contract, account: Account = None, **kwargs):
    if account == None:
        account = get_account()

    if kwargs.get("lottery_timeout") == None:
        tx = wait_for_tx_confs(lottery.startLottery({"from": account}).txid)
    else:
        tx = wait_for_tx_confs(
            lottery.startLottery(kwargs.get("lottery_timeout"), {"from": account}).txid
        )

    print(f"Lottery at address {lottery.address} has started.")
    return tx


# def start_timed_lottery(
#     lottery: Contract, account: Account = None, end_after: int = 120
# ):
#     if account == None:
#         account = get_account()
#     wait_for_tx_confs(lottery.startLottery(end_after, {"from": account}).txid)
#     print(f"Lottery at address {lottery.address} has started.")


def main():
    account = get_account()
    contract = deploy_lottery(account)
    start_lottery(contract, account)
