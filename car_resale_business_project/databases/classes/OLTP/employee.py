from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Employee:
    employee_id: int
    first_name: str
    last_name: str
    middle_name: Optional[str]
    birth_date: date
    sex: str
    email: str
    position: str
    salary: int
    hire_date: date

    def get_db_sex(self):
        dataset_to_db_sex_dict = {'M': 'male', 'F': 'female'}
        return dataset_to_db_sex_dict[self.sex]
    
@dataclass
class Position:
    name: str
    description: str