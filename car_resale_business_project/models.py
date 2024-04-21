from car_resale_business_project import db

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
    # Different cars can have the same color
    cars = db.relationship('Car', backref='color')


class Car(db.Model):
    __tablename__ = 'car'

    vin = db.Column(db.Text, primary_key=True)
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

    def __repr__(self):
        return f"car_vin = {self.vin}"
