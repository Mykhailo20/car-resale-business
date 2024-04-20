from dataclasses import dataclass
from datetime import date
from classes.OLTP.address import Address

@dataclass
class Buyer:
    buyer_id: int
    first_name: str
    last_name: str
    middle_name: str
    birth_date: date
    sex: str
    email: str
    address: Address