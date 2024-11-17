from web3 import Web3
from ...fibrouspy.core import FibrousRouter
from eth_utils import to_wei

# RPC URL for the Scroll network
RPC_URL = "https://rpc.scroll.io"

# Destination address for the swap (required)
DESTINATION = "<DESTINATION_ADDRESS>"

# Private key of the account that will be used to sign the transaction
PRIVATE_KEY = "<PRIVATE_KEY>"

def account(private_key, rpc_url):
    """
    Connect to the Scroll network and return the Web3 account instance.
    """
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    if not web3.isConnected():
        raise Exception("Unable to connect to the RPC URL")
    account_instance = web3.eth.account.privateKeyToAccount(private_key)
    return web3, account_instance

async def main():
    # Create a new router instance
    fibrous = FibrousRouter()

    # Create a Web3 account instance
    web3, account_instance = account(PRIVATE_KEY, RPC_URL)
    fibrous_contract = await fibrous.get_contract_with_account(account_instance, "scroll")

    # Build route options
    tokens = await fibrous.supported_tokens("scroll")
    token_in_address = tokens["usdt"]["address"]
    token_out_address = tokens["usdc"]["address"]
    token_in_decimals = int(tokens["usdt"]["decimals"])
    input_amount = int(to_wei(5, 'ether') / (10 ** (18 - token_in_decimals)))  # Equivalent to parseUnits("5", tokenInDecimals)

    # Build the transaction
    slippage = 1  # 1% slippage
    swap_call = await fibrous.build_transaction(
        input_amount,
        token_in_address,
        token_out_address,
        slippage,
        DESTINATION,
        "scroll"
    )

    # Approve the tokens
    approve_response = await fibrous.build_approve_evm(
        input_amount,
        token_in_address,
        account_instance.address,
        "scroll"
    )

    if approve_response:
        try:
            # Swap tokens
            swap_txn = fibrous_contract.functions.swap(
                swap_call["route"],
                swap_call["swap_parameters"]
            ).buildTransaction({
                'from': account_instance.address,
                'nonce': web3.eth.getTransactionCount(account_instance.address),
                'gas': 2000000,
                'gasPrice': web3.eth.gas_price,
            })

            signed_txn = web3.eth.account.sign_transaction(swap_txn, private_key=PRIVATE_KEY)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"https://scrollscan.com/tx/{receipt.transactionHash.hex()}")
        except Exception as e:
            print(f"Error swapping tokens: {e}")
    else:
        print("Error approving tokens")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
