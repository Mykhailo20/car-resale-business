from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from sqlalchemy import desc

from car_resale_business_project import db
from car_resale_business_project.cars.forms import SearchByVinForm, SearchByFiltersForm
from car_resale_business_project.cars.utils.filters import *
from car_resale_business_project.models import Car, CarMake, Seller, Purchase, Sale
from car_resale_business_project.config.website_config import LAST_PURCHASED_CARS_NUMBER

cars = Blueprint("cars", __name__, template_folder="templates", static_folder="static")


@cars.route('/last_purchased')
def last_purchased():

    # Fetch the top 5 last purchases sorted by purchase date
    last_purchases = Purchase.query.order_by(desc(Purchase.purchase_date)).limit(LAST_PURCHASED_CARS_NUMBER).all()
    filter_values_dict = get_filter_values()

    return render_template('purchased_cars.html', filter_values_dict=filter_values_dict, purchased_cars=last_purchases, main_page=True)


@cars.route('/last_purchased/filter', methods=['POST'])
def last_purchased_filter():

    filters = request.json
    filter_operations = get_purchase_filter_operations()
    for filter_name, filter_value in filters.items():
        if filter_name == 'csrf_token':
            continue
        session[filter_name] = filter_value

    print(f"/last_purchased/filter: session = {session}")

    base_query = Purchase.query.order_by(desc(Purchase.purchase_date))
    # Apply filters directly in the database query
    for filter_name, filter_value in session.items():
        if filter_value and filter_value != 'All':
            filter_operation = filter_operations.get(filter_name)
            if filter_operation:
                base_query = base_query.filter(filter_operation(filter_value))

    # Limit the number of results
    base_query = base_query.limit(LAST_PURCHASED_CARS_NUMBER)

    # Execute the query and fetch the results
    filtered_purchases = base_query.all()
    filtered_purchases_dict = [purchase.to_dict() for purchase in filtered_purchases]

    return jsonify(filtered_purchases_dict)


@cars.route('/last_sold')
def last_sold():
    return render_template('sold_cars.html', main_page=True)


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
        # Extract filters from the form
        filters = {}
        for key, value in form_data.items():
            if key in ['csrf_token', 'identifier', 'submit', 'car_search_choice']:
                continue

            if value != '__None':
                filters[key] = value

        return redirect(url_for('cars.search_results', search_place_choice=form_data['car_search_choice'], **filters))
        # return f"<h1>Cars Search Result</h1><p>You searched for form_data.get('brand') form_data.get('model')</p>"

    if request.form.get('identifier') == 'navbar_search_form' and request.method == 'POST': # It is not quite correct
        search_field_value = request.form.get('navbar_search_field')
        # Split the search field value into brand and model
        search_values = search_field_value.split(' ', 1)
        brand = search_values[0]
        model = None
        brand = CarMake.query.filter_by(name=brand).first()
        if len(search_values) == 2:
            model = search_values[1]
        filters = {
            'brand': brand.car_make_id if brand else -1, # # It is not quite correct
            'model': model
        }
        return redirect(url_for('cars.search_results', search_place_choice='cars_sold', **filters))
        
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


@cars.route('/search_results/<search_place_choice>', methods=['GET'])
def search_results(search_place_choice):

    # Retrieve filter parameters from the AJAX request
    filters = request.args

    base_query = Purchase.query.filter(Purchase.car_vin.not_in(Sale.query.with_entities(Sale.car_vin))).order_by(desc(Purchase.purchase_date))
    filter_operations = get_purchase_filter_operations()

    # Check if the "car_search_choice" filter is set to "cars_sold"
    if search_place_choice == 'cars_sold':
        base_query = Sale.query.order_by(desc(Sale.sale_date))
        filter_operations = get_sale_filter_operations()

    for filter_name, filter_value in filters.items():
        if filter_name == 'csrf_token':
            continue
        session[filter_name] = filter_value

    print(f"/search_results: session = {session}")

    # Apply filters directly in the database query
    for filter_name, filter_value in session.items():
        if filter_value and filter_value != 'All':
            filter_operation = filter_operations.get(filter_name)
            if filter_operation:
                base_query = base_query.filter(filter_operation(filter_value))

    base_query = base_query.limit(LAST_PURCHASED_CARS_NUMBER)

    filtered_transaction_records = base_query.all()

    print(f"filtered_transaction_records = {filtered_transaction_records}")

    filter_values_dict = get_filter_values()
    if search_place_choice == 'cars_in_storage':
        return render_template('purchased_cars.html', filter_values_dict=filter_values_dict, purchased_cars=filtered_transaction_records, main_page=False)
    return render_template('sold_cars.html', filter_values_dict=filter_values_dict, sold_cars=filtered_transaction_records, main_page=False)