from typing import Dict

import requests
from starknet_py.net.client_models import Call
from starknet_py.hash.selector import get_selector_from_name

from .models import (RouteSuccess,
                    Token,
                    Protocol,
                    Slippage,
                    RouteParams,
                    RouteExecuteParams)

from .utils import build_route_url, fix_calldata, calculate_slippage


class FibrousClient:
    """
    A client to interact with the Fibrous API.


    Args:
        route_url (str): The base URL for the route API.
        graph_url (str): The base URL for the graph API.
        router_address (str): The address of the fibrous router.
    """
    def __init__(self, route_url: str = "https://api.fibrous.finance",
                 graph_url: str = "https://graph.fibrous.finance",
                 router_address: str =
                 "0x00f6f4CF62E3C010E0aC2451cC7807b5eEc19a40b0FaaCd00CCA3914280FDf5a"
                 ) -> None:
        self.route_url = route_url
        self.graph_url =graph_url
        self.router_address = router_address
        self.headers = {"User-Agent": "FibrousPy/0.1.0"}

    def supported_tokens(self) -> Dict[str, Token]:
        """
        A list of supported tokens by Fibrous.


        Returns:
            tokens (List[Token]): Tokens list.

        """
        response = requests.get(f"{self.graph_url}/tokens",
                                headers=self.headers).json()
        tokens: Dict[str, Token] = {}
        for item in response:
            tokens[item["symbol"].lower()] = Token(**item)

        return tokens

    def supported_protocols(self) -> Dict[str, Protocol]:
        """
        A list of supported AMM protocols by Fibrous.

        Returns:
            protocols (Dict[str, Protocol]): List of protocols.
        """
        response = requests.get(f"{self.route_url}/protocols",
                                headers = self.headers).json()
        protocols = {}
        for i, v in enumerate(response):
            protocols[v] = Protocol(i)

        return protocols

    def get_best_route(self, amount: int, token_in_address: str,
                       token_out_address: str):
        """
        Get best route and extra data from Fibrous Router.


        Args:
            amount (in): Amount of tokens to be swapped.
            token_in_address (str): Input token address.
            token_out_address (str): Output token address.

        Returns:
            route_response (RouteSuccess): Detailed route response.
        """
        route_params = RouteParams(amount=amount,
                                   tokenInAddress=token_in_address,
                                   tokenOutAddress=token_out_address)
        route_url = build_route_url(f"{self.route_url}/route", route_params)

        response = requests.get(route_url, headers=self.headers).json()
        route_response = RouteSuccess(**response)
        route_response.slippage = calculate_slippage(route_response)

        return route_response

    def build_transaction(self, input_amount: int, token_in_address: str,
                          token_out_address: str, slippage: float,
                          destination:str) -> Call:
        """
        Get calldata from Fibrous Router to swap tokens.


        Args:
            token_in_address (str): Input token address.
            token_out_address (str): Output token address.
            slippage (float): Arbitrary slipage rate.
                The maximum value this parameter can take is 0.49.
                1.0 = 100% // 0.1 = 10% // 0.05 = 5%
            destination (str): Address to send the output token to.
                You will probably want to pass your address here.


        Returns:
            calldata (Call): Starknetpy call object.
        """
        amount = hex(input_amount)
        route_params = RouteExecuteParams(amount=amount,
                                         tokenInAddress=token_in_address,
                                         tokenOutAddress=token_out_address,
                                         destination=destination,
                                         slippage=slippage)
        route_url = build_route_url(f"{self.route_url}/execute", route_params)
        calldata = requests.get(route_url,
                               headers=self.headers).json()

        return Call(to_addr=int(self.router_address, 16),
                    selector=get_selector_from_name("swap"),
                    calldata=fix_calldata(calldata))

