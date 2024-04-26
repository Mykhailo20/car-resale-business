from dataclasses import dataclass

from car_resale_business_project.databases.classes.OLAP.dimensions import *


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


@dataclass
class CarRepairFact:
    car_vin: str
    employee_dim: EmployeeDim
    location_dim: LocationDim
    date_dim: DateDim
    car_repair_type_dim: CarRepairTypeDim
    cost: int
    condition_delta: float
    oltp_id: int


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