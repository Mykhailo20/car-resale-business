from flask import redirect, url_for, request, jsonify, session
from sqlalchemy import func

from car_resale_business_project import app, db
from car_resale_business_project.models import Car, CarMake, CarBodyType


@app.route('/')
def index():
    session.clear()
    return redirect(url_for('cars.last_purchased'))


@app.route('/get_car_brand_models/<make_id>')
def get_car_brand_models(make_id):
    if make_id is None:
        return "Make not found", 404
    if make_id == 'All':
        car_unique_models = Car.query.distinct(Car.model).all()
    else:
        car_unique_models = Car.query.filter_by(make_id=make_id).distinct(Car.model).all()
    # Serialize the list of car models to JSON
    car_models_json = [{"model": car.model} for car in car_unique_models]
    # Return the JSON response
    return jsonify(car_models=car_models_json)


@app.route('/get_car_brand_body_types/<make_id>')
def get_car_brand_body_types(make_id):
    if make_id is None:
        return "Make not found", 404
    if make_id == 'All':
        car_unique_body_types = CarBodyType.query.distinct(CarBodyType.car_body_type_id, CarBodyType.name).all()
    else:
        car_unique_body_types = db.session.query(CarBodyType.car_body_type_id, CarBodyType.name).join(Car).filter(Car.make_id == make_id).distinct().all()

    # Serialize the list of car models to JSON
    car_body_types_json = [{"body_type_id": body_type.car_body_type_id, "body_type_name": body_type.name} for body_type in car_unique_body_types]
    # Return the JSON response
    return jsonify(car_body_types=car_body_types_json)


@app.route('/get_car_brand_manufacture_years/<make_id>')
def get_car_brand_manufacture_years(make_id):
    if make_id is None:
        return "Make not found", 404
    if make_id == 'All':
        car_unique_manufacture_years = Car.query.distinct(Car.manufacture_year).all()
    else:
        car_unique_manufacture_years = Car.query.filter_by(make_id=make_id).distinct(Car.manufacture_year).all()

    # Serialize the list of car models to JSON
    car_manufacture_years_json = [{"manufacture_year": car.manufacture_year} for car in car_unique_manufacture_years]
    # Return the JSON response
    return jsonify(car_manufacture_years=car_manufacture_years_json)


@app.route('/get_car_brand_model_body_types/<make_id>/<model_name>')
def get_car_brand_model_body_types(make_id, model_name):
    if make_id is None:
        return "Make not found", 404
    
    if model_name is None:
        return "Model not found", 404
    
    if make_id == 'All':
        car_unique_body_types = CarBodyType.query.distinct(CarBodyType.car_body_type_id, CarBodyType.name).all()
    elif (make_id != 'All') and (model_name == 'All'):
        car_unique_body_types = db.session.query(CarBodyType.car_body_type_id, CarBodyType.name)\
                        .join(Car)\
                        .filter(Car.make_id == make_id)\
                        .distinct().all()
    else:
        car_unique_body_types = db.session.query(CarBodyType.car_body_type_id, CarBodyType.name)\
                        .join(Car)\
                        .filter(Car.make_id == make_id)\
                        .filter(Car.model == model_name)\
                        .distinct().all()
        
    # Serialize the list of car models to JSON
    car_body_types_json = [{"body_type_id": body_type.car_body_type_id, "body_type_name": body_type.name} for body_type in car_unique_body_types]
    # Return the JSON response
    return jsonify(car_body_types=car_body_types_json)


if __name__ == '__main__':
    app.run(debug=True)

