import pytest

from brownie import network
from scripts.helpful.tools import LOCAL_BLOCKCHAIN_ENVIRONMENTS

def only_local():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()