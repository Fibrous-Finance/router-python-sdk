from typing import Optional, Union
from pydantic import BaseModel


class Token(BaseModel):
    """
    Represents ERC20 token
    """

    # hex string token address
    address: str

    # token full name
    name: str

    # token symbol / ticker
    symbol: str

    # token decimals
    decimals: int

    # token price
    price: Union[str, float]
    imageUrl: Optional[str] = None
    valuable: Optional[bool] = None

    # is token verifed by Fibrous
    verified: bool

    # token categories (unruggable, )
    category: Optional[str] = None

