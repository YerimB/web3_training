#!./../brownie_venv/bin/python3

from web3 import Web3
from scripts.useful.common import get_account

from brownie import FundMe


def fund(amount: int, contract=FundMe[-1], account=get_account()):
    print(f"Funding from {account.address}...")
    # Funding...
    fund_tx = contract.fund({"from": account, "value": amount})
    if fund_tx.confirmations == 0:
        fund_tx.wait(1)
    print("Funded !")


def withdraw(amount: int = 0, contract=FundMe[-1], account=get_account()):
    (_, amount_funded, _) = contract.m_AddressToFunderData(account.address)
    print(f"Deposited balance : {amount_funded / 1e18} $ETH")

    def get_amount_to_withdraw(amount):
        if amount == 0:
            print("Withdrawing entire balance...")
            amount = amount_funded
        else:
            print(f"Withdrawing {amount / 1e18} $ETH...")

    # Getting amount to withdraw
    amount = get_amount_to_withdraw(amount)

    # Withdrawing...
    tx = contract.withdrawWei(amount, {"from": account})
    if tx.confirmations == 0:
        tx.wait(1)
    print("Successfully withdrawed !")


def main():
    amount = FundMe[-1]._getEntranceFee()
    fund(amount)
    withdraw()
