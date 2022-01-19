from brownie import VRFCoordinatorMock, LinkToken

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
    "vrf_coordinator": deploy_VRFCoordinatorMock,
    "link_token": deploy_LinkToken,
}


def deploy_mock(mock_name, account):
    CONTRACT_NAME_TO_DEPLOYMENT_FUNC[mock_name](from_account=account)
