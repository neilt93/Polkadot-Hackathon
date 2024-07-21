from web3 import Web3
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to Moonbeam Testnet
web3 = Web3(Web3.HTTPProvider('https://moonbeam-alpha.api.onfinality.io/public'))

# Load the contract ABI
json_path = os.path.join(os.path.dirname(__file__), 'build/contracts/NFT.json')
with open(json_path, 'r') as file:
    contract_json = json.load(file)
    contract_abi = contract_json['abi']

# Set the contract address and account details from the environment variables
contract_address = os.getenv('CONTRACT_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')
my_account = web3.eth.account.from_key(private_key)
my_address = my_account.address

# Initialize the contract
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def mint_nft(recipient, token_uri="null"):
    nonce = web3.eth.get_transaction_count(my_address)
    txn = contract.functions.createNFT(recipient, token_uri).build_transaction({
        'chainId': 1287,  # Moonbase Alpha network ID
        'gas': 2000000,
        'gasPrice': web3.to_wei('2', 'gwei'),
        'nonce': nonce
    })
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    #print(f'Transaction receipt: {tx_receipt}')
    return tx_receipt

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python mint.py <recipient> [token_uri]")
        sys.exit(1)
    
    recipient = sys.argv[1]
    token_uri = sys.argv[2] if len(sys.argv) == 3 else "null"
    mint_nft(recipient, token_uri)
