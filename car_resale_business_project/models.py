from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy import ForeignKeyConstraint
from dataclasses import dataclass
from datetime import datetime, date

from car_resale_business_project import db


@dataclass
class Country(db.Model):
    __tablename__ = 'country'

    country_id: int
    name: str
    iso: str
    iso3: str
    created_at: datetime
    updated_at: datetime

    country_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    iso = db.Column(db.String(2))
    iso3 = db.Column(db.String(3))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


@dataclass
class City(db.Model):
    __tablename__ = 'city'

    city_id: int
    country_id: int
    name: str
    created_at: datetime
    updated_at: datetime

    city_id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'))
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


@dataclass
class Address(db.Model):
    __tablename__ = 'address'

    address_id: int
    city_id: int
    street: str
    postal_code: str
    created_at: datetime
    updated_at: datetime

    address_id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.city_id'))
    street = db.Column(db.String(50))
    postal_code = db.Column(db.String(15))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    city = db.relationship('City', backref='address', lazy=True)


@dataclass
class Person(db.Model):
    __tablename__ = 'person'

    person_id: int
    first_name: str
    last_name: str
    middle_name: str
    birth_date: date
    sex: str
    email: str

    person_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    sex = db.Column(db.Text)
    email = db.Column(db.String(100))


@dataclass
class Position(db.Model):
    __tablename__ = 'position'

    position_id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    position_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


@dataclass
class Employee(db.Model):
    __tablename__ = 'employee'

    person_id: int
    first_name: str
    last_name: str
    middle_name: str
    birth_date: date
    sex: str
    email: str
    position_id: int
    salary: int
    hire_date: date
    created_at: datetime
    updated_at: datetime

    person_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    sex = db.Column(db.Text)
    email = db.Column(db.String(100))
    position_id = db.Column(db.Integer, db.ForeignKey('position.position_id'))
    salary = db.Column(db.Integer)
    hire_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


@dataclass
class Buyer(db.Model):
    __tablename__ = 'buyer'

    person_id: int
    first_name: str
    last_name: str
    middle_name: str
    birth_date: date
    sex: str
    email: str
    address_id: int
    created_at: datetime
    updated_at: datetime

    person_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    sex= db.Column(db.Text)
    email = db.Column(db.String(100))
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    address = db.relationship('Address', backref='buyer', lazy=True)

    def __repr__(self):
        return f"Buyer(person_id={self.person_id}, email='{self.email}', address_id={self.address_id})"

@dataclass
class Seller(db.Model):
    __tablename__ = 'seller'

    seller_id: int
    name: str
    type: str
    address_id: int
    email: str
    website_url: str
    created_at: datetime
    updated_at: datetime

    seller_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Text)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'))
    email = db.Column(db.String(100))
    website_url = db.Column(db.String(2048))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    address = db.relationship('Address', backref='seller', lazy=True)


@dataclass
class CarMake(db.Model):
    __tablename__ = 'car_make'

    car_make_id: int
    name: str

    car_make_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


@dataclass
class CarBodyType(db.Model):
    __tablename__ = 'car_body_type'

    car_body_type_id: int
    name: str
    descripton: str

    car_body_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    descripton = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


@dataclass
class Color(db.Model):
    __tablename__ = 'color'

    color_id: int
    name: str
    hex_code: str

    color_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    hex_code = db.Column(db.String(6))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


@dataclass
class Car(db.Model):
    __tablename__ = 'car'

    vin: str
    manufacture_year: int
    make_id: int
    model: str
    trim: str
    body_type_id: int
    transmission: str
    color_id: int
    description: str

    vin = db.Column(db.String(17), primary_key=True)
    manufacture_year = db.Column(db.Integer)
    make_id = db.Column(db.Integer, db.ForeignKey('car_make.car_make_id'))
    model = db.Column(db.String(50))
    trim = db.Column(db.String(100))
    body_type_id = db.Column(db.Integer, db.ForeignKey('car_body_type.car_body_type_id'))
    transmission = db.Column(db.Text)
    color_id = db.Column(db.Integer, db.ForeignKey('color.color_id'))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    make = db.relationship('CarMake', backref='car', lazy=True)
    body_type = db.relationship('CarBodyType', backref='car', lazy=True)
    color = db.relationship('Color', backref='car', lazy=True)


@dataclass
class Purchase(db.Model):
    __tablename__ = 'purchase'

    car_vin: str
    seller_id: int
    employee_id: int
    price: int
    odometer: int
    condition : float
    description: str
    car_image: bytes
    content_type: str
    purchase_date: date

    car_vin = db.Column(db.String(17),  db.ForeignKey('car.vin'), primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.seller_id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.person_id'))
    price = db.Column(db.Integer)
    odometer = db.Column(db.Integer)
    condition = db.Column(db.Numeric(2, 1))
    description = db.Column(db.Text)
    car_image =  db.Column(BYTEA)
    content_type = db.Column(db.String(10))
    purchase_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # Define the relationship with the Car table
    car = db.relationship('Car', backref='purchase', lazy=True)
    seller = db.relationship('Seller', backref='purchase', lazy=True)
    employee = db.relationship('Employee', backref='purchase', lazy=True)
