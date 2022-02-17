from brownie import AdvancedCollectible, config, network
from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts.helpful import tools


def deploy_collectible(account: Account, name: str, symbol: str) -> Contract:
    fURI = "https://ipfs.io/ipfs/{}"
    current_network_config = config["networks"][network.show_active()]
    collectible: Contract = AdvancedCollectible.deploy(
        name,
        symbol,
        tools.get_contract("vrf_coordinator"),
        tools.get_contract("link_token"),
        current_network_config["link_fee"],
        current_network_config["keyhash"],
        [
            fURI.format("QmYjNhogVukEobwJDYg9PiGeX9cANmXudVdhvZJTLApR9Y?filename=frolian.json"),
            fURI.format("QmXHH6mtYSVBjQ5gCTrMuh5XBL5M74gLTiGYUT39Dz7rwo?filename=mr_patate_marchais.json"),
            fURI.format("QmWbNnhSAhtKcGRjeRKJgt2pEJySjgZVmrQe65x73TXZu3?filename=alde_defense.json"),
        ],
        {"from": account},
        # publish_source=current_network_config.get("verify", False)
    )
    tools.wait_for_tx_confs(collectible.tx.txid)
    print("Deployed successfully.")
    return collectible


def main():
    account = tools.get_account()

    deploy_collectible(account, "Yamo RNG NFT", "YMOr")
