from dataclasses import dataclass

@dataclass
class Country:
    name: str
    iso: str
    iso3: str

@dataclass
class City:
    name: str
    country_name: str

@dataclass
class Address:
    address_id: int
    country: str
    city: str
    street: str
    postal_code: str