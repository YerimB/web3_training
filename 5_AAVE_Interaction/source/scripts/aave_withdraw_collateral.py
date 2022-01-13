from web3 import Web3

from brownie import network, config, interface
from brownie.network.account import Account
from scripts import aave_deposit_weth

from scripts.helpful.tools import (
    get_account,
    get_borrowable_data,
    wait_for_tx_confs,
    get_lending_pool,
)


def withdraw_collateral_weth(account: Account):
    # Get weth token contract instance.
    weth_token = interface.IWeth(
        config["networks"][network.show_active()]["weth_token"]
    )
    # Get aave lending pool contract.
    lending_pool = get_lending_pool()

    # Get the total amount to withdraw.
    amount_to_withdraw = Web3.toWei(
        get_borrowable_data(lending_pool, account)[2], "ether"
    )

    # Withdraw from lending pool.
    print("Withdrawing...")
    tx = lending_pool.withdraw(
        weth_token.address, amount_to_withdraw, account.address, {"from": account}
    )
    wait_for_tx_confs(tx.txid)
    print("Withdrawn successfully !")
    get_borrowable_data(lending_pool, account)


def main():
    account = get_account()

    # Deposit some ether to aave before withdrawing.
    # If there is nothing to withdraw, the call to the lending pool smart contract reverts
    amount_to_deposit = Web3.toWei(0.1, "ether")
    aave_deposit_weth.deposit(account, amount_to_deposit)
    # Deposit script
    withdraw_collateral_weth(account)
