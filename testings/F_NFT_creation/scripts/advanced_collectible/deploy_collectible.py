from brownie import AdvancedCollectible, config, network
from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts.helpful import tools


def deploy_collectible(account: Account, name: str, symbol: str) -> Contract:
    current_network_config = config["networks"][network.show_active()]
    collectible = AdvancedCollectible.deploy(
        name,
        symbol,
        tools.get_contract("vrf_coordinator"),
        tools.get_contract("link_token"),
        current_network_config["link_fee"],
        current_network_config["keyhash"],
        {"from": account},
        # publish_source=current_network_config.get("verify", False)
    )
    tools.wait_for_tx_confs(collectible.tx.txid)
    print("Deployed successfully.")
    return collectible


def main():
    account = tools.get_account()

    deploy_collectible(account, "Yamo RNG NFT", "YMOr")
