from car_resale_business_project import db
from car_resale_business_project.models import City, Address, Car, Seller, Buyer, Purchase, Sale


def get_filter_values():

    filters_values = {}

    # Fetch distinct manufacture years
    car_manufacture_years = Car.query.with_entities(Car.manufacture_year).distinct().all()
    car_manufacture_years = [year[0] for year in car_manufacture_years]
    filters_values['car_manufacture_years'] = car_manufacture_years

    # Fetch distinct cities
    cities = db.session.query(City).distinct(City.name).all()
    filters_values['cities'] = cities

    return filters_values


def get_purchase_filter_operations():
    # Define filter operations
    filter_operations = {
        'car_vin': lambda value: Purchase.car.has(vin=value),
        'brand': lambda value: Purchase.car.has(make_id=int(value)),
        'model': lambda value: Purchase.car.has(model=value),
        'body_type': lambda value: Purchase.car.has(body_type_id=int(value)),
        'transmission': lambda value: Purchase.car.has(transmission=value),
        'city': lambda value: Purchase.seller.has(Seller.address.has(Address.city.has(name=value))),
        'manufacture_year': lambda value: Purchase.car.has(manufacture_year=value),
        'condition': lambda value: Purchase.car.has(Car.condition.between(*map(float, value.split('-')))),
        'odometer': lambda value: Purchase.car.has(Car.odometer.between(*map(int, value.split('-')))),
        'from_date': lambda value: Purchase.purchase_date >= value,
        'to_date': lambda value: Purchase.purchase_date <= value
    }

    return filter_operations


def get_sale_filter_operations():
    # Define filter operations
    filter_operations = {
        'car_vin': lambda value: Sale.car.has(vin=value),
        'brand': lambda value: Sale.car.has(make_id=int(value)),
        'model': lambda value: Sale.car.has(model=value),
        'body_type': lambda value: Sale.car.has(body_type_id=int(value)),
        'transmission': lambda value: Sale.car.has(transmission=value),
        'city': lambda value: Sale.buyer.has(Buyer.address.has(Address.city.has(name=value))),
        'manufacture_year': lambda value: Sale.car.has(manufacture_year=value),
        'condition': lambda value: Sale.car.has(Car.condition.between(*map(float, value.split('-')))),
        'odometer': lambda value: Sale.car.has(Car.odometer.between(*map(int, value.split('-')))),
        'from_date': lambda value: Sale.purchase_date >= value,
        'to_date': lambda value: Sale.purchase_date <= value
    }

    return filter_operations