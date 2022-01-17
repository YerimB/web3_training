from brownie import config
from brownie import EventEmitter

from brownie import network
from brownie.network.account import Account

from scripts.useful.tools import get_account, wait_for_tx_confs


def deploy_event_emitter(account: Account):
    contract = EventEmitter.deploy({"from": account}, publish_source=config["networks"][network.show_active()].get("verify", False))
    wait_for_tx_confs(contract.tx.txid)

    return contract


def main():
    account = get_account()
    deploy_event_emitter(account)
