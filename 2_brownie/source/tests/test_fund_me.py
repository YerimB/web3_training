import pytest

from brownie import network, accounts, exceptions
from scripts.useful.common import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account
from scripts.fund_me.deploy import deploy_fund_me


def test_can_fund_and_withdraw():
    # Initialisation
    account = get_account()
    contract = deploy_fund_me()
    wei_entrance_fee = (contract._getEntranceFee() * 1e9) + 100

    # Fund : Core
    tx = contract.fund({'from': account, 'value': wei_entrance_fee})
    if tx.confirmations == 0:
        tx.wait(1)
    (is_funder, _, amount_funded) = contract.m_AddressToFunderData(account.address)

    # Fund : Check
    assert is_funder == True
    assert amount_funded == wei_entrance_fee

    # Withdraw : Core
    tx2 = contract.withdrawWei(amount_funded, {'from': account})
    if tx2.confirmations == 0:
        tx2.wait(1)
    (is_funder, _, amount_funded) = contract.m_AddressToFunderData(account.address)

    # Withdraw : Check
    assert is_funder == False
    assert amount_funded == 0


def test_cannot_withdraw_if_not_funder():
    # Skipping if not on local blockchain
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing.")

    # Initialisation
    bad_actor = accounts.add()
    contract = deploy_fund_me()
    withdraw_amount = (contract._getEntranceFee() * 1e9) + 100

    # Core : Exception expected
    with pytest.raises(exceptions.VirtualMachineError):
        contract.withdrawWei(withdraw_amount, {'from': bad_actor})
