from web3 import Web3
from brownie import network, config, interface

from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts.helpful import convert
from scripts.helpful.tools import (
    approve_erc20,
    get_account,
    wait_for_tx_confs,
    get_lending_pool,
    get_borrowable_data,
)


def get_max_repayable_dai_amount(lending_pool, account, **kwargs):
    dai_token = kwargs.get(
        "dai_token",
        interface.IERC20(config["networks"][network.show_active()]["dai_token"]),
    )
    dai_balance = dai_token.balanceOf(account.address)
    dai_borrowed_amount = Web3.toWei(
        convert.eth_to_dai(get_borrowable_data(lending_pool, account)[1]), "ether"
    )
    print(f"Current DAI balance : {Web3.fromWei(dai_balance, 'ether')}")
    print(f"Current DAI dept : {Web3.fromWei(dai_borrowed_amount, 'ether')}")
    return min(dai_balance, dai_borrowed_amount)


def repay_dai_dept(lending_pool: Contract, account: Account):
    dai_token = interface.IERC20(config["networks"][network.show_active()]["dai_token"])
    amount_to_repay = get_max_repayable_dai_amount(
        lending_pool, account, dai_token=dai_token
    )

    # Approve spending
    approve_erc20(
        spender_address=lending_pool.address,
        amount=amount_to_repay,
        erc20_address=dai_token.address,
        account=account,
    )

    # Repay contract call
    print(f"Repaying {amount_to_repay}...")
    repay_tx = lending_pool.repay(
        dai_token.address,
        amount_to_repay,
        2,  # Interest mode : variable
        account.address,
        {"from": account},
    )
    wait_for_tx_confs(repay_tx.txid)
    print("Dept repaid !")
    # Check aave data
    get_borrowable_data(lending_pool, account)


def main():
    account = get_account()
    lending_pool = get_lending_pool()

    repay_dai_dept(lending_pool, account)
