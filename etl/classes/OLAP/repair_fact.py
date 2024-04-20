from dataclasses import dataclass
from classes.OLAP.employee_dim import EmployeeDim
from classes.OLAP.location_dim import LocationDim
from classes.OLAP.date_dim import DateDim

@dataclass
class CarRepairType:
    repair_type: str


@dataclass
class CarRepairFact:
    car_vin: str
    employee_dim: EmployeeDim
    location_dim: LocationDim
    date_dim: DateDim
    car_repair_type_dim: CarRepairType
    cost: int
    condition_delta: float
    oltp_id: int
