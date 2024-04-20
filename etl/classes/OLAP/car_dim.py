from dataclasses import dataclass

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