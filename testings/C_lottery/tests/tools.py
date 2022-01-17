import pytest
from enum import Enum

from brownie import network

from scripts.useful.tools import LOCAL_BLOCKCHAIN_ENVIRONMENTS


class LotteryState(Enum):
    CLOSED = 0
    OPENED = 1
    CALCULATING_WINNER = 2


def only_local():
    # Skip test if not on local environment.
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only executed on local environment.")


def skip_local():
    # Skip test if not on local environment.
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Not executed on local environment.")
