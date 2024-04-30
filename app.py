from flask import redirect, url_for, request, jsonify, render_template, flash 

import os
from datetime import datetime
import json
import base64

from car_resale_business_project import app, db, oltp_config_dict, olap_config_dict

from car_resale_business_project.config.files_config import FILL_OLTP_DATA_FILENAME, FILL_OLTP_CONFIG_FILENAME, ETL_CONFIG_FILENAME
from car_resale_business_project.config.data_config import FILL_OLTP_MIN_RECORDS_NUMBER, CAR_RELATIVE_CONDITION_DICT
from car_resale_business_project.config.website_config import MAIN_PAGE_CONFIG_FILENAME

from car_resale_business_project.databases.etl.perform_etl import perform_etl
from car_resale_business_project.databases.fill_oltp.perform_filling import *

from car_resale_business_project.utils.help_functions import *
from car_resale_business_project.cars.utils.filters import remove_session_car_filters

from car_resale_business_project.models import Address, Car, CarBodyType, Purchase, Repair, Sale
from car_resale_business_project.forms import AddPurchaseForm, AddRepairForm


@app.route('/')
def index():
    # session.clear()
    remove_session_car_filters()
    print(f"url_for('cars.car_page', vin=12345) = {url_for('cars.car_page', vin=12345)}")
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

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    add_purchase_form = AddPurchaseForm()
    if add_purchase_form.identifier.data == "add_purchase_form" and request.method == 'POST': # It is not quite correct
        
        car_image = request.files['car-image']
        car_image_content_type = None
        if car_image:
            car_image_content_type = car_image.mimetype

        form_data = request.form.to_dict()
        print(f"form_data = {form_data}")
        
        seller = add_purchase_form.seller_name.data
        employee = add_purchase_form.employee_name.data
        
        # Car
        car_vin = add_purchase_form.car_vin.data

        # Create a new car instance
        car = Car(
            vin=car_vin,
            manufacture_year=add_purchase_form.manufacture_year.data,
            make_id=add_purchase_form.brand.data.car_make_id,
            model=form_data['model'],
            trim=form_data['trim'],
            body_type_id=add_purchase_form.body_type.data.car_body_type_id,
            transmission=add_purchase_form.transmission.data,
            color_id=add_purchase_form.color.data.color_id,
            description=add_purchase_form.description.data,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Create a new purchase instance
        purchase = Purchase(
            car_vin=car_vin,
            seller_id=seller.seller_id,
            employee_id=employee.person_id,
            price=add_purchase_form.purchase_price.data,
            odometer=add_purchase_form.odometer.data,
            condition=add_purchase_form.condition.data,
            description=add_purchase_form.description.data,
            car_image=car_image.read(),
            car_image_content_type=car_image_content_type,
            purchase_date=add_purchase_form.purchase_date.data,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
        db.session.add(car)
        db.session.add(purchase)
        db.session.commit()
        return redirect(url_for('cars.last_purchased'))

    return render_template('add_purchase.html', add_purchase_form=add_purchase_form)

@app.route('/repair/<vin>', methods=['GET', 'POST'])
def repair(vin):
    
    add_repair_form = AddRepairForm()
    if add_repair_form.identifier.data == "add_repair_form" and request.method == 'POST': # It is not quite correct
        try:
            address = Address(
                city=add_repair_form.city.data,
                street=add_repair_form.street.data,
                postal_code=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            db.session.add(address)
            db.session.commit()

            repair = Repair(
                car_vin=vin,
                employee_id=add_repair_form.employee_name.data.person_id,
                address_id=address.address_id,
                repair_type=add_repair_form.repair_type.data,
                cost=add_repair_form.repair_cost.data,
                condition=add_repair_form.condition.data,
                description= add_repair_form.description.data,
                repair_date=add_repair_form.repair_date.data,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.session.add(repair)
            db.session.commit()
            flash("Registration of car repair was successful. The registration results can be viewed on this page (Repair History) or on the vehicle data page.", category='success')
        except Exception as e:
            print(f"Error occured during the registration of car repair: {e}")
            flash("Error occured during the registration of car repair. Please try again", category='error')
        
        return redirect(url_for('repair', vin=vin))
        
    # Query the database to retrieve car details
    car = Car.query.filter_by(vin=vin).first()
    
    # Query the database to retrieve purchase details
    purchase = Purchase.query.filter_by(car_vin=vin).first()

    repairs = Repair.query.filter_by(car_vin=vin).order_by(Repair.repair_date).all()

    # Initialize the list to store condition deltas
    repairs_condition_delta_list = []
    relative_conditions_list = [CAR_RELATIVE_CONDITION_DICT(purchase.condition)]
    car_condition = purchase.condition
    car_rel_condition = CAR_RELATIVE_CONDITION_DICT(purchase.condition)
    for i, repair in enumerate(repairs):
        if i == 0:  # First repair
            condition_delta = repair.condition - purchase.condition
        else:
            previous_repair = repairs[i - 1]
            condition_delta = previous_repair.condition - repair.condition

        car_condition = repair.condition
        # Append the condition delta to the list
        repairs_condition_delta_list.append(condition_delta)
        repair_rel_condition = CAR_RELATIVE_CONDITION_DICT(repair.condition)
        car_rel_condition = repair_rel_condition
        relative_conditions_list.append(repair_rel_condition)
    
    car_image = {"image": base64.b64encode(purchase.car_image).decode("utf-8"), "content_type": purchase.car_image_content_type }

    return render_template('add_repair.html', add_repair_form=add_repair_form, car=car, car_image=car_image, purchase=purchase, repairs=repairs, repairs_condition_delta_list=repairs_condition_delta_list, relative_conditions_list=relative_conditions_list, car_condition=car_condition, car_rel_condition=car_rel_condition)


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


@app.route('/get_car_brand_model_trims/<make_id>/<model_name>')
def get_car_brand_model_trims(make_id, model_name):
    print(f"make_id = {make_id}; model_name = {model_name}")
    if make_id is None:
        return "Make not found", 404
    
    if model_name is None:
        return "Model not found", 404
    
    trims = db.session.query(Car.trim).filter(Car.make_id == make_id, Car.model == model_name).distinct().all()
    
    if not trims:
        return "No trims found for the specified make and model", 404
    
    trim_values = [trim[0] for trim in trims]
    print(f"trims = {trims}; trim_values = {trim_values}")
    return jsonify(trim_values)
    


if __name__ == '__main__':
    app.run(debug=True)
    renew_main_page_metadata(filename=MAIN_PAGE_CONFIG_FILENAME, page_name='databases')

