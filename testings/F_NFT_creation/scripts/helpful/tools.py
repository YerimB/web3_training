from brownie import network, accounts, config
from brownie import LinkToken, VRFCoordinatorMock

from brownie.network.transaction import TransactionReceipt
from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts.helpful.mocks import deploy_mock


FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local-1"]
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"


def wait_for_tx_confs(txid: str, conf_nb: int = 1):
    tx_receipt = TransactionReceipt(txid)
    if tx_receipt.confirmations == conf_nb:
        tx_receipt.wait(conf_nb)
    return tx_receipt


def get_account(index: int | None = None, id: str | None = None):
    active_network = network.show_active()

    if index:
        return accounts[index]
    elif id:
        return accounts.load(id)
    if (
        active_network in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or active_network in FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS
    ):
        return accounts[0]
    # else
    return accounts.add(config["accounts"]["from_key"])


CONTRACT_TO_MOCK = {
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, and
    return that mock contract.
        Args:
            contract_name (string)
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    active_network = network.show_active()
    contract_type = CONTRACT_TO_MOCK[contract_name]

    if active_network in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()  # Deploys needed mocks when one missing.
        # Gets the latest contract of type : contract_type
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][active_network][contract_name]
        # Gets the contract from its name, address and ABI
        # Not using interfaces : since the contract type is not readable by humans,
        # we may not have the matching interface.
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    # Returns the mock or the contract instance.
    return contract


def deploy_mocks(account: Account = None):
    if account == None:
        account = get_account()

    for mock_name, mock_type in CONTRACT_TO_MOCK.items():
        if len(mock_type) == 0:
            deploy_mock(mock_name, account)
            print(f" --- Mock '{mock_type._name}' : deployed !")
    print("All missing mocks were deployed !")


def fund_with_link(
    contract_address,
    from_account: Account = None,
    link_token: Contract = None,
    amount: int = 1e17,  # 0.1 LINK
    wait_tx: bool = False,
    **kwargs,
):
    # Get account
    if from_account == None:
        from_account = get_account()
    # Get LINK token contract
    if link_token == None:
        link_token = get_contract("link_token")

    # Fund
    balance = link_token.balanceOf(from_account)
    print(f"Balance : {balance}")
    tx = link_token.transfer(contract_address, amount, {"from": from_account})
    if wait_tx == True and tx.confirmations == 0:
        print(
            f"Funding contract at address {contract_address} with {amount * 1e-18} $LINK...",
            end="",
            flush=True,
        )
        tx.wait(kwargs.get("confirmations", 1))  # Wait for n confimations
        print("Success !")
    return tx
