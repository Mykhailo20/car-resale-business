from car_resale_business_project import db
from car_resale_business_project.models import *


def get_filter_values(brand_id=None, model_name=None):
    
    filters_values = {}

    # Fetch distinct manufacture years
    car_manufacture_years = Car.query.with_entities(Car.manufacture_year).distinct().all()
    car_manufacture_years = [year[0] for year in car_manufacture_years]
    car_manufacture_years.sort()
    filters_values['car_manufacture_years'] = car_manufacture_years

    # Fetch distinct brands
    car_brands = CarMake.query.with_entities(CarMake.car_make_id, CarMake.name).distinct().all()
    brand_dict_list = [{'brand_id': brand[0], 'brand_name': brand[1]} for brand in car_brands]
    filters_values['car_brands'] = brand_dict_list
    
    # Fetch distinct models for the specified brand
    brand_id = int(brand_id) if brand_id is not None else None
    car_brand_models = Car.query.filter(Car.make_id == brand_id).with_entities(Car.model).distinct().all()
    car_brand_models = [model[0] for model in car_brand_models]
    filters_values['car_models'] = car_brand_models

    # Fetch distinct body types
    model_name = model_name if model_name is not None else None
    if brand_id is None:
        car_body_types = CarBodyType.query.with_entities(CarBodyType.car_body_type_id, CarBodyType.name).distinct().all()
    elif (brand_id is not None) and (model_name is None):
        car_body_types = db.session.query(CarBodyType.car_body_type_id, CarBodyType.name).join(Car).filter(Car.make_id == brand_id).distinct().all()
    elif (brand_id is not None) and (model_name is not None):
        car_body_types = db.session.query(CarBodyType.car_body_type_id, CarBodyType.name)\
                    .join(Car)\
                    .filter(Car.make_id == brand_id)\
                    .filter(Car.model == model_name)\
                    .distinct().all()

    car_body_types = [{'body_type_id': body_type[0], 'body_type_name': body_type[1]} for body_type in car_body_types]
    filters_values['car_body_types'] = car_body_types

    # Fetch distinct transmissions
    car_transmissions = Car.query.with_entities(Car.transmission).distinct().all()
    car_transmissions = [transmission[0] for transmission in car_transmissions]
    filters_values['car_transmissions'] = car_transmissions

    # Fetch distinct sellers
    seller_names = Seller.query.with_entities(Seller.name).distinct().all()
    seller_names = [name[0] for name in seller_names]
    filters_values['seller_name'] = seller_names

    # Fetch distinct cities
    cities = db.session.query(City).distinct(City.name).all()
    filters_values['cities'] = cities

    return filters_values


def get_purchase_filter_operations():
    # Define filter operations
    filter_operations = {
        'purchase_car_vin': lambda value: Purchase.car.has(vin=value),
        'purchase_brand': lambda value: Purchase.car.has(make_id=int(value)),
        'purchase_model': lambda value: Purchase.car.has(model=value),
        'purchase_body_type': lambda value: Purchase.car.has(body_type_id=int(value)),
        'purchase_transmission': lambda value: Purchase.car.has(transmission=value),
        'purchase_city': lambda value: Purchase.seller.has(Seller.address.has(Address.city.has(name=value))),
        'purchase_manufacture_year': lambda value: Purchase.car.has(manufacture_year=value),
        'purchase_condition': lambda value: Purchase.car.has(Car.condition.between(*map(float, value.split('-')))),
        'purchase_odometer': lambda value: Purchase.car.has(Car.odometer.between(*map(int, value.split('-')))),
        'purchase_date_from': lambda value: Purchase.purchase_date >= value,
        'purchase_date_to': lambda value: Purchase.purchase_date <= value
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