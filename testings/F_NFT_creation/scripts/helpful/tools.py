from web3 import Web3

from brownie import network, accounts
from brownie.network.transaction import TransactionReceipt

FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local-1"]


def wait_for_tx_confs(txid: str, conf_nb: int = 1):
    tx_receipt = TransactionReceipt(txid)
    if tx_receipt.confirmations == conf_nb:
        tx_receipt.wait(conf_nb)
    return tx_receipt


def get_account(index: int | None = None, id: str | None = None):
    active_network = network.show_active()

    if index:
        return accounts[index]
    elif id:
        return accounts.load(id)
    if (
        active_network in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or active_network in FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS
    ):
        return accounts[0]
    # else
    return accounts.load("dev_mask_1")
