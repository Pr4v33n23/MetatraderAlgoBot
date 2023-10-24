from enum import Enum

class OrderStatus(str, Enum):
    Open = 'open'
    Closed = 'closed'
