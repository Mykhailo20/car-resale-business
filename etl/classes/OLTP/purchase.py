from dataclasses import dataclass
from datetime import date

from classes.OLTP.employee import Employee
from classes.OLTP.seller import Seller
from classes.OLTP.car import Car


@dataclass
class Purchase:
    purchase_id: str
    car: Car
    seller_id: int
    address_id: int
    employee: Employee
    price: int
    odometer: int
    condition: float
    description: str
    car_image: bytes
    car_image_content_type: str
    purchase_date: date