import json
import time
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import desc

from car_resale_business_project import db
from car_resale_business_project.models import Car, Purchase, Seller, Address, City
from car_resale_business_project.utils.filter_cars import *
from car_resale_business_project.config.website_config import CAR_CARDS_PER_PAGE


purchases = Blueprint("purchases", __name__, template_folder="templates", static_folder="static")


@purchases.route('/add')
def add():
    return render_template('add.html')