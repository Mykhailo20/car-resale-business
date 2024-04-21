from car_resale_business_project import db
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy import ForeignKeyConstraint

class Country(db.Model):
    __tablename__ = 'country'

    country_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    iso = db.Column(db.String(2))
    iso3 = db.Column(db.String(3))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    cities = db.relationship('City', backref='country')


class City(db.Model):
    __tablename__ = 'city'

    city_id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'))
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    

class Address(db.Model):
    __tablename__ = 'address'

    address_id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.city_id'))
    street = db.Column(db.String(50))
    postal_code = db.Column(db.String(15))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    city = db.relationship('City', backref='address', lazy=True)


class Person(db.Model):
    __tablename__ = 'person'

    person_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    sex= db.Column(db.Text)
    email = db.Column(db.String(100))


class Position(db.Model):
    __tablename__ = 'position'

    position_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    descripton = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    employees = db.relationship('Employee', backref='position')


class Employee(db.Model):
    __tablename__ = 'employee'

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

    def __repr__(self):
        """
        return f"Employee(person_id={self.person_id}, first_name='{self.first_name}', last_name='{self.last_name}', middle_name='{self.middle_name}', birth_date='{self.birth_date}', sex='{self.sex}', email='{self.email}', position_id={self.position_id}, salary={self.salary}, hire_date='{self.hire_date}', created_at='{self.created_at}', updated_at='{self.updated_at}')"
        """
        return f"Employee(person_id={self.person_id}, email='{self.email}', position_id={self.position_id}, salary={self.salary}, hire_date='{self.hire_date}')"


class Buyer(db.Model):
    __tablename__ = 'buyer'

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

class Seller(db.Model):
    __tablename__ = 'seller'

    seller_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Text)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'))
    email = db.Column(db.String(100))
    website_url = db.Column(db.String(2048))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    address = db.relationship('Address', backref='seller', lazy=True)


class CarMake(db.Model):
    __tablename__ = 'car_make'

    car_make_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    # A car manufacturer can produce many cars
    cars = db.relationship('Car', backref='car_make')


class CarBodyType(db.Model):
    __tablename__ = 'car_body_type'

    car_body_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    descripton = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    cars = db.relationship('Car', backref='car_body_type')


class Color(db.Model):
    __tablename__ = 'color'

    color_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    hex_code = db.Column(db.String(6))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


class Car(db.Model):
    __tablename__ = 'car'

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

    def __repr__(self):
        return f"Car(vin='{self.vin}')"


class Purchase(db.Model):
    __tablename__ = 'purchase'

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


    def __repr__(self):
        return f"Purchase(car_vin='{self.car_vin}', Car(vin='{self.car.vin}'))"
