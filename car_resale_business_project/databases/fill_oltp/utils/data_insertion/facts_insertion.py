from datetime import datetime, timedelta, date
import time

from faker import Faker
import random
from random import choice
import gender_guesser.detector as gender

import pandas as pd

from car_resale_business_project.databases.classes.OLTP.employee import *
from car_resale_business_project.databases.classes.OLTP.seller import *
from car_resale_business_project.databases.classes.OLTP.buyer import *
from car_resale_business_project.databases.classes.OLTP.car import *
from car_resale_business_project.databases.classes.OLTP.address import *
from car_resale_business_project.databases.classes.OLTP.purchase import *
from car_resale_business_project.databases.classes.OLTP.repair import *
from car_resale_business_project.databases.classes.OLTP.sale import *

from car_resale_business_project.databases.fill_oltp.utils.data_insertion.general_functions import *
from car_resale_business_project.databases.fill_oltp.utils.data_insertion.car_insertion import insert_into_car_table
from car_resale_business_project.databases.fill_oltp.utils.random_generation.dimensions_generation import *
from car_resale_business_project.config.data_config import FILL_OLTP_BATCH_SIZE, FILL_OLTP_CAR_CITY_CHANGE_FREQUENCY, FILL_OLTP_CAR_REPAIR_FREQUENCY


def insert_into_purchase_table(conn, purchases, logger):
    # Construct the SQL query
    query = """
        WITH purchase_seller AS (
        	SELECT seller_id
        	FROM seller s
        	JOIN address a
        	ON s.address_id = a.address_id
        	JOIN city c
        	ON c.city_id = a.city_id
        	WHERE 
        		s.name = %s
        		AND c.name = %s
        ), purchase_employee AS (
        	SELECT person_id 
        	FROM employee
        	WHERE 
        		first_name = %s 
        		AND last_name = %s
        )
        
        INSERT INTO purchase(
            car_vin, seller_id, employee_id, 
        	price, odometer, condition, 
            description, car_image, car_image_content_type, 
            purchase_date, created_at, updated_at
        )
        VALUES
        	(
        		%s,
        		(SELECT seller_id FROM purchase_seller),
        		(SELECT person_id FROM purchase_employee),
        		%s, %s, %s, 
                %s, %s, %s,
                %s::DATE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        	)

    """
    data = [
        (
            purchase.seller_name,
            purchase.city,
            purchase.employee.first_name,
            purchase.employee.last_name,
            purchase.car.vin,
            purchase.price,
            purchase.odometer,
            purchase.condition,
            purchase.description,
            purchase.car_image,
            purchase.car_image_content_type,
            purchase.purchase_date
        )
        for purchase in purchases
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'purchase', logger)

def insert_into_repair_table(conn, repairs, logger):
    # Construct the SQL query
    query = """
        WITH repair_address AS (
        	INSERT INTO address (city_id, street, postal_code, created_at, updated_at)
        	VALUES
        		((SELECT city_id FROM city WHERE name=%s), %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        	RETURNING address_id
        	
        ), repair_employee AS (
        	SELECT person_id 
        	FROM employee
        	WHERE 
        		first_name = %s 
        		AND last_name = %s
        )
        
        INSERT INTO repair(
        	car_vin, employee_id, address_id,
        	repair_type, cost, condition, description, 
        	repair_date, created_at, updated_at
        )
        VALUES
        	(
        		%s,
        		(SELECT person_id FROM repair_employee),
        		(SELECT address_id FROM repair_address),
        		%s, %s, %s, %s,
        		%s::DATE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        	)


    """
    data = [
        (
            repair.address.city,
            repair.address.street,
            repair.address.postal_code,
            repair.employee.first_name,
            repair.employee.last_name,
            repair.car_vin,
            repair.repair_type,
            repair.cost,
            repair.condition,
            repair.description,
            repair.repair_date
        )
        for repair in repairs
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'repair', logger)

def insert_into_sale_table(conn, sale_records, logger):
    # Construct the SQL query
    query = """
        WITH address_insert AS (
        	INSERT INTO address (city_id, street, postal_code, created_at, updated_at)
        	VALUES
        		((SELECT city_id FROM city WHERE name=%s), %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        	RETURNING address_id
        ), sale_buyer AS  (
        	INSERT INTO buyer (
        		first_name, last_name, middle_name, birth_date, sex, email,
        		address_id, created_at, updated_at
        	)
        	VALUES
        	(
        		%s, %s, %s, %s::DATE, %s, %s,
        		(SELECT address_id FROM address_insert),
        		CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        	)
        	RETURNING person_id
        ), sale_employee AS (
        	SELECT person_id 
        	FROM employee
        	WHERE 
        		first_name = %s 
        		AND last_name = %s
        )
        
        INSERT INTO sale(
        	car_vin, buyer_id, employee_id, 
        	mmr, price, odometer, 
        	condition,  description, car_image, car_image_content_type,
        	sale_date, created_at, updated_at
        )
        VALUES
        	(
        		%s,
        		(SELECT person_id FROM sale_buyer),
        		(SELECT person_id FROM sale_employee),
        		%s, %s, %s, 
        		%s, %s, %s, %s,
        		%s::DATE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        	)
    """
    data = [
        (
            sale_record_dict['buyer'].address.city,
            sale_record_dict['buyer'].address.street,
            sale_record_dict['buyer'].address.postal_code,
            sale_record_dict['buyer'].first_name,
            sale_record_dict['buyer'].last_name,
            sale_record_dict['buyer'].middle_name,
            sale_record_dict['buyer'].birth_date,
            sale_record_dict['buyer'].sex,
            sale_record_dict['buyer'].email,
            sale_record_dict['sale'].employee.first_name,
            sale_record_dict['sale'].employee.last_name,
            sale_record_dict['sale'].car_vin,
            sale_record_dict['sale'].mmr,
            sale_record_dict['sale'].price,
            sale_record_dict['sale'].odometer,
            sale_record_dict['sale'].condition,
            sale_record_dict['sale'].description,
            sale_record_dict['sale'].car_image,
            sale_record_dict['sale'].car_image_content_type,
            sale_record_dict['sale'].sale_date
        )
        for sale_record_dict in sale_records
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'sale', logger)


def perform_facts_filling(conn, car_df, logger, car_buyer_employees_list, car_mechanic_employees_list, car_seller_employees_list):

    # Preparation of necessary arrays and dictionaries
    car_df['sale_timestamp'] = pd.to_datetime(car_df['sale_timestamp'])
    car_df['sale_date'] = pd.to_datetime(car_df['sale_date'])
    car_df['sale_date_fake'] = pd.to_datetime(car_df['sale_date_fake'])

    print(f"len(car_df) = {len(car_df)}")
    print(f"len(car_df[car_df['sale_date'].dt.year < car_df['year']]) = {len(car_df[car_df['sale_date'].dt.year < car_df['year']])}")
    print(f"len(car_df[car_df['sale_date_fake'].dt.year < car_df['year']]) = {len(car_df[car_df['sale_date_fake'].dt.year < car_df['year']])}")

    car_buyer_employees = create_employee_df(car_buyer_employees_list)
    car_mechanic_employees = create_employee_df(car_mechanic_employees_list)
    car_seller_employees = create_employee_df(car_seller_employees_list)

    cities_list = list(car_df['city'].unique())

    car_buyer_employees['city'] = cities_list
    car_mechanic_employees['city'] = cities_list
    car_seller_employees['city'] = cities_list

    print(f"car_buyer_employees['city'].nunique() = {car_buyer_employees['city'].nunique()}")
    print(f"car_mechanic_employees['city'].nunique() = {car_mechanic_employees['city'].nunique()}")
    print(f"car_seller_employees['city'].nunique() = {car_seller_employees['city'].nunique()}\n")

    colors_list = list(car_df['color'].unique())
    # Define the color_weights_dict
    color_weights_dict = {}

    # Assign a random coefficient value to each color
    for color in colors_list:
        coefficient = round(random.uniform(0.5, 0.92), 1)
        color_weights_dict[color] = coefficient
    
    SALE_PRICE_MIN_MINUS_FOR_PURCHASE = 1000
    SALE_PRICE_MAX_MINUS_FOR_PURCHASE = 2000

    repair_enum_values = get_db_enum_values(conn=conn, enum_name='repair_type_enum')
    repair_enum_values = [value for value in repair_enum_values if value != 'painting']
    repair_type_cost_dict = {
        # 'painting': (100, 500),
        'mechanical_repair': (500, 1000),
        'body_repair': (450, 800),
        'electrical_repair': (400, 950)
    }

    repair_type_condition_dict = {
        # 'painting': (0, 0),
        'mechanical_repair': (0.2, 1),
        'body_repair': (0.3, 0.7),
        'electrical_repair': (0.1, 0.5)
    }

    MIN_PURCHASE_SALE_TIMEDELTA = timedelta(hours=1)
    MAX_PURCHASE_SALE_TIMEDELTA = timedelta(days=20)

    MIN_PURCHASE_REPAIR_TIMEDELTA = timedelta(hours=1)
    MAX_PURCHASE_REPAIR_TIMEDELTA = timedelta(days=3)

    unique_seller_city_pairs = car_df[['seller', 'city']].drop_duplicates()

    # Get car_vins values already inserted in DB
    with conn.cursor() as cur:
        cur.execute('SELECT vin FROM car')
        data = cur.fetchall()

    car_vins = [item[0] for item in data]
    encountered_car_vins = set(car_vins)
    print(f"Number of cars to insert (car_df['vin'].nunique()) = {car_df['vin'].nunique()}\n\n")

    # Insertion loop
    batch_size = FILL_OLTP_BATCH_SIZE if len(car_df) > FILL_OLTP_BATCH_SIZE else len(car_df)
    total_records = len(car_df)
    start_index = 0

    iteration = 0
    data_insertion_start_time = time.time()
    logger.info(f"Facts Insertion Loop: Starting process of inserting records into tables 'car', 'purchase', 'repair', 'buyer' and 'sale'. The number of cars is {car_df['vin'].nunique()}.")
    while start_index < total_records:
        end_index = min(start_index + batch_size, total_records)
        batch_df = car_df.iloc[start_index:end_index]
        cars_list = []
        purchases_list = []
        repairs_list = []
        sale_records_list = []
        
        faker = Faker()
        detector = gender.Detector()
        iteration_start_time = time.time()
        for index, row in batch_df.iterrows():
            
            car_vin = row['vin'].upper()
            car_color = row['color']
            car_condition = row['condition']
            purchase_odometer = row['odometer']
            purchase_city = row['city']
            car_seller = row['seller']
            sale_date = row['sale_date_fake']
            
            if car_vin in encountered_car_vins:
                continue  # Skip to the next iteration

            # Add the car_vin to the set of encountered values
            encountered_car_vins.add(car_vin)
            
            car_obj = Car(
                vin = car_vin,
                manufacture_year = int(row['year']),
                manufacturer = row['make'],
                model = row['model'],
                trim = row['trim'],
                body_type = row['body'].lower(),
                transmission = row['transmission'],
                color = row['color'],
                description = None
            )
        
            cars_list.append(car_obj)
            
            car_repair = None
            car_repair_cost = 0
            repair_date = None
            
            # Car repair
            if index % FILL_OLTP_CAR_REPAIR_FREQUENCY == 0:
                repair_employees_df = car_mechanic_employees[car_mechanic_employees['city'] == purchase_city]
                random_mechanic_employee = repair_employees_df.sample(n=1)
            
                # Generate random address
                repair_street = faker.street_address()
                repair_postal_code = faker.zipcode()
                repair_address = Address(address_id=None, country=None, city=purchase_city, street=repair_street, postal_code=repair_postal_code)
                
                repair_type = choice(repair_enum_values)
                
                if repair_type == 'painting':
                    test_color = select_new_random_value(car_color, colors_list)
                    
                car_repair_cost = generate_random_price(repair_type_cost_dict[repair_type][0], repair_type_cost_dict[repair_type][1])
                
                repair_date = (
                    sale_date 
                    - timedelta(seconds=random.uniform(MIN_PURCHASE_SALE_TIMEDELTA.total_seconds(), MAX_PURCHASE_SALE_TIMEDELTA.total_seconds()))
                )
                repair_date = repair_date.floor('D')
            
                upgrade = round(random.uniform(repair_type_condition_dict[repair_type][0], repair_type_condition_dict[repair_type][1]), 1)
                car_condition_temp = car_condition - upgrade
                if car_condition_temp >= 1.0:
                    car_condition -= upgrade
                    
        
            purchase_date = sale_date - timedelta(seconds=random.uniform(MIN_PURCHASE_SALE_TIMEDELTA.total_seconds(), MAX_PURCHASE_SALE_TIMEDELTA.total_seconds()))
            if repair_date is not None:
                purchase_date = repair_date - timedelta(seconds=random.uniform(MIN_PURCHASE_REPAIR_TIMEDELTA.total_seconds(), MAX_PURCHASE_REPAIR_TIMEDELTA.total_seconds()))
            purchase_date = purchase_date.floor('D')

            if (repair_date is not None) and (purchase_date > repair_date):
                purchase_date = repair_date
            if purchase_date.year < car_obj.manufacture_year:
                purchase_date = sale_date
                logger.warning(f"Facts Insertion Loop: a record with purchase_date.year < car_obj.manufacture_year was created due to random generation. To ensure the correctness of the data, purchase_date = sale_date is set: purchase_date = {purchase_date}; repair_date = {repair_date}; sale_date = {sale_date}")
                if repair_date is not None:
                    repair_date = sale_date
                    logger.warning(f"Facts Insertion Loop: a record with purchase_date.year < car_obj.manufacture_year was created due to random generation. To ensure the correctness of the data, purchase_date = sale_date; repair_date = sale_date is set: purchase_date = {purchase_date}; repair_date = {repair_date}; sale_date = {sale_date}")
                    
            odometer_range = (1, 5) # in percents
            
            # Change the city of the car
            if index % FILL_OLTP_CAR_CITY_CHANGE_FREQUENCY == 0:
                seller_cities_list = unique_seller_city_pairs[unique_seller_city_pairs['seller'] == car_seller]['city'].tolist()
                if len(seller_cities_list) != 1:
                    purchase_city = select_new_random_value(purchase_city, seller_cities_list)
                odometer_range = (3, 10)
            
            purchase_employees_df = car_buyer_employees[car_buyer_employees['city'] == purchase_city]
            random_buyer_employee = purchase_employees_df.sample(n=1)
            
            if purchase_odometer > 100:
                purchase_odometer = int(purchase_odometer - purchase_odometer * random.randint(odometer_range[0], odometer_range[1]) / 100)
            
            car_purchase = Purchase(
                car=car_obj,
                seller_id=None,
                seller_name=car_seller,
                address_id=None,
                city=purchase_city,
                employee=get_employee_obj(car_buyer_employees_list,  random_buyer_employee),
                price=int(
                    row['sellingprice'] - generate_random_price(SALE_PRICE_MIN_MINUS_FOR_PURCHASE, SALE_PRICE_MAX_MINUS_FOR_PURCHASE) 
                    * color_weights_dict[row['color']] - car_repair_cost
                ),
                odometer=purchase_odometer,
                condition=car_condition,
                description=None,
                car_image=None,
                car_image_content_type=None,
                purchase_date=purchase_date
            )

            # Car repair
            if index % FILL_OLTP_CAR_REPAIR_FREQUENCY == 0:
                car_repair = Repair(
                        repair_id=None,
                        car_vin=car_vin,
                        employee=get_employee_obj(car_mechanic_employees_list,  random_mechanic_employee),
                        address=repair_address,
                        repair_type=repair_type,
                        cost=car_repair_cost,
                        condition=row['condition'],
                        purchase_condition=None,
                        description=None,
                        repair_date=repair_date
                )
            
            buyer = generate_random_buyer(faker, detector, row['city'])
            
            sale_employees_df = car_seller_employees[car_seller_employees['city'] == row['city']]
            random_seller_employee = sale_employees_df.sample(n=1)
            
            car_sale = Sale(
                car_vin=car_vin,
                car_manufacture_year=None,
                buyer=buyer,
                employee=get_employee_obj(car_seller_employees_list,  random_seller_employee),
                mmr=int(row['mmr']),
                price=int(row['sellingprice']),
                odometer=int(row['odometer']),
                condition=row['condition'],
                car_image=None,
                car_image_content_type=None,
                description=None,
                sale_date=row['sale_date_fake'],
                purchase_price=None,
                repair_cost=None,
                purchase_date=None
            )
            
            sale_record = {'buyer': buyer, 'sale': car_sale}
            
            purchases_list.append(car_purchase)
            
            if car_repair is not None:
                repairs_list.append(car_repair)
                
            sale_records_list.append(sale_record)

        
        insert_into_car_table(conn, cars_list, logger)
        insert_into_purchase_table(conn, purchases_list, logger)
        insert_into_repair_table(conn, repairs_list, logger)
        insert_into_sale_table(conn, sale_records_list, logger)
        
        iteration_duration = time.time() - iteration_start_time
        print(f"Facts Insertion Loop: Iteration №{iteration + 1} duration: {iteration_duration // 60: .0f}m {iteration_duration % 60: .3f}s\n")
        logger.info(f"Facts Insertion Loop: Iteration {iteration + 1} duration: {iteration_duration // 60: .0f}m {iteration_duration % 60: .3f}s\n")
        
        iteration += 1
        start_index += batch_size

    data_insertion_duration = time.time() - data_insertion_start_time
    print(f"Facts Insertion Loop: Data insertion time: {data_insertion_duration // 60: .0f}m {data_insertion_duration % 60: .0f}s\n")
    logger.info(f"Facts Insertion Loop: Data insertion time: {data_insertion_duration // 60: .0f}m {data_insertion_duration % 60: .0f}s\n")