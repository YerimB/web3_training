import time

from brownie import web3
from brownie import EventEmitter

# Web3 & Brownie types
from web3.datastructures import AttributeDict
from brownie.network.alert import Alert
from brownie.network.contract import Contract

from scripts.deploy import deploy_event_emitter
from scripts.useful.tools import get_account, get_w3_event_from_name
from scripts.useful.event_subscriber import EventSubscriber


def _event_callback(_: AttributeDict, _event: AttributeDict):
    if _event == None:
        return
    print(type(_event))
    print(_event["args"])


def catch_contract_event(contract: Contract):
    print(f"Using contract at : {contract.address}")
    event_sub = EventSubscriber(contract, event_name="CallEvent", callback=_event_callback)
    print("Callback on CallEvent was set !")
    return event_sub


def main():
    account = get_account()

    # Get contract
    contract = None
    if EventEmitter.__len__() == 0:
        contract = deploy_event_emitter(account)
    else:
        contract = EventEmitter[-1]

    print(type(contract))
    # Start catching events
    catch_contract_event(contract)

    while True:
        time.sleep(120)
