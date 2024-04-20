from dataclasses import dataclass

@dataclass
class EmployeeDim:
    first_name: str
    age: int
    age_group: str
    sex: str
    salary: int
    work_experience: int
    oltp_id: int