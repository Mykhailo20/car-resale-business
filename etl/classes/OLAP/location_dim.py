from dataclasses import dataclass

@dataclass
class LocationDim:
    country: str
    city: str
    oltp_id: int