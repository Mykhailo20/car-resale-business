from dataclasses import dataclass
from datetime import date

@dataclass
class BuyerDim:
    first_name: str
    age: int
    age_group: str
    sex: str
    oltp_id: int

@dataclass
class CarDim:
    vin: str
    manufacture_year: int
    make: str
    model: str
    trim: str
    body_type: str
    transmission: str
    color: str

@dataclass
class DateDim:
    date: date
    year: int
    month: int
    day: int
    week_day: str
    oltp_id: str    # was int
    fact_name: str

@dataclass
class EmployeeDim:
    first_name: str
    age: int
    age_group: str
    sex: str
    salary: int
    work_experience: int
    oltp_id: int

@dataclass
class LocationDim:
    country: str
    city: str
    oltp_id: int

@dataclass
class SellerDim:
    name: str
    type: str
    oltp_id: int


@dataclass
class CarRepairTypeDim:
    repair_type: str