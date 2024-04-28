from dataclasses import dataclass
from datetime import date
from typing import Optional

from car_resale_business_project.databases.classes.OLTP.employee import Employee
from car_resale_business_project.databases.classes.OLTP.buyer import Buyer
from car_resale_business_project.databases.classes.OLTP.car import Car


@dataclass
class Sale:
    car_vin: str
    car_manufacture_year: int
    buyer: Buyer
    employee: Employee
    mmr: int
    price: int
    odometer: int
    condition: float
    description: str
    car_image: bytes
    car_image_content_type: str
    sale_date: date
    purchase_price: int
    repair_cost: int
    purchase_date: date