# Fibrous Finance Router Client for Python

Python client for Fibrous Router. It makes it easy to get the tokens and protocols supported by Fibrous, choose the best route for your swap from the Fibrous API and build those swap transactions. Compatible with Starknetpy.

## Installation

You can install fibrous-python via Pip.
```bash
pip install fibrous-python
```
Or
```bash
git clone https://github.com/Fibrous-Finance/router-python-sdk
cd fibrous_python
pip install .
```

## Usage

Create Fibrous client:
```python
from fibrous_python import FibrousClient

client = FibrousClient()

# or you can specify custom API url (you probably won't need this)
client = FibrousClient(route_url="https://api.fibrous.finance",
                       graph_url="https://graph.fibrous.finance",
                       router_address="0x00f6f4CF62E3C010E0aC2451cC7807b5eEc19a40b0FaaCd00CCA3914280FDf5a")
```

Get supported tokens by Fibrous.
```python
chainName="" #starknet or scroll
tokens = client.supported_tokens(chainId)
tokens["eth"]

# expected output:
Token(
    address='0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7',
    name='Ether',
    symbol='eth',
    decimals=18,
    price='3841.3',
    imageUrl='https://assets.coingecko.com/coins/images/279/small/ethereum.png?1696501628',
    valuable=True,
    verified=True,
    category=None
)
```

Get best route:
```python
chainName="" #starknet or scroll
tokens = client.supported_tokens(chainId)
route = client.get_best_route(amount=10**12,
                        token_in_address=tokens["eth"].address,
                        token_out_address=tokens["usdc"].address),
                        chainName
route

# expected output:
RouteSuccess(
    success=True,
    inputToken=Token(...),
    inputAmount='1000000000000',
    outputToken=Token(...),
    outputAmount='4117',
    route=[Route...],
    Slippage(input_token_value=0.00381994, output_token_value=0.005948858756000001, slippage=0.5573173285444276),
    estimatedGasUsed='8975364622720',
    bestQuotesByProtocols=['3821', '3876', '3815', '3878', '3838', '4117', '3883', '0', '3838', '5467'],
    time=1.354,
    initial=True
)
```

The slippage object contains the slippage value calculated by processing the input/output amount and token prices. In the example, the slipage object shows that the value of the tokens we send to fibrous is $0.00381, in return we will receive an `output token` with a value of $0.0059 and we will profit 55.73% from this transaction.

```python
 Slippage(input_token_value=0.00381994, output_token_value=0.005948858756000001, slippage=0.5573173285444276)
```


Build transaction:
```python
chainName="" # Chain name should be "starknet" for StarkNet and "scroll" for Scroll
tokens    = client.supported_tokens()
swap_call = client.build_transaction(input_amount=10**12,
                        token_in_address=tokens["eth"].address,
                        token_out_address=tokens["usdc"].address,
                        slippage=0.01,
                        # starknet address
                        destination="0x07bfe36393355f52844e45622ef0f0fd9bcb18c63f9004060effc8cc0970f8e1",
                        chain_name
                        )

# expected output:
Call(
    to_addr=436333995167355148017722927569021171726157728206902557777108018048487382874,
    selector=602962535134499854912799851629033993488593928113527484350375636311213640489,
    calldata=[int, int, int....]
)

```

## Swap example with Starknet.py
```python
import asyncio

from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair

from fibrous_python.core import FibrousClient
from fibrous_python.utils import build_approve_call


async def main():
    your_public_key = "0x123456"
    your_private_key = "0x123456"
    account0 = Account(
        address=your_public_key,
        client=FullNodeClient("https://rpc.starknet.lava.build:443"),
        key_pair=KeyPair(private_key=your_private_key,
                         public_key=your_public_key),
        chain=StarknetChainId.MAINNET)
    chainName="starknet"
    client = FibrousClient()
    tokens = client.supported_tokens(chainName)

    # amount to swap
    amount: int = int(0.001 * (10**tokens["eth"].decimals))

    # swap call
    swap_call = client.build_transaction(
        amount,
        tokens["eth"].address,
        tokens["usdc"].address,
        0.01,
        your_public_key,
        chainName)

    # approve call
    approve_call = build_approve_call(
            token_address=tokens["eth"].address,
            amount=amount)

    txre = await account0.execute(calls=[approve_call,
                                         swap_call],
                                  max_fee=int(1e16))

    print(f"Transaction hash: {hex(txre.transaction_hash)}")


if __name__ == "__main__":
    asyncio.run(main())
```

