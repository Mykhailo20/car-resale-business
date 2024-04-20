
from dataclasses import dataclass
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

    def __post_init__(self):
        # Validate VIN
        if not re.match('^[A-Z0-9]{17}$', self.vin):
            raise ValueError("Invalid VIN format")

        # Validate manufacture_year
        """
        if self.manufacture_year < 1900:
            raise ValueError("Manufacture year must be greater than or equal to 1900")
        """