from tests.tools import only_local

from scripts.helpful import tools
from scripts.deploy_collectible import deploy_collectible
from scripts.create_collectible import create_collectible


def test_can_create_simple_collectible():
    only_local()
    # Init
    account = tools.get_account()
    nft_contract = deploy_collectible(account, "Test name", "TST")
    og_account_collectible_balance = nft_contract.balanceOf(account.address)

    # Core
    # --- Create collectible.
    token_id, transfer_event = create_collectible(nft_contract, account)
    # --- Get the newly generated collectible owner's address.
    generated_collectible_owner_address = nft_contract.ownerOf(token_id)
    # --- Get the number of collectible account.address has.
    account_collectible_balance = nft_contract.balanceOf(account.address)

    # Assert
    assert generated_collectible_owner_address == account.address
    assert transfer_event['to'] == account.address
    assert account_collectible_balance == og_account_collectible_balance + 1
