from flask import redirect, url_for, request, jsonify, session, render_template, Response, stream_with_context
from sqlalchemy import func
import os
from datetime import datetime
import json

from car_resale_business_project import app, db, oltp_config_dict, olap_config_dict

from car_resale_business_project.config.files_config import FILL_OLTP_DATA_FILENAME, FILL_OLTP_CONFIG_FILENAME, ETL_CONFIG_FILENAME
from car_resale_business_project.config.data_config import FILL_OLTP_MIN_RECORDS_NUMBER
from car_resale_business_project.config.website_config import MAIN_PAGE_CONFIG_FILENAME

from car_resale_business_project.databases.etl.perform_etl import perform_etl
from car_resale_business_project.databases.fill_oltp.perform_filling import *

from car_resale_business_project.utils.help_functions import *
from car_resale_business_project.cars.utils.filters import remove_session_car_filters

from car_resale_business_project.models import Car, CarMake, CarBodyType
from car_resale_business_project.forms import AddPurchaseForm


@app.route('/')
def index():
    # session.clear()
    remove_session_car_filters()

    with open(MAIN_PAGE_CONFIG_FILENAME) as file:
        main_page_metadata = json.load(file)

    return redirect(url_for(main_page_metadata['main_page']))
    

@app.route('/databases')
def databases():
    
    records_number = get_file_length(filename=FILL_OLTP_DATA_FILENAME)
    oltp_db_filled = check_db_filled(oltp_config_dict, query="SELECT * FROM seller LIMIT 1;")
    olap_db_filled = check_db_filled(olap_config_dict, query="SELECT * FROM dim_seller LIMIT 1;")

    renew_main_page_metadata(filename=MAIN_PAGE_CONFIG_FILENAME, page_name='cars.last_purchased')

    return render_template('databases.html', filename=os.path.basename(FILL_OLTP_DATA_FILENAME), min_records_no=FILL_OLTP_MIN_RECORDS_NUMBER, max_records_no=records_number, oltp_db_filled=oltp_db_filled, olap_db_filled=olap_db_filled)

"""
@app.route('/fill_oltp')
def fill_oltp():
    print(f"fill_oltp")
    with app.app_context():
        try:
            # Send a message indicating that the OLTP DB filling process is starting
            yield "The OLTP DB filling process is starting.\n"

            # Retrieve the number of records selected by the user from the request
            records_number = request.args.get('records', type=int)
            yield f"Number of records selected by user: {records_number}.\n"

            # For testing purposes, you can print the message to the console
            print(f"Number of records selected by user: {records_number}")

            # Perform OLTP DB filling
            # perform_oltp_filling(samples_no=5000)
            time.sleep(5)  # Simulate delay between messages

            # If the process completes successfully, yield a success message
            yield "The OLTP DB filling process completed successfully\n"

        except Exception as e:
            # If an error occurs during the process, yield an error message
            yield f"Error occurred during OLTP DB filling: {str(e)}\n"
"""

@app.route('/fill_oltp')
def fill_oltp():
    print(f"fill_oltp")
    try:
        start_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{start_timestamp}]: The OLTP DB filling process has started.\n"
        records_number = request.args.get('records', type=int)
        print(f"Number of records selected by user: {records_number}")

        perform_oltp_filling(samples_no=records_number)

        end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message += f"[{end_timestamp}]: The OLTP DB filling process completed successfully.\n"
        renew_fill_oltp_metadata(filename=FILL_OLTP_CONFIG_FILENAME, last_filling_datetime=end_timestamp)

    except Exception as e:
        # If an error occurs during the process, yield an error message
        end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message += f"[{end_timestamp}]: Error occurred during OLTP DB filling: {str(e)}.\n"
    return message


@app.route('/fill_olap')
def fill_olap():
    print(f"fill_olap")
    try:
        start_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{start_timestamp}]: The OLAP DB filling process has started.\n"

        perform_etl(initial_data_loading=True)

        end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message += f"[{end_timestamp}]: The OLAP DB filling process completed successfully.\n"
    except Exception as e:
        # If an error occurs during the process, yield an error message
        end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message += f"[{end_timestamp}]: Error occurred during OLAP DB filling: {str(e)}.\n"
    return message

@app.route('/update_olap')
def update_olap():
    print(f"update_olap")
    try:
        start_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{start_timestamp}]: The OLAP Incremental ETL process has started.\n"

        perform_etl(initial_data_loading=False)

        end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message += f"[{end_timestamp}]: The OLAP Incremental ETL process completed successfully.\n"
    except Exception as e:
        # If an error occurs during the process, yield an error message
        end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message += f"[{end_timestamp}]: Error occurred during OLAP Incremental ETL process: {str(e)}.\n"
    return message

@app.route('/purchase')
def purchase():
    add_purchase_form = AddPurchaseForm()
    if add_purchase_form.identifier.data == "add_purchase_form" and request.method == 'POST': # It is not quite correct
        car_vin = add_purchase_form.car_vin.data
        print(f"Add Purchase: car_vin = {car_vin}")
    return render_template('purchase.html', add_purchase_form=add_purchase_form)

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
    renew_main_page_metadata(filename=MAIN_PAGE_CONFIG_FILENAME, page_name='databases')

