from dataclasses import dataclass
from datetime import date

@dataclass
class Employee:
    employee_id: int
    first_name: str
    last_name: str
    middle_name: str
    birth_date: date
    sex: str
    email: str
    position: str
    salary: int
    hire_date: date


@dataclass
class Position:
    name: str
    description: str