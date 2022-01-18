import time
from typing import Callable


# Web3 & Brownie types
from web3.datastructures import AttributeDict
from brownie import EventEmitter
from brownie.network.contract import Contract

# My scripts
from classes.event_subscriber import EventSubscriber

from scripts.useful.tools import wait_for_tx_confs
from scripts.deploy import deploy_event_emitter
from scripts.useful.tools import get_account


def _event_callback(_: AttributeDict, _event: AttributeDict):
    if _event == None:
        return
    print("Event caught !")
    print(f"Arguments : {_event['args']}")


def subscribe_to_event(contract: Contract, event_name: str, callback: Callable) -> EventSubscriber:
    event_sub = EventSubscriber(contract, event_name=event_name, callback=callback)
    event_sub.enable(delay=1, repeat=True)
    return event_sub


def main():
    account = get_account()

    # Get contract
    contract = None
    if EventEmitter.__len__() == 0:
        contract = deploy_event_emitter(account)
    else:
        contract = EventEmitter[-1]
    print(f"Using contract at : {contract.address}")

    subscription = subscribe_to_event(contract, event_name="CallEvent", callback=_event_callback)

    for _ in range(5):
        tx = contract.triggerEvent({"from": account})
        wait_for_tx_confs(tx.txid)
        time.sleep(3)
    subscription.disable()
