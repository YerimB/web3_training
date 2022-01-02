#!./../brownie_venv/bin/python3

from ..useful.common import get_account

from brownie import FundMe
from brownie.network.account import Account


def deploy_fund_me(from_account: Account = None):
    if from_account == None:
        from_account = get_account()
    contract = FundMe.deploy({"from": from_account})
    if contract.tx.confirmations == 0:
        contract.tx.wait(1)
    print(f"Contract deployed to {contract.address}")


def main():
    deploy_fund_me()
