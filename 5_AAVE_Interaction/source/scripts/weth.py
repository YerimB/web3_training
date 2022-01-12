from web3 import Web3

from brownie import network, interface, config
from brownie.network.account import Account

from scripts.helpful.tools import get_account, wait_for_tx_confs


DEFAULT_WEI_AMOUNT = Web3.toWei(0.1, "ether")

def get_weth(account: Account, wei_amount: int = DEFAULT_WEI_AMOUNT):
    """
    Mints $WETH by depositing $ETH
    """
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": wei_amount})
    wait_for_tx_confs(tx.txid)
    return weth


def get_eth(account: Account, wei_amount: int = DEFAULT_WEI_AMOUNT):
    """
    Burns $WETH to get $ETH back
    """
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.withdraw(wei_amount, "ether", {"from": account})
    wait_for_tx_confs(tx.txid)
    return tx


def main():
    get_weth(account=get_account())
