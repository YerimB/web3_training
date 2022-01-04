import pytest

from brownie import network, accounts, exceptions
from scripts.useful.common import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account
from scripts.fund_me.deploy import deploy_fund_me


def get_wei_entrance_fee(contract, offset=100):
    return (contract._getEntranceFee() * 1e9) + offset


def test_can_fund_and_withdraw():
    # Initialisation
    account = get_account()
    contract = deploy_fund_me(account)
    wei_entrance_fee = get_wei_entrance_fee(contract)

    # Fund : Core
    tx = contract.fund({"from": account, "value": wei_entrance_fee})
    if tx.confirmations == 0:
        tx.wait(1)
    (is_funder, amount_funded, _) = contract.m_AddressToFunderData(account.address)

    # Fund : Check
    assert is_funder == True
    assert amount_funded == wei_entrance_fee

    # Withdraw : Core
    tx2 = contract.withdrawWei(amount_funded, {"from": account})
    if tx2.confirmations == 0:
        tx2.wait(1)
    (is_funder, amount_funded, _) = contract.m_AddressToFunderData(account.address)

    # Withdraw : Check
    assert is_funder == False
    assert amount_funded == 0


def test_can_fund_multiple_times():
    # Initialisation
    account = get_account()
    contract = deploy_fund_me(account)
    wei_entrance_fee = get_wei_entrance_fee(contract)
    total_funded = 0

    # Core
    tx = contract.fund({"from": account, "value": wei_entrance_fee})
    total_funded += wei_entrance_fee
    if tx.confirmations == 0:
        tx.wait(1)
    tx2 = contract.fund({"from": account, "value": 2 * wei_entrance_fee})
    total_funded += 2 * wei_entrance_fee
    if tx2.confirmations == 0:
        tx2.wait(1)
    (is_funder, amount_funded, _) = contract.m_AddressToFunderData(account.address)

    # Check
    assert is_funder == True
    assert amount_funded == total_funded


def test_can_withdraw_portion_of_amount_funded():
    # Initialisation
    account = get_account()
    contract = deploy_fund_me(account)
    wei_entrance_fee = get_wei_entrance_fee(contract)
    amount_to_withdraw = int(wei_entrance_fee * 0.5)

    # Core
    tx = contract.fund({"from": account, "value": wei_entrance_fee})
    if tx.confirmations == 0:
        tx.wait(1)
    (_, amount_funded, _) = contract.m_AddressToFunderData(account.address)
    tx2 = contract.withdrawWei(amount_to_withdraw, {"from": account})
    if tx2.confirmations == 0:
        tx2.wait(1)
    (is_funder, amount_funded_after_withdraw, _) = contract.m_AddressToFunderData(
        account.address
    )

    # Check
    assert is_funder == True
    assert amount_funded_after_withdraw == (amount_funded - amount_to_withdraw)


def test_cannot_withdraw_if_not_funder():
    # Skipping if not on local blockchain
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing.")

    # Initialisation
    bad_actor = accounts.add()
    contract = deploy_fund_me()
    withdraw_amount = get_wei_entrance_fee(contract)

    # Core : Exception expected
    with pytest.raises(exceptions.VirtualMachineError):
        contract.withdrawWei(withdraw_amount, {"from": bad_actor})


def test_cannot_withdraw_more_than_funded():
    # Initialisation
    account = get_account()
    contract = deploy_fund_me(account)
    wei_entrance_fee = get_wei_entrance_fee(contract)

    # Core : VMError expected
    # --- Deposit
    tx = contract.fund({'from': account, 'value': wei_entrance_fee})
    if tx.confirmations == 0:
        tx.wait(1)
    # --- Withdrawal
    (_, amount_funded, _) = contract.m_AddressToFunderData(account.address)
    with pytest.raises(exceptions.VirtualMachineError):
        # Trying to withdraw more than the amount funded right before
        contract.withdrawWei(amount_funded + 1, {"from": account})


def test_setting_entrance_fee():
    # Initialisation
    account = get_account()
    contract = deploy_fund_me(account)
    initial_wei_entrance_fee = get_wei_entrance_fee(contract, offset=0)

    # Core 1 : Superior
    tx = contract._setEntranceFee(200, {'from': account})
    if tx.confirmations == 0:
        tx.wait(1)
    new_wei_entrance_fee = get_wei_entrance_fee(contract, offset=0)
    # Check 1
    assert new_wei_entrance_fee > initial_wei_entrance_fee

    # Core 2 : Zero
    tx2 = contract._setEntranceFee(0, {'from': account})
    if tx2.confirmations == 0:
        tx2.wait(1)
    new_wei_entrance_fee = get_wei_entrance_fee(contract, offset=0)
    # Check 2
    assert new_wei_entrance_fee == 0

    # Core 3 : Negative (Expecting OverflowError)
    with pytest.raises(OverflowError):
        contract._setEntranceFee(-10, {'from': account})

    # Core 4 : From bad account (Expecting VMError)
    bad_actor = accounts.add()
    with pytest.raises(exceptions.VirtualMachineError):
        contract._setEntranceFee(50, {'from': bad_actor})
