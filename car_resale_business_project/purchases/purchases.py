from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from car_resale_business_project.utils.filter_cars import *

purchases = Blueprint("purchases", __name__, template_folder="templates", static_folder="static")

# Define a list to simulate car data (replace this with your actual data source)
cars_data = [
    {"model": "Toyota", "brand": "Toyota", "year": 2020, "seller": "Nissan Seller", "purchase_date": "2021-05-07", "location": "Sacramento"},
    {"model": "Civic", "brand": "Honda", "year": 2018, "seller": "Kia Rio Seller", "purchase_date": "2020-05-07", "location": "Austin"},
    {"model": "Camry", "brand": "Toyota", "year": 2019, "seller": "Nissan Seller", "purchase_date": "2022-05-07", "location": "Albany"}
]


@purchases.route('/add')
def add():
    return render_template('add.html')

@purchases.route('/last_purchased')
def last_purchased():
    return render_template('last_purchased.html')


@purchases.route('/last_purchased/filter', methods=['POST'])
def last_purchased_filter():
    # Retrieve filter parameters from the AJAX request
    filters = request.json

    # Perform filtering logic based on the received filters
    filtered_cars = filter_cars(filters, cars_data=cars_data)

    # Return the filtered cars as JSON response
    return jsonify(filtered_cars)
