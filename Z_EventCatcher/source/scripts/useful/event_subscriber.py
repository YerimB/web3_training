# Typing
from typing import Callable

from web3._utils import datatypes as w3_datatypes
from brownie import web3 as w3
from brownie.network import alert

# Web3 & Brownie types
# --- Web3
from web3.datastructures import AttributeDict
from web3.contract import Contract as w3_Contract

# --- Brownie
from brownie.network.contract import Contract, ProjectContract


def _brownie_contract_to_web3_contract(brownie_contract: Contract) -> w3_Contract:
    w3_contract = w3.eth.contract(
        address=brownie_contract.address, abi=brownie_contract.abi
    )
    return w3_contract


def _get_latests_events(event, **kwargs):
    """Returns a generator, which, when called, returns a list containing all
    events that occured between the last checked block (or the start block on
    the first call) and the last mined block.

    Args:
        event ([type]): [description]

    Yields:
        events: List containing all events since last call.
    """
    start_block = kwargs.get("start_block", w3.eth.block_number - 100)
    to_block = w3.eth.block_number

    while True:
        event_filter = event.createFilter(fromBlock=start_block, toBlock=to_block)
        events = event_filter.get_all_entries()
        yield events

        # Shifts the blocks to look at.
        start_block = to_block
        to_block = w3.eth.block_number


def _get_next_event(event_to_watch, **kwargs):
    # Get event catcher generator
    _gen_latests_events = _get_latests_events(event_to_watch, **kwargs)
    while True:
        # Get latests events since last block checked
        events_list = next(_gen_latests_events)
        # If no event detected return None
        if events_list.__len__() == 0:
            yield None
        # Submit latest events one by one.
        for event in events_list:
            yield event


class EventSubscriber:
    # Member variables
    _brownie_contract = None  # brownie.network.contract.Contract
    _w3_contract = None  # web3.contract.Contract
    _alert = None  # brownie.network.alert.Alert
    _event_name = None  # str
    _callback = None  # typing.Callable
    _gen_event_getter = None  # generator
    _from_block = 0  # int

    def __init__(
        self, contract: Contract, event_name: str, callback: Callable, **kwargs
    ):
        """Initializes instance of the EventSubscriber class.

        Args:
            contract (Contract): Contract from which to get the event.
            event_name (str): Event name in the solidity file
            callback (Callable): Function called on event received. It must take 2 parameters.
            The first one is useless, and the second one is a 'web3.datastructures.AttributeDict'
            object containing the event data.

        **kwargs:
            from_block (int > 0): Block from which to start catching events.
            auto_enable (bool): If False, does not enable the callback after instantiation,
            otherwise, calls the 'enable' function with the default parameters

        Raises:
            TypeError: Raised when the 'contract' argument is not of
            type brownie.network.contract.Contract or of type brownie.network.contract.ProjectContract
        """
        if type(contract) not in [Contract, ProjectContract]:
            raise TypeError(
                "Given argument \'contract\' invalid type."
            )
        self._brownie_contract = contract
        self._w3_contract = _brownie_contract_to_web3_contract(self._brownie_contract)
        self._event_name = event_name
        self._callback = callback
        self._from_block = kwargs.get("from_block", w3.eth.block_number)
        if kwargs.get("auto_enable", True):
            self.enable()

    def enable(self, delay: int = 2, repeat: bool = False):
        """Enables the established callback on the established event.

        Args:
            delay (int, optional): @dev see : https://eth-brownie.readthedocs.io/en/stable/api-network.html#brownie.network.alert.Alert. Defaults to 2.
            repeat (bool, optional): @dev see : https://eth-brownie.readthedocs.io/en/stable/api-network.html#brownie.network.alert.Alert. Defaults to False.
        """
        self.__setup_event_callback(delay, repeat)

    def disable(self, wait: bool = True):
        """Disables the established callback on the established event.

        Args:
            wait (bool, optional): @dev see : https://eth-brownie.readthedocs.io/en/stable/api-network.html#Alert.stop. Defaults to True.
        """
        if self._alert == None or self._alert.is_alive() == False:
            print("Warning : Alert not enabled.")
            return
        self._alert.stop(wait)

    # PRIVATE METHODS #

    def __setup_event_callback(self, _delay: int, _repeat: bool):
        # Get event (PropertyCheckingFactory) from event name
        self.event_watched = self.__get_w3_event_from_name(
            self._event_name
        )
        # Get event generator
        self._gen_event_getter = _get_next_event(
            self.event_watched, from_block=self._from_block
        )
        # Sets a new alert to self._alert and runs it
        self._alert = alert.new(
            next,
            args=(self._gen_event_getter,),
            delay=_delay,
            callback=self._callback,
            repeat=_repeat,
        )

    def __get_w3_event_from_name(self, event_name: str):
        # Get event with name matching 'event_name' parameter
        property_checking_factory = self._w3_contract.events.__dict__.get(
            event_name, None
        )
        # Check if event was found
        if property_checking_factory == None:
            raise Exception(f"Could not retrieve event with name : {event_name}")
        # Returns the event
        return property_checking_factory

    # PROPERTIES #

    def _get_prop_check_fact(self):
        return self._property_checking_factory

    def _set_prop_check_fact(self, value):
        if type(value) not in [w3_datatypes.PropertyCheckingFactory, type(None)]:
            raise ValueError("_property_checking_factory setter : invalid value type.")
        self._property_checking_factory = value

    event_watched = property(fget=_get_prop_check_fact, fset=_set_prop_check_fact)  # <-> Event
