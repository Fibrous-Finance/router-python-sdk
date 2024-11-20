from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call

def build_approve_call(token_address: str, amount: int) -> Call:
    """
    Creates an approve call to approve tokens.


    Args:
        token_address (str): Token to approve.
        amount (int): Approve amount.


    Returns:
        approve_call (Call): Starknetpy call.
    """
    approve_call = Call(
        to_addr=int(token_address, 16),
        selector=get_selector_from_name("approve"),
        calldata=[
            # spender -> fibrous router
            0x00f6f4CF62E3C010E0aC2451cC7807b5eEc19a40b0FaaCd00CCA3914280FDf5a,
            amount,
            0x0
    ])
    return approve_call
