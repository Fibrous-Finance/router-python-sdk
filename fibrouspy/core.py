import requests
from web3 import Web3
from web3.contract import Contract
from typing import Any, Dict, List, Optional, Union
from .abis.erc20ABI import erc20_abi
from .abis.fibrousRouterABI import fibrousRouterABI

class FibrousRouter:
    DEFAULT_API_URL = "https://api.fibrous.finance"
    GRAPH_API_URL = "https://graph.fibrous.finance"
    STARKNET_ROUTER_ADDRESS = "0x00f6f4CF62E3C010E0aC2451cC7807b5eEc19a40b0FaaCd00CCA3914280FDf5a"
    SCROLL_ROUTER_ADDRESS = "0x4bb92d3f730d5a7976707570228f5cb7e09094c5"

    def __init__(self, dedicated_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = dedicated_url.rstrip('/') if dedicated_url else self.DEFAULT_API_URL
        self.api_key = api_key

    def build_headers(self) -> Dict[str, str]:
        headers = {}
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"
        return headers

    def build_route_url(self, base_url: str, params: Dict[str, Any]) -> str:
        return f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

    def get_best_route(self, amount: int, token_in_address: str, token_out_address: str,
                       chain_name: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        route_params = {
            "amount": amount,
            "tokenInAddress": token_in_address,
            "tokenOutAddress": token_out_address
        }
        
        if options:
            route_params.update(options)
        
        url = self.build_route_url(f"{self.api_url}/{chain_name}/route", route_params)
        print(url)
        response = requests.get(url, headers=self.build_headers())
        response.raise_for_status()
        return response.json()

    def supported_tokens(self, chain_name: str) -> Dict[str, Dict[str, Any]]:
        url = f"{self.GRAPH_API_URL}/{chain_name}/tokens"
        response = requests.get(url, headers=self.build_headers())
        response.raise_for_status()
        tokens = response.json()
        return {token['symbol'].lower(): token for token in tokens}

    def supported_protocols(self, chain_name: str) -> Dict[str, str]:
        url = f"{self.GRAPH_API_URL}/{chain_name}/protocols"
        response = requests.get(url, headers=self.build_headers())
        response.raise_for_status()
        protocols = response.json()
        return {p['amm_name']: p['protocol'] for p in protocols}

    def build_approve_starknet(self, amount: int, token_address: str) -> Dict[str, Any]:
        return {
            "contractAddress": self.STARKNET_ROUTER_ADDRESS,
            "entrypoint": "approve",
            "calldata": [amount, token_address]
        }

    def build_approve_evm(self, amount: int, token_address: str, account: Web3, chain_name: str) -> bool:
        if chain_name == "scroll":
            contract = account.eth.contract(address=token_address, abi=erc20_abi)
            allowance = contract.functions.allowance(account.eth.default_account, self.SCROLL_ROUTER_ADDRESS).call()
            if allowance >= amount:
                return True
            
            tx = contract.functions.approve(self.SCROLL_ROUTER_ADDRESS, amount).transact()
            account.eth.waitForTransactionReceipt(tx)
            return True
        else:
            raise ValueError("Invalid chain ID")

    def build_transaction(self, amount: int, token_in_address: str, token_out_address: str,
                          slippage: float, destination: str, chain_name: str,
                          options: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], Any]:
        route_params = {
            "amount": amount,
            "tokenInAddress": token_in_address,
            "tokenOutAddress": token_out_address,
            "slippage": slippage,
            "destination": destination
        }
        
        if options:
            route_params.update(options)
        
        url = self.build_route_url(f"{self.api_url}/{chain_name}/execute", route_params)
        response = requests.get(url, headers=self.build_headers())
        response.raise_for_status()
        calldata = response.json()
        
        if chain_name == "starknet":
            return {
                "contractAddress": self.STARKNET_ROUTER_ADDRESS,
                "entrypoint": "swap",
                "calldata": calldata
            }
        elif chain_name == "scroll":
            return calldata
        else:
            raise ValueError("Invalid chain ID")

    def build_batch_transaction(self, amounts: List[int], token_in_addresses: List[str],
                                token_out_addresses: List[str], slippage: float,
                                destination: str, chain_name: str,
                                options: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], Any]:
        route_params = {
            "amounts": amounts,
            "tokenInAddresses": token_in_addresses,
            "tokenOutAddresses": token_out_addresses,
            "slippage": slippage,
            "destination": destination
        }
        
        if options:
            route_params.update(options)
        
        url = self.build_route_url(f"{self.api_url}/{chain_name}/executeBatch", route_params)
        response = requests.get(url, headers=self.build_headers())
        response.raise_for_status()
        calldata = response.json()
        
        if chain_name == "starknet":
            return [
                {
                    "contractAddress": self.STARKNET_ROUTER_ADDRESS,
                    "entrypoint": "swap",
                    "calldata": call
                }
                for call in calldata
            ]
        else:
            raise ValueError("Invalid chain ID")

    def get_contract_instance(self, rpc_url: str, chain_name: str) -> Contract:
        if chain_name == "scroll":
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            return w3.eth.contract(address=self.SCROLL_ROUTER_ADDRESS, abi=fibrousRouterABI)
        else:
            raise ValueError("Invalid chain ID")

    def get_contract_with_account(self, account: Web3, chain_name: str) -> Contract:
        if chain_name == "scroll":
            return account.eth.contract(address=self.SCROLL_ROUTER_ADDRESS, abi=fibrousRouterABI)
        else:
            raise ValueError("Invalid chain ID")
