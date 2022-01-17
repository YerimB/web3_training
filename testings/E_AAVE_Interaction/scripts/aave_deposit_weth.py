from web3 import Web3

from brownie.network.account import Account

from scripts import weth
from scripts.helpful.tools import (
    get_account,
    wait_for_tx_confs,
    approve_erc20,
    get_lending_pool,
)


def deposit(account: Account, amount_to_deposit: int):
    # Get some $wETH to be able to deposit
    weth_token = weth.get_weth(account, wei_amount=amount_to_deposit)

    # Get aave lending pool contract
    lending_pool = get_lending_pool()

    # Approve wETH (erc20) token before depositing
    approve_erc20(
        spender_address=lending_pool.address,
        amount=amount_to_deposit,
        erc20_address=weth_token.address,
        account=account,
    )

    # Deposit to lending pool
    print("Depositing...")
    tx = lending_pool.deposit(
        weth_token.address, amount_to_deposit, account.address, 0, {"from": account}
    )
    wait_for_tx_confs(tx.txid)
    print("Deposit successful !")


def main():
    account = get_account()
    amount_to_deposit = Web3.toWei(0.1, "ether")

    # Deposit script
    deposit(account, amount_to_deposit)
