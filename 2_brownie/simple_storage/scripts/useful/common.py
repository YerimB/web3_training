from brownie import network, accounts

def get_account():
    active_network = network.show_active()

    if (active_network == 'development'):
        return accounts[0]
    # else
    return accounts.load("dev_mask_1")