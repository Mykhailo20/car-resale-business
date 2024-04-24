from flask import redirect, url_for, request, jsonify, session
from sqlalchemy import func

from car_resale_business_project import app
from car_resale_business_project.models import Car, CarMake


@app.route('/')
def index():
    session.clear()
    return redirect(url_for('cars.last_purchased'))


@app.route('/get_car_brand_models/<make_id>')
def get_car_brand_models(make_id):
    if make_id is None:
        return "Make not found", 404
    car_unique_models = Car.query.filter_by(make_id=make_id).distinct(Car.model).all()
    # Serialize the list of car models to JSON
    car_models_json = [{"model": car.model} for car in car_unique_models]
    # Return the JSON response
    return jsonify(car_models=car_models_json)



if __name__ == '__main__':
    app.run(debug=True)

