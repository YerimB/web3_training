from brownie.network.contract import Contract
from brownie.network.account import Account

from classes.event_subscriber import EventSubscriber
from scripts.advanced_collectible.deploy_collectible import deploy_collectible
from scripts.helpful.tools import (
    get_account,
    wait_for_tx_confs,
    fund_with_link,
    OPENSEA_URL,
)


def create_collectible(collectible: Contract, account: Account):
    """Generates collectible from the given AdvancedCollectible contract.
    Collectible ownership is then transfered to the transaction sender

    Args:
        collectible (Contract): Collectible contract
        account (Account): Account used to mint the collectible

    Returns:
        int: ID of the generated token
        OrderedDict: Transfer event changing ownership of the collectible to 'account'
    """
    print("Setting callbacks...")
    cb1_triggered = False
    cb2_triggered = False
    token_id = None

    def _cb1(_, event_data):
        nonlocal cb1_triggered
        print("Collectible creation requested.")
        cb1_triggered = True

    def _cb2(_, event_data):
        nonlocal cb2_triggered, account, token_id

        token_id = event_data["args"].get("tokenId")

        print("Collectible minted !")
        print(f"--- See it at {OPENSEA_URL.format(account.address, token_id)}")
        cb2_triggered = True

    colRequested_sub = EventSubscriber(
        collectible, event_name="collectibleRequested", callback=_cb1
    ).enable(delay=0.5)
    colMinted_sub = EventSubscriber(
        collectible, event_name="collectibleMinted", callback=_cb2
    ).enable(delay=0.5)
    print("Callbacks set. Creating collectible...")
    wait_for_tx_confs(collectible.createCollectible({"from": account}).txid)

    if cb1_triggered == False:
        colRequested_sub.wait(1, timeout=10)
    if cb2_triggered == False:
        colMinted_sub.wait(1, timeout=600)

    return token_id


def main():
    account = get_account()
    contract = deploy_collectible(account, "Yamo RNG NFT", "YMOr")
    fund_with_link(contract.address, account, wait_tx=True)
    create_collectible(contract, account)
