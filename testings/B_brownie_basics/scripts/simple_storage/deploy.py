#!./../brownie_venv/bin/python3

from ..useful.common import get_account

from brownie import SimpleStorage
from brownie.network.account import Account


def deploy_simple_storage(from_account: Account = None):
    if from_account == None:
        from_account = get_account()
    contract = SimpleStorage.deploy({"from": from_account})
    if contract.tx.confirmations == 0:
        contract.tx.wait(1)
    print(f"Contract deployed to {contract.address}")


def main():
    deploy_simple_storage()
