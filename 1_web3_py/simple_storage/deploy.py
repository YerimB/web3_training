#!./../web3_venv/bin/python3

import os
import json

from dotenv import load_dotenv
from solcx import compile_standard, install_solc
from solcx.install import get_installed_solc_versions
from web3 import Web3
from web3.middleware import geth_poa_middleware
from semantic_version.base import Version


# CONSTANTS
LANGUAGE = "Solidity"
SOLC_VERSION = Version("0.8.7")
NETWORK_URL = "https://rinkeby.infura.io/v3/6db881fa5d5741029e8b3f5022f22930"
CHAIN_ID = 4


# Load .env file
load_dotenv()
# Load environment variables
PRIVATE_KEY_ADDR1 = os.getenv("PRIVATE_KEY_ADDR1")
PUBLIC_KEY_ADDR1 = os.getenv("PUBLIC_KEY_ADDR1")


# Install compiler if needed
if SOLC_VERSION not in get_installed_solc_versions():
    install_solc(SOLC_VERSION)

print("Compiling solidity...", end="", flush=True)
with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile solidity file
compiled_sol = compile_standard(
    input_data={
        "language": LANGUAGE,
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version=SOLC_VERSION,
)
print("Done.")

# Write compiled solidity file as JSON
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Get the bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# Get the abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# Connecting to ganache
w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
# Needed to interacting with rinkeby testnet
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

print("Creating contract on network...", end="", flush=True)
# Create the contract instance ('Contract' type, see : seb3._utils.datatypes.Contract)
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Set the nonce to the latest transaction count from my address
nonce = w3.eth.getTransactionCount(PUBLIC_KEY_ADDR1)

# 1. Build the transaction
txn_params = {
    # "gasPrice": w3.eth.gas_price,
    "chainId": CHAIN_ID,
    "from": PUBLIC_KEY_ADDR1,
    "nonce": nonce,
}
unsigned_txn = SimpleStorage.constructor().buildTransaction(txn_params)
# 2. Sign the transaction
signed_txn = w3.eth.account.sign_transaction(unsigned_txn, PRIVATE_KEY_ADDR1)
# 3. Send the signed transaction
txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# 4. Wait for transaction to end
txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
# Update nonce after transaction end
nonce += 1
print("Done.")

# Accessing the deployed contract
simple_storage = w3.eth.contract(address=txn_receipt.contractAddress, abi=abi)

# Call a view function from the contract
print(simple_storage.functions.retrieve().call())

print("Updating contract...", end="", flush=True)
# Call a function that modifies blockchain state
store_txn_params = {
    # "gasPrice": w3.eth.gas_price,
    "chainId": CHAIN_ID,
    "from": PUBLIC_KEY_ADDR1,
    "nonce": nonce,
}  # Create TX
unsigned_store_txn = simple_storage.functions.store(15).buildTransaction(
    store_txn_params
)
signed_store_txn = w3.eth.account.sign_transaction(
    unsigned_store_txn, PRIVATE_KEY_ADDR1
)  # Sign TX
txn_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)  # Send TX
txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)  # Get TX receipt
nonce += 1
print("Done.")

# Call a view function from the contract
print(simple_storage.functions.retrieve().call())
