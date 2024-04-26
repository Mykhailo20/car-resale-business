from dataclasses import dataclass
from typing import Optional
from datetime import date

from car_resale_business_project.databases.classes.OLTP.address import Address

@dataclass
class Buyer:
    buyer_id: int
    first_name: str
    last_name: str
    middle_name: str
    birth_date: date
    sex: str
    email: str
    address: Address
    dataset_to_db_sex_dict = {'M': 'male', 'F': 'female'}

    def get_db_sex(self):
        return self.__class__.dataset_to_db_sex_dict[self.sex]