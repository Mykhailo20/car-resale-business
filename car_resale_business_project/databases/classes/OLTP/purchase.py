from dataclasses import dataclass
from datetime import date

from car_resale_business_project.databases.classes.OLTP.employee import Employee
from car_resale_business_project.databases.classes.OLTP.seller import Seller
from car_resale_business_project.databases.classes.OLTP.car import Car


@dataclass
class Purchase:
    car: Car
    seller_id: int
    seller_name: str
    address_id: int
    city: str
    employee: Employee
    price: int
    odometer: int
    condition: float
    description: str
    car_image: bytes
    car_image_content_type: str
    purchase_date: date