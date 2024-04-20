from dataclasses import dataclass

@dataclass
class SellerDim:
    name: str
    type: str
    oltp_id: int