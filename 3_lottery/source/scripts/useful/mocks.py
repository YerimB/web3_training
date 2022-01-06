from brownie import MockV3Aggregator, VRFCoordinatorMock, LinkToken

# USD / ETH price feed
DECIMALS = 8
STARTING_PRICE = 2000e8


def deploy_MockV3Aggregator(from_account):
    return MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": from_account})


def deploy_LinkToken(from_account):
    if len(LinkToken) == 0:
        LinkToken.deploy({"from": from_account})
    return LinkToken[-1]


def deploy_VRFCoordinatorMock(from_account):
    # Get Link token address
    link_token_address = deploy_LinkToken(from_account).address
    # Deploy VRFCoordinatorMock
    return VRFCoordinatorMock.deploy(link_token_address, {"from": from_account})


CONTRACT_NAME_TO_DEPLOYMENT_FUNC = {
    "eth_usd_price_feed": deploy_MockV3Aggregator,
    "vrf_coordinator": deploy_VRFCoordinatorMock,
    "link_token": deploy_LinkToken,
}


def deploy_mock(mock_name, account):
    CONTRACT_NAME_TO_DEPLOYMENT_FUNC[mock_name](from_account=account)
