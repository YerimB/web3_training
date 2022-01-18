from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts.deploy import deploy_lottery
from scripts.useful.tools import get_account, wait_for_tx_confs


def start_lottery(lottery: Contract, account: Account = None, **kwargs):
    if account == None:
        account = get_account()

    if lottery._build["contractName"] == "Lottery":
        tx = wait_for_tx_confs(lottery.startLottery({"from": account}).txid)
    else:
        tx = wait_for_tx_confs(
            lottery.startLottery(
                kwargs.get("lottery_timeout", 60), {"from": account}
            ).txid
        )

    print(f"Lottery at address {lottery.address} has started.")
    return tx


def main():
    account = get_account()
    contract = deploy_lottery(account)
    start_lottery(contract, account)
