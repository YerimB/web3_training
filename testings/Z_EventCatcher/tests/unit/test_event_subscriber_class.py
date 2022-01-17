import pytest

from brownie import network

from classes.event_subscriber import EventSubscriber

from scripts.deploy import deploy_event_emitter
from scripts.useful.tools import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account


def only_local(msg: str = ""):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip(msg)


def test_create_event_subscription():
    only_local()

    # Init
    account = get_account()
    contract = deploy_event_emitter(account)
    callback_was_triggered = False
    parameters_match = False

    # --- Define callback function.
    def event_callback(_, event_data):
        # Gets variable from parent function
        nonlocal callback_was_triggered, parameters_match, account

        callback_was_triggered = True
        parameters_match = event_data["args"]["sender"] == account.address

    # Core
    subscriber = EventSubscriber(
        contract, event_name="CallEvent", callback=event_callback
    )
    subscriber.enable()
    tx = contract.triggerEvent({"from": account})
    if tx.confirmations == 0:
        tx.wait(1)
    # Wait for callback to be triggered
    # Similar to Thread.join()
    subscriber.wait()

    # Assert
    assert callback_was_triggered == True
    assert (
        parameters_match
    ), "Assertion error in thread : parameters don't match the expected ones"
