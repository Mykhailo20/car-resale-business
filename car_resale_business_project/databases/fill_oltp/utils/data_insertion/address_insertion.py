from car_resale_business_project.databases.fill_oltp.utils.data_insertion.general_functions import insert_data
from car_resale_business_project.config.data_config import CITY_TO_COUNTRY_DICT
from car_resale_business_project.databases.classes.OLTP.address import *


def insert_into_country_table(conn, countries, logger):
    # Construct the SQL query
    query = """
        INSERT INTO country (
            name, iso, iso3, created_at, updated_at
        )
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
    """
    data = [
        (
            country.name,
            country.iso,
            country.iso3
        )
        for country in countries
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'country', logger)


def insert_into_city_table(conn, cities, logger):
    # Construct the SQL query
    query = """
        INSERT INTO city (
            name, country_id, created_at, updated_at
        )
        VALUES (%s, (SELECT country_id FROM country WHERE name = %s), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
    """
    data = [
        (
            city.name,
            city.country_name
        )
        for city in cities
    ]
    if len(data) == 1:
        data = data[0]
    insert_data(conn, query, data, 'city', logger)


def perform_address_filling(conn, car_df, logger):
    logger.info("Starting process of inserting records into tables 'country' and 'city'.")
    # Countries
    countries = [
        Country(
            'United States of America', 'US', 'USA'
        ),
        Country(
            'Canada', 'CA', 'CAN'
        ),
        Country(
            'Mexico', 'MX', 'MEX'
        )
    ]

    insert_into_country_table(conn, countries, logger)

    # Cities
    cities = car_df['city'].unique()
    cities_list = []
    for city in CITY_TO_COUNTRY_DICT.keys():
        city = City(
            name=city, 
            country_name=CITY_TO_COUNTRY_DICT[city]
        )
        cities_list.append(city)

    insert_into_city_table(conn, cities_list, logger)
    logger.info("Process of inserting records into tables 'country' and 'city' ended.")