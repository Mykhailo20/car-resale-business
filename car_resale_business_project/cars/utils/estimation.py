import datetime

from sqlalchemy import func, desc
from sqlalchemy.orm import aliased

from car_resale_business_project import db
from car_resale_business_project.models import Car, CarMake, Seller, Purchase, Sale, Repair, Estimation


def get_new_estimation_price(car_vin):
    # Retrieve the last estimate for the specified car VIN
    last_estimation = db.session.query(Estimation)\
        .filter(Estimation.car_vin == car_vin)\
        .order_by(Estimation.estimation_date.desc(), Estimation.created_at.desc())\
        .limit(1)\
        .first()
    
    old_price = last_estimation.price

    purchase = Purchase.query.filter_by(car_vin=car_vin).first()

    repairs = Repair.query.filter_by(car_vin=car_vin).order_by(Repair.repair_date).all()
    if repairs:
        
        repairs_cost = sum([repair.cost for repair in repairs])
        old_price = purchase.price + repairs_cost
    
    current_date = datetime.date.today()
    months_since_purchase = (current_date.year - purchase.purchase_date.year) * 12 + current_date.month - purchase.purchase_date.month

    # Calculate the adjustment factor based on the elapsed time
    adjustment_factor = 0.03 - (months_since_purchase * 0.01)

    # Calculate the new estimated price
    new_estimated_price = old_price * (1 + adjustment_factor)

    return new_estimated_price


