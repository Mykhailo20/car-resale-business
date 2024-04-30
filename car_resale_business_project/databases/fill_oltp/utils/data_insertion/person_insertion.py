from faker import Faker
import random
from random import choice
import gender_guesser.detector as gender

from datetime import datetime, timedelta, date

from car_resale_business_project.databases.fill_oltp.utils.data_insertion.general_functions import *
from car_resale_business_project.databases.fill_oltp.utils.random_generation.dimensions_generation import *
from car_resale_business_project.config.data_config import SELLER_TYPE_DICT
from car_resale_business_project.databases.classes.OLTP.employee import *
from car_resale_business_project.databases.classes.OLTP.seller import *
from car_resale_business_project.databases.classes.OLTP.buyer import *
from car_resale_business_project.databases.classes.OLTP.address import *


def insert_into_position_table(conn, positions, logger):
    # Construct the SQL query
    query = """
        INSERT INTO position (
            name, description, created_at, updated_at
        )
        VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
    """
    data = [
        (
            position.name,
            position.description
        )
        for position in positions
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'position', logger)   


def insert_into_employee_table(conn, employees, logger):
    query = """
        INSERT INTO employee (
            first_name, last_name, middle_name, birth_date, sex, email,
            position_id, salary, hire_date, created_at, updated_at
        )
        SELECT
            %s, %s, %s, %s::DATE, %s, %s, p.position_id, %s, %s::DATE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        FROM
            position p
        WHERE
            p.name = %s;
    """
    data = [
        (
            employee.first_name,
            employee.last_name,
            employee.middle_name,
            employee.birth_date,
            employee.get_db_sex(),
            employee.email,
            employee.salary,
            employee.hire_date,
            employee.position
        )
        for employee in employees
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'employee', logger)


def insert_into_buyer_address_tables(conn, buyers, logger):
    query = """
        WITH address_insert AS (
        	INSERT INTO address (city_id, street, postal_code, created_at, updated_at)
        	VALUES
        		((SELECT city_id FROM city WHERE name=%s), %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        	RETURNING address_id
        )

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
    """
    data = [
        (
            buyer.address.city,
            buyer.address.street,
            buyer.address.postal_code,
            buyer.first_name,
            buyer.last_name,
            buyer.middle_name,
            buyer.birth_date,
            buyer.get_db_sex(),
            buyer.email,
            buyer.first_purchase_date
        )
        for buyer in buyers
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'buyer', logger)


def insert_into_seller_address_tables(conn, sellers, logger):
    query = """
        WITH address_insert AS (
        	INSERT INTO address (city_id, street, postal_code, created_at, updated_at)
        	VALUES
        		((SELECT city_id FROM city WHERE name=%s), %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        	RETURNING address_id
        )
        
        INSERT INTO seller(name, type, address_id, email, website_url, created_at, updated_at)
        VALUES
        	(
        		%s, %s, 
        		(SELECT address_id FROM address_insert),
        		%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        	)
    """
    data = [
        (
            seller.address.city,
            seller.address.street,
            seller.address.postal_code,
            seller.name,
            seller.type,
            seller.email,
            seller.website_url
        )
        for seller in sellers
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'seller', logger)


def perform_position_filling(conn, car_df, logger):
    position = Position(
        name='Manager',
        description='Responsible for buying cars from sellers, selling cars to buyers and finding repair shops if necessary.'
    )
    positions = [position]
    insert_into_position_table(conn, positions, logger)


def perform_seller_filling(conn, car_df, logger):
    seller_enum_values = get_db_enum_values(conn, 'seller_type_enum')
    unique_seller_city_pairs = car_df[['seller', 'city']].drop_duplicates()
    faker = Faker()

    sellers_list = []
    seller_type_loop_dict = {}

    for index, row in unique_seller_city_pairs.iterrows():
        seller_name = row['seller']
        seller_city = row['city']
        if seller_name not in seller_type_loop_dict.keys():
            seller_type = get_seller_type(seller_name, SELLER_TYPE_DICT)
            seller_type_loop_dict[seller_name] = seller_type

        seller_type = seller_type_loop_dict[seller_name]
        
        # Generate fake address
        street = faker.street_address()
        postal_code = faker.zipcode()
        
        address = Address(address_id=None, country=None, city=seller_city, street=street, postal_code=postal_code)
        seller = Seller(seller_id=None, name=seller_name, type=seller_type, address=address, email=None, website_url=None)

        sellers_list.append(seller)

    insert_into_seller_address_tables(conn, sellers_list, logger)


def perform_employee_class_filling(conn, faker, detector, EMPLOYEE_HIRE_DATE_RANGE, EMPLOYEE_SALARY_RANGE, EMPLOYEES_NUMBER_PER_TRANSACTION, logger, encountered_names:set):
    car_employees_list = []
    for i in range(EMPLOYEES_NUMBER_PER_TRANSACTION):
        new_employee, encountered_names = generate_random_employee(
            faker, detector, logger, employee_hire_date_range=[EMPLOYEE_HIRE_DATE_RANGE[0], EMPLOYEE_HIRE_DATE_RANGE[1]], 
            employee_salary_range=EMPLOYEE_SALARY_RANGE, encountered_names=encountered_names, position='Manager'
        )
        car_employees_list.append(new_employee)


    print(f"len(car_buyer_employees_list) = {len(car_employees_list)}")
    insert_into_employee_table(conn, car_employees_list, logger)
    return car_employees_list, encountered_names


def perform_employee_filling(conn, car_df, logger):
    max_car_year = car_df['year'].max()
    min_sale_date = car_df['sale_date'].min()

    EMPLOYEE_HIRE_DATE_RANGE = [date(2010, 1, 1), (min_sale_date - timedelta(days=30))]
    EMPLOYEE_SALARY_RANGE = (30000, 100000)
    EMPLOYEES_NUMBER_PER_TRANSACTION = car_df['city'].nunique()

    # Initialize Faker and Gender Detector
    faker = Faker()
    detector = gender.Detector()
    encountered_names = set()

    # The first EMPLOYEES_NUMBER_PER_TRANSACTION employees are Car Buyers
    car_buyer_employees_list, encountered_names = perform_employee_class_filling(conn, faker, detector, EMPLOYEE_HIRE_DATE_RANGE, EMPLOYEE_SALARY_RANGE, EMPLOYEES_NUMBER_PER_TRANSACTION, logger, encountered_names)

    # The next EMPLOYEES_NUMBER_PER_TRANSACTION employees are Car Mechanics
    car_mechanic_employees_list, encountered_names = perform_employee_class_filling(conn, faker, detector, EMPLOYEE_HIRE_DATE_RANGE, EMPLOYEE_SALARY_RANGE, EMPLOYEES_NUMBER_PER_TRANSACTION, logger, encountered_names)

    # The last EMPLOYEES_NUMBER_PER_TRANSACTION employees are Car Sellers
    car_seller_employees_list, encountered_names = perform_employee_class_filling(conn, faker, detector, EMPLOYEE_HIRE_DATE_RANGE, EMPLOYEE_SALARY_RANGE, EMPLOYEES_NUMBER_PER_TRANSACTION, logger, encountered_names)

    return car_buyer_employees_list, car_mechanic_employees_list, car_seller_employees_list

    
def perform_bussiness_participants_filling(conn, car_df, logger):
    logger.info("Starting process of inserting records into tables 'position', 'seller' and 'employee'.")
    perform_position_filling(conn, car_df, logger)
    perform_seller_filling(conn, car_df, logger)
    car_buyer_employees_list, car_mechanic_employees_list, car_seller_employees_list = perform_employee_filling(conn, car_df, logger)
    logger.info("Process of inserting records into tables 'position', 'seller' and 'employee' ended.")
    return car_buyer_employees_list, car_mechanic_employees_list, car_seller_employees_list


    
