from dataclasses import dataclass

from classes.OLAP.buyer_dim import BuyerDim
from classes.OLAP.employee_dim import EmployeeDim
from classes.OLAP.location_dim import LocationDim
from classes.OLAP.date_dim import DateDim

@dataclass
class CarSaleFact:
    car_vin: str
    buyer_dim: BuyerDim
    employee_dim: EmployeeDim
    location_dim: LocationDim
    date_dim: DateDim
    price: int
    gross_profit_amount: int
    gross_profit_percentage: int
    mmr: int
    price_margin: int
    car_years: int
    odometer: int
    condition: float
    employee_experience: int
    service_time: int
    service_cost: int