
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class Car:
    vin: str
    manufacture_year: int
    manufacturer: str
    model: str
    trim: str
    body_type: str
    transmission: str
    color: str
    description: Optional[str]=None

    def __post_init__(self):
        # Validate VIN
        if not re.match('^[A-Z0-9]{17}$', self.vin):
            raise ValueError("Invalid VIN format")

        # Validate manufacture_year
        if self.manufacture_year < 1900:
            raise ValueError("Manufacture year must be greater than or equal to 1900")
        

@dataclass
class CarBodyType:
    name: str
    description: str


@dataclass
class Color:
    name: str
    hex_code: str