import json
import time
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import desc

from car_resale_business_project import db
from car_resale_business_project.models import Car, Purchase, Seller, Address
from car_resale_business_project.model_encoders import PurchaseEncoder
from car_resale_business_project.utils.filter_cars import *
from car_resale_business_project.config.website_config import LAST_PURCHASED_CARS_NUMBER


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
    # Fetch the top 5 last purchases sorted by purchase date
    last_purchases = Purchase.query.order_by(desc(Purchase.purchase_date)).limit(LAST_PURCHASED_CARS_NUMBER).all()
    
    return render_template('last_purchased.html', last_purchases=last_purchases)


@purchases.route('/last_purchased/filter', methods=['POST'])
def last_purchased_filter():
    # Retrieve filter parameters from the AJAX request
    filters = request.json
    print(f"filters = {filters}")
    # Construct the base query
    base_query = Purchase.query.order_by(desc(Purchase.purchase_date))

    # Apply filters directly in the database query
    if filters.get('fromDate') and filters.get('fromDate') != 'All':
        base_query = base_query.filter(Purchase.purchase_date >= filters['fromDate'])
        print(f"fromDate: base_query = {base_query}")
    if filters.get('toDate') and filters.get('toDate') != 'All':
        base_query = base_query.filter(Purchase.purchase_date <= filters['toDate'])
        print(f"toDate: base_query = {base_query}")
    if filters.get('seller') and filters.get('seller') != 'All':
        base_query = base_query.filter(Purchase.seller.has(name=filters['seller']))
        print(f"seller: base_query = {base_query}")
    if filters.get('location') and filters.get('location') != 'All':
        base_query = base_query.filter(Purchase.seller.has(Seller.address.has(Address.city.has(name=filters['location']))))
        print(f"location: base_query = {base_query}")

    # Limit the number of results
    base_query = base_query.limit(LAST_PURCHASED_CARS_NUMBER)

    # Execute the query and fetch the results
    filtered_purchases = base_query.all()

    # Return the filtered purchases as JSON response
    return jsonify(filtered_purchases)
