from dataclasses import dataclass
from car_resale_business_project.databases.classes.OLTP.address import Address

@dataclass
class Seller:
    seller_id: int
    name: str
    type: str
    address: Address
    email: str
    website_url: str