from typing import List, Union
from urllib.parse import urlencode

from ..models import RouteParams, RouteExecuteParams


def build_route_url(url: str, route_params: RouteParams | RouteExecuteParams) -> str:
    """
    Makes route params to url encoded.


    Args:
        url (str): Base url.
        route_params (RouteParams, RouteExecuteParams)

    Returns:
        url (str): API query url.

    """
    params = urlencode(route_params.__dict__)
    return f"{url}?{params}"


def fix_calldata(calldata: List[Union[str, int]]) -> List[int]:
    """
    Starknet.py requires all calldata elements to be integers, but the Fibrous
    API returns some hex strings and int strings (like "1000"). This function
    makes the calldata from Fibrous API compatible with Starknet.py.


    Args:
        calldata: Calldata response from Fibrous API.
    Returns:
        new_calldata: Formatted calldata.
    """
    def convert(d: Union[str, int]) -> int:
        if isinstance(d, str):
            return int(d, 16) if d.startswith("0x") else int(d)
        return d

    return [convert(d) for d in calldata]
