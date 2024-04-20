from dataclasses import dataclass

@dataclass
class BuyerDim:
    first_name: str
    age: int
    age_group: str
    sex: str
    oltp_id: int