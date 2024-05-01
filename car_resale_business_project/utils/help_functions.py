import csv
import json
import base64

import psycopg2 as pg2
from sqlalchemy import desc

from car_resale_business_project.models import Address, Car, CarBodyType, Purchase, Repair, Sale, Estimation
from car_resale_business_project.config.data_config import FILL_OLTP_MIN_RECORDS_NUMBER, CAR_RELATIVE_CONDITION_DICT


def get_file_length(filename):
    with open(filename, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        row_count = 0
        for row in csv_reader:
            row_count += 1

        # The first row contains the record headers
        return row_count - 1
    

def renew_fill_oltp_metadata(filename, last_filling_datetime):
    with open(filename) as file:
        databases_metadata = json.load(file)
    databases_metadata['fill_oltp']['last_filling']['datetime'] = last_filling_datetime
    with open(filename, 'w') as file:
        json.dump(databases_metadata, file, indent=4)


def renew_main_page_metadata(filename, page_name):
    with open(filename) as file:
        databases_metadata = json.load(file)
    databases_metadata['main_page'] = page_name

    with open(filename, 'w') as file:
        json.dump(databases_metadata, file, indent=4)


def check_db_filled(db_config_dict, query):
    db_conn = pg2.connect(database=db_config_dict['database'], user=db_config_dict['user'], password=db_config_dict['password'])
    with db_conn.cursor() as cur:
        cur.execute(query)
        # Fetch the results
        data = cur.fetchall()
    db_conn.close()

    if len(data) > 0:
        return True
    return False

def get_car_transactions_data(vin):
    # Query the database to retrieve car details
    car = Car.query.filter_by(vin=vin).first()
    
    # Query the database to retrieve purchase details
    purchase = Purchase.query.filter_by(car_vin=vin).first()
    
    # Query the database to retrieve sale details
    sale = Sale.query.filter_by(car_vin=vin).first()

    # Query the database to retrieve latest estimation details
    latest_estimation = Estimation.query \
        .filter_by(car_vin=vin) \
        .order_by(desc(Estimation.estimation_date), desc(Estimation.created_at)) \
        .first()

    # Query the database to retrieve repair details
    repairs = Repair.query.filter_by(car_vin=vin).order_by(Repair.repair_date).all()

    # Initialize the list to store condition deltas
    repairs_condition_delta_list = []
    relative_conditions_list = [CAR_RELATIVE_CONDITION_DICT(purchase.condition)]
    if sale is not None:
        relative_conditions_list.append(CAR_RELATIVE_CONDITION_DICT(sale.condition)) # because we don't know how many repairs
        
    repairs_cost = 0
    car_condition = purchase.condition
    car_image = {"image": purchase.car_image, "content_type": purchase.car_image_content_type }
    car_rel_condition = CAR_RELATIVE_CONDITION_DICT(purchase.condition)

    # Iterate through repairs to calculate condition deltas
    for i, repair in enumerate(repairs):
        if i == 0:  # First repair
            condition_delta = repair.condition - purchase.condition
        else:
            previous_repair = repairs[i - 1]
            condition_delta = previous_repair.condition - repair.condition

        repairs_cost += repair.cost
        car_condition = repair.condition
        # Append the condition delta to the list
        repairs_condition_delta_list.append(condition_delta)
        repair_rel_condition = CAR_RELATIVE_CONDITION_DICT(repair.condition)
        car_rel_condition = repair_rel_condition 
        relative_conditions_list.append(repair_rel_condition)
    
    gross_profit_amount = None
    if sale is not None:
        gross_profit_amount = sale.price - purchase.price - repairs_cost
        if sale.car_image:
            car_image["image"] = sale.car_image 
            car_image["content_type"] = sale.car_image_content_type 
    
    if car_image['image'] is not None:
        car_image['image'] = base64.b64encode(car_image['image']).decode("utf-8")
    else:
        car_image = None

    return car, car_image, purchase, repairs, repairs_cost, repairs_condition_delta_list, relative_conditions_list, car_condition, car_rel_condition, sale, gross_profit_amount, latest_estimation