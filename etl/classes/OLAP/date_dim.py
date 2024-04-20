from dataclasses import dataclass
from datetime import date

@dataclass
class DateDim:
    date: date
    year: int
    month: int
    day: int
    week_day: str
    oltp_id: int
    fact_name: str