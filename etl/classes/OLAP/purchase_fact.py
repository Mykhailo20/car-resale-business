from dataclasses import dataclass
from classes.OLAP.car_dim import CarDim
from classes.OLAP.employee_dim import EmployeeDim
from classes.OLAP.seller_dim import SellerDim
from classes.OLAP.location_dim import LocationDim
from classes.OLAP.date_dim import DateDim

@dataclass
class CarPurchaseFact:
    car_dim: CarDim
    seller_id: int
    employee_dim: EmployeeDim
    location_id: int
    date_dim: DateDim
    price: int
    car_years: int
    odometer: int
    condition: float
    employee_experience: int