import json
import time
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import desc

from car_resale_business_project import db
from car_resale_business_project.models import Car, Purchase, Seller, Address
from car_resale_business_project.utils.filter_cars import *
from car_resale_business_project.config.website_config import LAST_PURCHASED_CARS_NUMBER


purchases = Blueprint("purchases", __name__, template_folder="templates", static_folder="static")


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

    filter_operations = {
        'fromDate': lambda value: Purchase.purchase_date >= value,
        'toDate': lambda value: Purchase.purchase_date <= value,
        'seller': lambda value: Purchase.seller.has(name=value),
        'location': lambda value: Purchase.seller.has(Seller.address.has(Address.city.has(name=value))),
        # Add more filters and their operations as needed
    }

    # Apply filters directly in the database query
    for filter_name, filter_value in filters.items():
        if filter_value and filter_value != 'All':
            filter_operation = filter_operations.get(filter_name)
            if filter_operation:
                base_query = base_query.filter(filter_operation(filter_value))

    # Print the final query
    print(f"Final query: {base_query}")

    # Limit the number of results
    base_query = base_query.limit(LAST_PURCHASED_CARS_NUMBER)

    # Execute the query and fetch the results
    filtered_purchases = base_query.all()
    filtered_purchases_dict = [purchase.to_dict() for purchase in filtered_purchases]
    # Return the filtered purchases as JSON response
    return jsonify(filtered_purchases_dict)
