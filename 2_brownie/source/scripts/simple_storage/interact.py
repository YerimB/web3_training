#!./../brownie_venv/bin/python3

from brownie import SimpleStorage, accounts, config
from brownie.network.account import Account
from .deploy import get_account


def read_contract(instance=SimpleStorage[-1]):
    return instance.retrieve()


def set_value(
    value: int,
    instance=SimpleStorage[-1],
    account: Account = get_account(),
    validation: int = 0,
):
    tx = instance.store(value, {"from": account})
    if validation > 0:
        tx.wait(1)


def main():
    print(read_contract())
    set_value(44, validation=1)
    print(read_contract())
