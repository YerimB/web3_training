from brownie import network, config
from web3 import Web3

from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts import aave_deposit_weth
from scripts.aave_repay_dai_debt import repay_dai_dept
from scripts.helpful import convert
from scripts.helpful.tools import (
    get_account,
    get_borrowable_data,
    wait_for_tx_confs,
    get_lending_pool,
    get_asset_price,
)


def borrow_dai(account: Account, amount_to_deposit: int):
    # Get current network
    current_network = network.show_active()

    # Get lending pool.
    lending_pool = get_lending_pool()

    # Deposit collateral to borrow...
    aave_deposit_weth.deposit(account, amount_to_deposit)

    # Get account data on aave lending pool
    borrowable_eth, total_debt, total_collateral = get_borrowable_data(
        lending_pool, account
    )

    # Convert borrowable ether to borrowable dai to dai to borrow (75%)
    borrowable_dai = convert.eth_to_dai(borrowable_eth)
    amount_to_borrow = float(borrowable_dai) * 0.75  # 75% of the borrowable amount.
    print(
        "Borrowable DAI amount : %.3f | Amount to borrow : %.3f"
        % (borrowable_dai, amount_to_borrow)
    )

    # Borrow contract call
    print("Borrowing...")
    borrow_tx = lending_pool.borrow(
        config["networks"][current_network]["dai_token"],
        Web3.toWei(amount_to_borrow, "ether"),
        2,  # Variable interest rate mode
        0,  # referral code -> 0 if None (deprecated)
        account.address,
        {"from": account},
    )
    wait_for_tx_confs(borrow_tx.txid)
    print("Borrowed successfully !")


def main():
    account = get_account()
    amount_to_deposit = Web3.toWei(0.1, "ether")

    borrow_dai(account, amount_to_deposit)
