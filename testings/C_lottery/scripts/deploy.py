from brownie import config, network
from brownie import Lottery
from brownie.network.account import Account
from brownie.network.contract import Contract, ContractContainer

from scripts.useful.tools import get_account, get_contract, wait_for_tx_confs


def deploy_lottery(account: Account = None, entrance_fee: int = 50, lottery_type: ContractContainer = Lottery) -> Contract:
    current_network = network.show_active()
    current_network_config = config["networks"][current_network]

    if account == None:
        account = get_account()

    contract = lottery_type.deploy(
        entrance_fee,
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        current_network_config["link_fee"],
        current_network_config["keyhash"],
        {"from": account},
        publish_source=config["networks"][current_network].get("verify", False),
    )
    wait_for_tx_confs(contract.tx.txid)

    print(f"Lottery contract deployed to {contract.address}")
    return contract


def main():
    deploy_lottery()
