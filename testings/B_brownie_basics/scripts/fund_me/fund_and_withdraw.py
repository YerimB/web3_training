#!./../brownie_venv/bin/python3

from scripts.useful.common import get_account

from brownie import FundMe


def fund(amount: int, contract=FundMe[-1], account=get_account()):
    print(f"Funding from {account.address}...")
    # Funding...
    tx = contract.fund({"from": account, "value": amount})
    if tx.confirmations == 0:
        tx.wait(1)
    print("Funded !")


def withdraw(amount: int = 0, contract=FundMe[-1], account=get_account()):
    (_, amount_funded, _) = contract.m_AddressToFunderData(account.address)
    print(f"Deposited balance : {amount_funded / 1e18} $ETH")

    def get_amount_to_withdraw(amount):
        if amount == 0:
            print("Withdrawing entire balance...")
            return amount_funded
        print(f"Withdrawing {amount / 1e18} $ETH...")
        return amount

    # Getting amount to withdraw
    amount = get_amount_to_withdraw(amount)

    # Withdrawing...
    tx = contract.withdrawWei(amount, {"from": account})
    if tx.confirmations == 0:
        tx.wait(1)
    print("Successfully withdrawed !")


def main():
    fund_me = FundMe[-1]
    amount = fund_me._getEntranceFee()
    print(f"Amount : {amount}")

    fund(amount, contract=fund_me)
    withdraw(contract=fund_me)
