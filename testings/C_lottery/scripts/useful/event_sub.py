from brownie import web3
from brownie import TimedLottery
from brownie.network.alert import Alert

from scripts.deploy import deploy_lottery
from scripts.enter import enter_lottery
from scripts.start import start_lottery
from scripts.useful.tools import get_account

# from scripts.useful.event_sub import subscribe_to_event_on_contract

def subscribe_to_event_on_contract():
    account = get_account()

    # Deploy
    contract = deploy_lottery(account, lottery_type=TimedLottery)
    w3_contract = web3.eth.contract(address=contract.address, abi=contract.abi)



    print(w3_contract.events.LotteryStarted().__dict__)

    # # Start
    # tx = start_lottery(contract, account, lottery_timeout=60)
    # # Enter
    # enter_lottery(contract, account)
    # # Wait for end
    # print(history)


def main():
    subscribe_to_event_on_contract()