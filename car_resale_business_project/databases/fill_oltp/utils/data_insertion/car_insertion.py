from car_resale_business_project.databases.fill_oltp.utils.data_insertion.general_functions import insert_data
from car_resale_business_project.databases.classes.OLTP.car import *


def insert_into_car_body_type_table(conn, car_body_types, logger):
    # Construct the SQL query
    query = """
        INSERT INTO car_body_type (
            name, description, created_at, updated_at
        )
        VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
    """
    data = [
        (
            car_body_type.name,
            car_body_type.description
        )
        for car_body_type in car_body_types
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'car_body_type', logger)


def insert_into_car_make_table(conn, car_makes, logger):
    # Construct the SQL query
    query = """
        INSERT INTO car_make (
            name, created_at, updated_at
        )
        VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
    """
    data = [
        (car_make, ) for car_make in car_makes
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'car_make', logger)


def insert_into_color_table(conn, colors, logger):
    # Construct the SQL query
    query = """
        INSERT INTO color (
            name, hex_code, created_at, updated_at
        )
        VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
    """
    data = [
        (
            color.name,
            color.hex_code
        )
        for color in colors
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'color', logger)


def insert_into_car_table(conn, cars, logger):
    # Construct the SQL query
    query = """
        INSERT INTO car
        	(vin, manufacture_year, make_id, model, trim, body_type_id, transmission, color_id, description, created_at, updated_at)
        VALUES
        	(%s, %s, 
        	 (SELECT car_make_id FROM car_make WHERE name=%s),
        	 %s, %s,
        	 (SELECT car_body_type_id FROM car_body_type WHERE name=%s),
        	 %s,
        	 (SELECT color_id FROM color WHERE name=%s),
        	 %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        	)
    """
    data = [
        (
            car.vin,
            car.manufacture_year,
            car.manufacturer,
            car.model,
            car.trim,
            car.body_type,
            car.transmission,
            car.color,
            car.description
        )
        for car in cars
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'car', logger)


def perform_car_body_type_filling(conn, car_df, logger):
    car_body_types = car_df['body'].unique()
    car_body_type_list = []
    for car_body_type in car_body_types:
        car_body_type = CarBodyType(
            name=car_body_type,
            description=None
        )
        car_body_type_list.append(car_body_type)

    insert_into_car_body_type_table(conn, car_body_type_list, logger)


def perform_car_make_filling(conn, car_df, logger):
    car_makes = car_df['make'].unique()
    car_makes = list(car_makes)
    insert_into_car_make_table(conn, car_makes, logger)


def perform_color_filling(conn, car_df, logger):
    car_colors = car_df['color'].unique()

    car_color_list = []
    for car_color in car_colors:
        car_color_obj = Color(
            name=car_color,
            hex_code=None
        )
        car_color_list.append(car_color_obj)
    insert_into_color_table(conn, car_color_list, logger)


def perform_car_tables_filling(conn, car_df, logger):
    logger.info("Starting process of inserting records into tables 'car_body_type', 'car_make' and 'color'.")
    perform_car_body_type_filling(conn, car_df, logger)
    perform_car_make_filling(conn, car_df, logger)
    perform_color_filling(conn, car_df, logger)
    logger.info("Process of inserting records into tables 'car_body_type', 'car_make' and 'color' ended.")