from brownie import SimpleCollectible
from brownie.network.account import Account
from brownie.network.contract import Contract

from scripts.helpful import tools


def deploy_collectible(account: Account, name: str, symbol: str) -> Contract:
    simple_collectible = SimpleCollectible.deploy(name, symbol, {"from": account})
    tools.wait_for_tx_confs(simple_collectible.tx.txid)
    return simple_collectible


def main():
    account = tools.get_account()

    deploy_collectible(account, "Mr. Potato", "POTA")
