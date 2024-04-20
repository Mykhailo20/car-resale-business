from dataclasses import dataclass
from classes.OLTP.address import Address

@dataclass
class Seller:
    seller_id: int
    name: str
    type: str
    address: Address