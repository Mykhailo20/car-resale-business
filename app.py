from flask import redirect, url_for, request, jsonify, render_template, flash 
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

import os
from datetime import datetime
import json
import base64

from car_resale_business_project import app, db, oltp_config_dict, olap_config_dict

from car_resale_business_project.config.files_config import FILL_OLTP_DATA_FILENAME, FILL_OLTP_CONFIG_FILENAME, ETL_CONFIG_FILENAME, OLAP_METADATA_FILENAME
from car_resale_business_project.config.data_config import FILL_OLTP_MIN_RECORDS_NUMBER, CAR_RELATIVE_CONDITION_DICT, CUBE_NAMES_DICT, CUBES_EXPORT_FILE_EXTENSIONS
from car_resale_business_project.config.website_config import MAIN_PAGE_CONFIG_FILENAME, OLAP_CUBES_EXPORT_METRICS_PER_ROW_NO, BOOTSTRAP_GRID_COLUMNS_NO

from car_resale_business_project.databases.etl.perform_etl import perform_etl
from car_resale_business_project.databases.fill_oltp.perform_filling import *

from car_resale_business_project.utils.help_functions import *
from car_resale_business_project.cars.utils.filters import remove_session_car_filters

from car_resale_business_project.models import Address, Car, CarBodyType, Purchase, Repair, Buyer, Sale
from car_resale_business_project.forms import AddPurchaseForm, AddRepairForm, AddSaleForm


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

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    add_purchase_form = AddPurchaseForm()
    if add_purchase_form.identifier.data == "add_purchase_form" and request.method == 'POST': # It is not quite correct
        try:
            car_image = request.files['car-image']
            car_image_content_type = None
            if car_image:
                car_image_content_type = car_image.mimetype

            form_data = request.form.to_dict()
            
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
                car_image=car_image.read() if car_image else None,
                car_image_content_type=car_image_content_type,
                purchase_date=add_purchase_form.purchase_date.data,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
            db.session.add(car)
            db.session.add(purchase)
            db.session.commit()
            flash("Registration of car purchase was successful. The registration results can be viewed on this page.", category='success')
            return redirect(url_for('cars.car_page', vin=car_vin))
        except Exception as e:
            db.session.rollback()  # Rollback changes in case of exception
            print(f"Error occured during the registration of car purchase: {e}")
            flash("Error occured during the registration of car purchase. Please try again.", category='error')
            return redirect(url_for('purchase'))

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
            db.session.rollback()  # Rollback changes in case of exception
            print(f"Error occured during the registration of car repair: {e}")
            flash("Error occured during the registration of car repair. Please try again.", category='error')
        
        return redirect(url_for('repair', vin=vin))
        
    car, car_image, purchase, repairs, repairs_cost, repairs_condition_delta_list, relative_conditions_list, car_condition, car_rel_condition, sale, gross_profit_amount = get_car_transactions_data(vin)

    return render_template('add_repair.html', add_repair_form=add_repair_form, car=car, car_image=car_image, purchase=purchase, repairs=repairs, repairs_condition_delta_list=repairs_condition_delta_list, relative_conditions_list=relative_conditions_list, car_condition=car_condition, car_rel_condition=car_rel_condition)


@app.route('/sale/<vin>', methods=['GET', 'POST'])
def sale(vin):
    add_sale_form = AddSaleForm()
    if add_sale_form.identifier.data == "add_sale_form" and request.method == 'POST': # It is not quite correct
        try:
            car_image = request.files['car-image']
            car_image_content_type = None
            if car_image:
                car_image_content_type = car_image.mimetype

            employee = add_sale_form.employee_name.data
            
            # Buyer Address
            address = Address(
                city=add_sale_form.city.data,
                street=add_sale_form.street.data,
                postal_code=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            db.session.add(address)
            db.session.commit()

            # Buyer
            buyer = Buyer(
                first_name=add_sale_form.buyer_first_name.data,
                last_name=add_sale_form.buyer_last_name.data,
                middle_name=add_sale_form.buyer_middle_name.data if add_sale_form.buyer_middle_name.data else None,
                birth_date=add_sale_form.buyer_birth_date.data,
                sex=add_sale_form.buyer_sex.data,
                email=add_sale_form.buyer_email.data if add_sale_form.buyer_email.data else None,
                address_id=address.address_id, 
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            db.session.add(buyer)
            db.session.commit()

            # Create a new purchase instance
            sale = Sale(
                car_vin=vin,
                buyer_id=buyer.person_id,
                employee_id=employee.person_id,
                price=add_sale_form.sale_price.data,
                odometer=add_sale_form.odometer.data,
                condition=add_sale_form.condition.data,
                description=add_sale_form.description.data,
                car_image=car_image.read() if car_image else None,
                car_image_content_type=car_image_content_type,
                sale_date=add_sale_form.sale_date.data,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            db.session.add(sale)
            db.session.commit()
            flash("Registration of car sale was successful. The registration results can be viewed on this page.", category='success')
            return redirect(url_for('cars.car_page', vin=vin))
        except Exception as e:
            db.session.rollback()  # Rollback changes in case of exception
            print(f"Error occured during the registration of car sale: {e}")
            flash("Error occured during the registration of car sale. Please try again.", category='error')
            return redirect(url_for('sale', vin=vin))
        
    car, car_image, purchase, repairs, repairs_cost, repairs_condition_delta_list, relative_conditions_list, car_condition, car_rel_condition, sale, gross_profit_amount = get_car_transactions_data(vin)

    return render_template('add_sale.html', add_sale_form=add_sale_form, car=car, car_image=car_image, purchase=purchase, repairs=repairs, repairs_cost=repairs_cost, repairs_condition_delta_list=repairs_condition_delta_list, relative_conditions_list=relative_conditions_list, car_condition=car_condition, car_rel_condition=car_rel_condition, sale=sale)

@app.route('/dasboard/purchases')
def dashboard_purchases():
    return render_template('bi_purchases_dashboard.html')

@app.route('/dasboard/sales')
def dashboard_sales():
    return render_template('bi_sales_dashboard.html')

@app.route('/cubes/export')
def olap_cubes_export():
    with open(OLAP_METADATA_FILENAME) as file:
        olap_metadata = json.load(file)
    return render_template('olap_cubes_export.html', olap_metadata=olap_metadata, cube_names_dict=CUBE_NAMES_DICT, file_extensions=CUBES_EXPORT_FILE_EXTENSIONS, metrics_cols_no=OLAP_CUBES_EXPORT_METRICS_PER_ROW_NO, bootstrap_cols_no=BOOTSTRAP_GRID_COLUMNS_NO)


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

