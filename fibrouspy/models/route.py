from typing import List, Union, Optional
from pydantic import BaseModel
from .token import Token


class RouteParams(BaseModel):
    amount: int
    tokenInAddress: str
    tokenOutAddress: str


class Swap(BaseModel):
    protocol: int
    poolId: str
    poolAddress: str
    fromTokenAddress: str
    toTokenAddress: str
    percent: str


class Route(BaseModel):
    percent: str
    swaps: List[List[Swap]]


class Slippage(BaseModel):
    # USD value of input
    input_token_value: float

    # USD value of output
    output_token_value: float

    # expected slippage out of 1 (profit or loss)
    # 0.1 = 10% positive slippage // -0.05 = 5% negative slippage
    slippage: float


class RouteSuccess(BaseModel):
    success: bool
    inputToken: Token
    inputAmount: str
    outputToken: Token
    outputAmount: str

    # best route
    route: List[Route]

    # expected slippage rates
    slippage: Optional[Slippage] = None

    estimatedGasUsed: str
    bestQuotesByProtocols: List[str]
    time: float
    initial: bool


class RouteExecuteParams(BaseModel):
    amount: Union[int, str]
    tokenInAddress: str
    tokenOutAddress: str
    slippage: float
    destination: str

