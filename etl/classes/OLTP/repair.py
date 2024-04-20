from dataclasses import dataclass
from datetime import date

from classes.OLTP.employee import Employee
from classes.OLTP.car import Car
from classes.OLTP.address import Address


@dataclass
class Repair:
    repair_id: int
    car_vin: str
    employee: Employee
    address: Address
    repair_type: str
    cost: int
    condition: float
    purchase_condition: float
    description: str
    repair_date: date