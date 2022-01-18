import time
import pytest

from brownie import network

from classes.event_subscriber import EventSubscriber

from scripts.deploy import deploy_event_emitter
from scripts.useful.tools import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account


def only_local(msg: str = ""):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip(msg)


def test_disable_subscription():
    only_local()

    # Init
    account = get_account()
    contract = deploy_event_emitter(account)

    # --- Define callback function.
    def event_callback(_, event_data):
        pass

    # Core
    subscriber = EventSubscriber(
        contract, event_name="CallEvent", callback=event_callback
    ).enable()

    # Assert
    assert subscriber.is_alive() == True
    subscriber.disable()
    assert subscriber.is_alive() == False


def test_subscription_disables_if_not_repeated_when_event_fires():
    only_local()

    # Init
    account = get_account()
    contract = deploy_event_emitter(account)
    callback_was_triggered = False

    # --- Define callback function.
    def event_callback(_, event_data):
        nonlocal callback_was_triggered
        callback_was_triggered = True

    # Core
    subscriber = EventSubscriber(
        contract, event_name="CallEvent", callback=event_callback
    ).enable()
    # --- Trigger event to catch and wait for confirmation
    tx = contract.triggerEvent({"from": account})
    if tx.confirmations == 0:
        tx.wait(1)
    # Wait for trigger if needed
    if callback_was_triggered == False:
        subscriber.wait()

    # Assert
    assert callback_was_triggered == True
    assert subscriber.is_alive() == False


def test_subscription_still_enabled_if_repeated_when_event_fires():
    only_local()

    # Init
    account = get_account()
    contract = deploy_event_emitter(account)
    callback_was_triggered = False

    # --- Define callback function.
    def event_callback(_, event_data):
        nonlocal callback_was_triggered
        callback_was_triggered = True

    # Core
    subscriber = EventSubscriber(
        contract, event_name="CallEvent", callback=event_callback
    ).enable(repeat=True)
    # --- Trigger event to catch and wait for confirmation
    tx = contract.triggerEvent({"from": account})
    if tx.confirmations == 0:
        tx.wait(1)
    # Wait for trigger if needed
    if callback_was_triggered == False:
        subscriber.wait(timeout=10)

    # Assert
    assert callback_was_triggered == True
    assert subscriber.is_alive() == True
    subscriber.disable(wait=False)


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
        parameters_match = bool(event_data["args"]["sender"] == account.address)

    # Core
    subscriber = EventSubscriber(
        contract, event_name="CallEvent", callback=event_callback
    ).enable()
    # --- Trigger event to catch and wait for confirmation
    tx = contract.triggerEvent({"from": account})
    if tx.confirmations == 0:
        tx.wait(1)
    # --- Wait for callback to be triggered
    # --- Similar to Thread.join()
    subscriber.wait()

    # Assert
    assert callback_was_triggered == True
    assert (
        parameters_match
    ), "Assertion error in thread : parameters don't match the expected ones"


def test_create_repeated_event_subscription():
    only_local()

    # Init
    account = get_account()
    contract = deploy_event_emitter(account)

    alert_delay = 3 # Seconds
    times_repeated = 3
    times_callback_was_triggered = 0
    parameters_match_count = 0

    # --- Define callback function.
    def event_callback(_, event_data):
        # Gets variable from parent function
        nonlocal times_callback_was_triggered, parameters_match_count, account

        times_callback_was_triggered += 1
        if event_data["args"]["sender"] == account.address:
            parameters_match_count += 1

    # Core
    subscriber = EventSubscriber(
        contract, event_name="CallEvent", callback=event_callback
    ).enable(delay=alert_delay, repeat=True)
    # --- Trigger event to catch and wait for confirmation
    for _ in range(times_repeated):
        # Should trigger the event each time the transaction is confirmed for the first time
        tx = contract.triggerEvent({"from": account})
        if tx.confirmations == 0:
            tx.wait(1)
    # Wait for the callback to be "theoretically" triggered (since there is a delay between each check).
    time.sleep(alert_delay * times_repeated)
    subscriber.disable(wait=False)

    # Assert
    assert times_callback_was_triggered == times_repeated
    assert (
        parameters_match_count == times_repeated
    ), "Assertion error in thread : parameters don't match the expected ones"
