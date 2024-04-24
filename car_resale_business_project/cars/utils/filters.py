from car_resale_business_project.models import Car, Seller, Purchase, Address, City

def get_filter_operations():
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