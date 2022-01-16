from web3._utils import datatypes
from web3.contract import Contract as w3_Contract

from brownie import network, accounts, web3 as w3, config

from brownie.network.transaction import TransactionReceipt
from brownie.network.contract import Contract

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
    return accounts.add(config["wallets"]["from_key"])


def get_w3_event_from_name(contract: Contract, event_name: str):
    # Get web3.py contract
    w3_contract = get_w3_contract(contract)
    # Get event with name matching 'event_name' parameter
    w3_event = w3_contract.events.__dict__.get(event_name, None)
    # Check if event was found
    if (
        w3_event == None
        or type(w3_event) != datatypes.PropertyCheckingFactory
    ):
        raise Exception(f"Could not retrieve event with name : {event_name}")
    # Returns the event
    return w3_event


def get_w3_contract(brownie_contract: Contract) -> w3_Contract:
    w3_contract = w3.eth.contract(
        address=brownie_contract.address, abi=brownie_contract.abi
    )
    return w3_contract
