#!./../brownie_venv/bin/python3

from web3 import Web3
from ..useful.common import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS

from brownie import FundMe, MockV3Aggregator, network, config
from brownie.network.account import Account

DECIMALS = 8
STARTING_PRICE = 2000e8


def get_AggregatorV3_address(current_network=None, **kwargs) -> str:
    """Gets the ETH / USD ratio feed address depending on which network we are on.

    Args:
        current_network (str, optional): name of the current network. Defaults to network.show_active().
    """

    if current_network == None:
        current_network = network.show_active()
    # If on a persistent network like Rinkeby, uses associated address,
    # Otherwise, deploys mocks.
    if current_network not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return config["networks"][current_network]["eth_usd_price_feed"]
    else:
        print(f"The active network is {current_network}.")
        print("Deploying & Getting Mocks...")
        # MockV3Aggregator
        if len(MockV3Aggregator) == 0:
            print(" --- MockV3Aggregator in progress...")
            # Gets the active account in order to deploy the mock
            from_account = kwargs.get("from_account")
            if from_account == None:
                from_account = get_account()
            # Deploys the mocks
            MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": from_account})
        print("Mocks Deployed !")
        return MockV3Aggregator[-1].address


def deploy_fund_me(from_account: Account = None):
    # Gets the active network
    active_network = network.show_active()

    if from_account == None:
        from_account = get_account()
    eth_usd_feed_address = get_AggregatorV3_address()

    # Deploys the FundMe Contract
    contract = FundMe.deploy(
        eth_usd_feed_address,
        {"from": from_account},
        publish_source=config["networks"][active_network].get("verify"),
    )
    if contract.tx.confirmations == 0:
        contract.tx.wait(1)
    print(f"FundMe contract deployed to {contract.address}")
    return contract


def main():
    deploy_fund_me()
