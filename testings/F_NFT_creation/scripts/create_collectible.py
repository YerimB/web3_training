from brownie.network.contract import Contract
from brownie.network.account import Account
from brownie.network.transaction import TransactionReceipt

from scripts.deploy_collectible import deploy_collectible
from scripts.helpful.tools import get_account, wait_for_tx_confs

SAMPLE_TOKEN_URI = "https://ipfs.io/ipfs/QmYjNhogVukEobwJDYg9PiGeX9cANmXudVdhvZJTLApR9Y?filename=frolian.json"
# SAMPLE_TOKEN_URI = "https://ipfs.io/ipfs/QmXHH6mtYSVBjQ5gCTrMuh5XBL5M74gLTiGYUT39Dz7rwo?filename=mr_patate_marchais.json"
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"


def create_collectible(simple_collectible: Contract, account: Account):
    """Generates collectible from the given simple collectible contract.
    Collectible ownership is then transfered to the transaction sender

    Args:
        simple_collectible (Contract): Collectible contract
        account (Account): Account used to mint the collectible

    Returns:
        int: ID of the generated token
        OrderedDict: Transfer event changing ownership of the collectible to 'account'
    """
    print("Creating NTF...")
    tx = simple_collectible.createCollectible(SAMPLE_TOKEN_URI, {"from": account})
    tx = wait_for_tx_confs(tx.txid)
    transfer_event = tx.events['Transfer'][-1]
    token_id = transfer_event['tokenId']
    print(f"NFT created ! Viewable at {OPENSEA_URL.format(simple_collectible.address, token_id)}")

    return token_id, transfer_event


def main():
    account = get_account()
    simple_collictible = deploy_collectible(account)
    create_collectible(simple_collictible, account)
