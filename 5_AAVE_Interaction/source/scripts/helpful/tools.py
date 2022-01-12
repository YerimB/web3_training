from web3 import Web3

from brownie import network, accounts, config, interface
from brownie.network.transaction import TransactionReceipt
from brownie.network.account import Account
from brownie.network.contract import Contract

FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local-1"]


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
    return accounts.load("dev_mask_1")


def approve_erc20(
    spender_address: str, amount: int, erc20_address: str, account: Account
):
    print(f"Approving ERC20 token at {erc20_address}...")
    token = interface.IERC20(erc20_address)
    tx = token.approve(spender_address, amount, {"from": account})
    wait_for_tx_confs(tx.txid)
    print("Token approved !")


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["aave_lp_address_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    return interface.ILendingPool(lending_pool_address)


def get_asset_price(price_feed_address: str):
    # Instanciate price feed
    price_feed = interface.IAggregatorV3(price_feed_address)
    # Get current asset price
    (_, answer, _, _, _) = price_feed.latestRoundData()
    # Number of decimals in the feed answer
    decimals = price_feed.decimals()

    return answer, decimals


def get_borrowable_data(lending_pool: Contract, account: Account):
    # Get user data
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrows_eth,
        current_liquidation_threshold,
        loan_to_value,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    # Transform data to more readable values (eth unit)
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    available_borrows_eth = Web3.fromWei(available_borrows_eth, "ether")

    print(f"Total collateral eth : {total_collateral_eth}")
    print(f"Total debt eth : {total_debt_eth}")
    print(f"Available to borrow eth : {available_borrows_eth}")
    return available_borrows_eth, total_debt_eth, total_collateral_eth
