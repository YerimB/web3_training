from brownie import network, config

from scripts.helpful.tools import get_asset_price


def eth_to_dai(eth_amount):
    # Get current network
    current_network = network.show_active()

    # Get eth / dai ratio
    eth_per_dai, decimals = get_asset_price(
        price_feed_address=config["networks"][current_network]["dai_eth_price_feed"]
    )

    # Convert
    dai_amount = (eth_amount * (10 ** decimals)) / eth_per_dai
    return dai_amount


def dai_to_eth(dai_amount):
    # Get current network
    current_network = network.show_active()

    # Get eth / dai ratio
    eth_per_dai, decimals = get_asset_price(
        price_feed_address=config["networks"][current_network]["dai_eth_price_feed"]
    )

    eth_amount = dai_amount * (eth_per_dai / (10 ** decimals))
    return eth_amount
