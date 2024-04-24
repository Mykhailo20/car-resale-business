from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from sqlalchemy import desc

from car_resale_business_project import db
from car_resale_business_project.cars.forms import SearchByVinForm, SearchByFiltersForm
from car_resale_business_project.cars.utils.filters import *
from car_resale_business_project.models import Car, Seller, Purchase, Address, City
from car_resale_business_project.config.website_config import LAST_PURCHASED_CARS_NUMBER

cars = Blueprint("cars", __name__, template_folder="templates", static_folder="static")

@cars.route('/last_purchased')
def last_purchased():

    # Fetch distinct manufacture years
    car_manufacture_years = Car.query.with_entities(Car.manufacture_year).distinct().all()
    car_manufacture_years = [year[0] for year in car_manufacture_years]

    # Fetch distinct cities
    cities = db.session.query(City).distinct(City.name).all()

    # Fetch the top 5 last purchases sorted by purchase date
    last_purchases = Purchase.query.order_by(desc(Purchase.purchase_date)).limit(LAST_PURCHASED_CARS_NUMBER).all()
    
    return render_template('last_purchased.html', car_manufacture_years=car_manufacture_years, cities=cities, last_purchases=last_purchases)

@cars.route('/last_purchased/filter', methods=['POST'])
def last_purchased_filter():

    filters = request.json
    filter_operations = get_filter_operations()
    for filter_name, filter_value in filters.items():
        session[filter_name] = filter_value

    base_query = Purchase.query.order_by(desc(Purchase.purchase_date))
    # Apply filters directly in the database query
    for filter_name, filter_value in session.items():
        print(f"filter_name = {filter_name}; filter_value={filter_value}")
        if filter_value and filter_value != 'All':
            filter_operation = filter_operations.get(filter_name)
            if filter_operation:
                base_query = base_query.filter(filter_operation(filter_value))

    # Limit the number of results
    base_query = base_query.limit(LAST_PURCHASED_CARS_NUMBER)

    # Execute the query and fetch the results
    filtered_purchases = base_query.all()
    filtered_purchases_dict = [purchase.to_dict() for purchase in filtered_purchases]
    # print(f"filtered_purchases_dict = {filtered_purchases_dict}")

    return jsonify(filtered_purchases_dict)


@cars.route('/search', methods=['GET', 'POST'])
def search():

    session.clear()
    car_vin_form = SearchByVinForm()
    car_filters_form = SearchByFiltersForm()

    if car_vin_form.identifier.data == "car_vin_form" and request.method == 'POST': # It is not quite correct
        car_vin = car_vin_form.car_vin.data
        return redirect(url_for('cars.search_results', **{'car_vin': car_vin}))
        # return f"<h1>Cars Search Result (car_vin form)</h1><p>You searched for {car_vin}</p>"
    
    if car_filters_form.identifier.data == "car_filters_form" and request.method == 'POST': # It is not quite correct
        form_data = request.form.to_dict()
        print(f"form_data = {form_data}")
        # Extract filters from the form
        filters = {}
        for key, value in form_data.items():
            if key in ['csrf_token', 'identifier', 'submit']:
                continue

            if value != '__None':
                filters[key] = value

        print("Filters:", filters)
        return redirect(url_for('cars.search_results', **filters))
        # return f"<h1>Cars Search Result</h1><p>You searched for form_data.get('brand') form_data.get('model')</p>"

    car_filters = {}

    car_transmissions = Car.query.with_entities(Car.transmission).distinct().all()
    car_transmissions = [year[0] for year in car_transmissions]
    car_filters['transmission'] = car_transmissions

    seller_names = Seller.query.with_entities(Seller.name).distinct().all()
    seller_names = [name[0] for name in seller_names]
    car_filters['seller_name'] = seller_names

    car_manufacture_years = Car.query.with_entities(Car.manufacture_year).distinct().all()
    car_manufacture_years = [year[0] for year in car_manufacture_years]
    car_filters['manufacture_year'] = car_manufacture_years

    return render_template("search.html", car_vin_form=car_vin_form, car_filters_form=car_filters_form, car_filters=car_filters)


@cars.route('/search_results', methods=['GET'])
def search_results():
    # Retrieve filter parameters from the AJAX request
    filters = request.args
    filter_operations = get_filter_operations()
    for filter_name, filter_value in filters.items():
        session[filter_name] = filter_value

    print(f"/search_results: session = {session}")

    # Construct the base query
    base_query = Purchase.query.order_by(desc(Purchase.purchase_date))

    # Apply filters directly in the database query
    for filter_name, filter_value in session.items():
        if filter_value and filter_value != 'All':
            filter_operation = filter_operations.get(filter_name)
            if filter_operation:
                base_query = base_query.filter(filter_operation(filter_value))

    base_query = base_query.limit(LAST_PURCHASED_CARS_NUMBER)

    filtered_purchases = base_query.all()
    # Fetch distinct manufacture years
    car_manufacture_years = Car.query.with_entities(Car.manufacture_year).distinct().all()
    car_manufacture_years = [year[0] for year in car_manufacture_years]

    # Fetch distinct cities
    cities = db.session.query(City).distinct(City.name).all()

    return render_template('last_purchased.html', car_manufacture_years=car_manufacture_years, cities=cities, last_purchases=filtered_purchases)