#!./../brownie_venv/bin/python3

from web3 import Web3
from scripts.useful.common import get_account

from brownie import FundMe


def fund(fund_me=FundMe[-1], account=get_account()):
    print(f"Funding from {account.address}...")
    fund_tx = fund_me.fund({"from": account, "value": Web3.toWei(0.5, "ether")})
    if fund_tx.confirmations == 0:
        fund_tx.wait(1)
    print("Funded !")


def withdraw(fund_me=FundMe[-1], account=get_account()):
    _, _, amount_funded = fund_me.m_AddressToFunderData(account.address)
    print(f"Deposited balance : {amount_funded / 10**18} $ETH")
    print("Withdrawing...")
    fund_me.withdrawWei(amount_funded, {"from": account})
    print("Successfully withdrawed !")


def main():
    fund()
    withdraw()
