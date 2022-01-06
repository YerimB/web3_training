from scripts.deploy import deploy_lottery
from scripts.start import start_lottery
from scripts.enter import enter_lottery
from scripts.end import end_lottery
from scripts.useful.tools import get_account

def main():
    owner = get_account()

    lottery = deploy_lottery(owner)
    start_lottery(lottery, owner)
    enter_lottery(lottery, owner)
    end_lottery(lottery, owner)