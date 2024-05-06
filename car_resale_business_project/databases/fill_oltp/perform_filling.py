import logging
import os
import psycopg2 as pg2

from car_resale_business_project.config.files_config import FILL_OLTP_LOGGING_FILENAME, FILL_OLTP_DATA_FILENAME
from car_resale_business_project.config.db_config import get_oltp_etl_test_config, get_olap_etl_test_config, get_oltp_fill_demonstration_config, get_olap_fill_demonstration_config
from car_resale_business_project.databases.fill_oltp.utils.data_preparation.car_df_preparation import *
from car_resale_business_project.databases.fill_oltp.utils.data_insertion.general_functions import get_db_enum_values
from car_resale_business_project.databases.fill_oltp.utils.data_insertion.address_insertion import *
from car_resale_business_project.databases.fill_oltp.utils.data_insertion.person_insertion import *
from car_resale_business_project.databases.fill_oltp.utils.data_insertion.car_insertion import *
from car_resale_business_project.databases.fill_oltp.utils.data_insertion.facts_insertion import *


def configure_logging():

    # Check if the log file exists, create it if it doesn't
    if not os.path.exists(FILL_OLTP_LOGGING_FILENAME):
        open(FILL_OLTP_LOGGING_FILENAME, 'w').close()
        
    oltp_logger = logging.getLogger('oltp')
    oltp_logger.setLevel(logging.DEBUG)
    oltp_handler = logging.FileHandler(FILL_OLTP_LOGGING_FILENAME)
    oltp_handler.setLevel(logging.DEBUG)
    oltp_formatter = logging.Formatter('[%(asctime)s] - %(levelname)s: %(message)s')
    oltp_handler.setFormatter(oltp_formatter)
    oltp_logger.addHandler(oltp_handler)

    return oltp_logger


def perform_oltp_filling(samples_no):
    oltp_logger = configure_logging()
    car_df = prepare_car_df(FILL_OLTP_DATA_FILENAME, samples_no, oltp_logger)
    print(f"len(car_df) = {len(car_df)}")

    oltp_config_dict = get_oltp_fill_demonstration_config()
    oltp_db_conn = pg2.connect(database=oltp_config_dict['database'], user=oltp_config_dict['user'], password=oltp_config_dict['password'])

    oltp_logger.info(f"Starting process of filling OLTP DB {oltp_config_dict['database']}.\n Number of records to insert into 'car' table = {len(car_df)}")
    perform_address_filling(oltp_db_conn, car_df, oltp_logger)
    car_buyer_employees_list, car_mechanic_employees_list, car_seller_employees_list = perform_bussiness_participants_filling(oltp_db_conn, car_df, oltp_logger)
    perform_car_tables_filling(oltp_db_conn, car_df, oltp_logger)
    perform_facts_filling(oltp_db_conn, car_df, oltp_logger, car_buyer_employees_list, car_mechanic_employees_list, car_seller_employees_list)
    oltp_logger.info(f"Process of filling OLTP DB {oltp_config_dict['database']} ended.\n\n\n")

    oltp_db_conn.close()
