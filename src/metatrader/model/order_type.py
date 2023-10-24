
from enum import Enum


class OrderType(str, Enum):
    Buy = 'buy'
    Sell = 'sell'
