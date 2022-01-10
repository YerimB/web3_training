from brownie import YamoToken, config, network
from brownie.network.account import Account
from brownie.network.contract import Contract, ContractContainer

from scripts.helpful.tools import get_account, wait_for_tx_confs

YAMO_TOKEN_PRECISION = 1e18
INITIAL_SUPPLY = 1e12 * YAMO_TOKEN_PRECISION


def deploy_yamo_token(
    account: Account, yamo_container: ContractContainer = YamoToken
) -> Contract:
    # Deploy token
    yamo_token = yamo_container.deploy(
        INITIAL_SUPPLY,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    # Wait for confirmation
    wait_for_tx_confs(yamo_token.tx.txid)

    print(f"{yamo_token.name()} Token ({yamo_token.symbol()}) deployed at : {yamo_token.address}")
    return yamo_token


def main():
    deploy_yamo_token(account=get_account())
