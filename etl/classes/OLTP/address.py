from dataclasses import dataclass

class Country:
    def __init__(self, name, iso, iso3):
        self.name = name
        self.iso = iso
        self.iso3 = iso3

class City:
    def __init__(self, name, country_name):
        self.name = name
        self.country_name = country_name

@dataclass
class Address:
    address_id: int
    country: str
    city: str
    street: str
    postal_code: str