import logging
import json
import os
from datetime import datetime
import time

import numpy as np
import pandas as pd
import psycopg2 as pg2

from car_resale_business_project.config.db_config import get_oltp_etl_test_config, get_olap_etl_test_config
from car_resale_business_project.config.files_config import OLAP_METADATA_FILENAME, ETL_FILENAME
from car_resale_business_project.config.data_formats import *
from car_resale_business_project.databases.etl.etl_utils.extract import *

from car_resale_business_project.databases.etl.etl_utils.entities_etl import *

    
def perform_etl():
    logging_filename = 'car_resale_business_project/logging/etl_logging.log'
    logging.basicConfig(filename=logging_filename, level=logging.INFO)
    oltp_config_dict = get_oltp_etl_test_config()
    olap_config_dict = get_olap_etl_test_config()
    # Record the ETL start time in the log file
    logging.info(f"ETL process started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with open(OLAP_METADATA_FILENAME) as file:
        olap_metadata = json.load(file)

    with open(ETL_FILENAME) as file:
        etl_metadata = json.load(file)

    initial_data_loading = etl_metadata['current_etl']['initial_data_loading']
    last_etl_datetime=etl_metadata['last_etl']['datetime']

    try:
        if initial_data_loading:
            print(f"Initial data loading")
            car_repair_type_etl(oltp_config_dict, olap_config_dict, olap_metadata, initial_data_loading, last_etl_datetime)
            seller_etl(oltp_config_dict, olap_config_dict, olap_metadata, initial_data_loading, last_etl_datetime)
            purchase_etl(oltp_config_dict, olap_config_dict, olap_metadata, initial_data_loading, last_etl_datetime)
            repair_etl(oltp_config_dict, olap_config_dict, olap_metadata, initial_data_loading, last_etl_datetime)
            sale_etl(oltp_config_dict, olap_config_dict, olap_metadata, initial_data_loading, last_etl_datetime)
        else:
            print(f"Incremental data loading")
            seller_etl(oltp_config_dict, olap_config_dict, olap_metadata, initial_data_loading, last_etl_datetime)
            location_etl(oltp_config_dict, olap_config_dict, olap_metadata, initial_data_loading, last_etl_datetime)
            purchase_etl(oltp_config_dict, olap_config_dict, olap_metadata, initial_data_loading, last_etl_datetime)
            repair_etl(oltp_config_dict, olap_config_dict, olap_metadata, initial_data_loading, last_etl_datetime)
            sale_etl(oltp_config_dict, olap_config_dict, olap_metadata, initial_data_loading, last_etl_datetime)
    except ValueError as e:
        print("A ValueError occurred during the ETL process.")
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Record the ETL end time in the log file
        etl_end_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"ETL process ended at: {etl_end_datetime}")

        # Update the last_etl.datetime field
        etl_metadata['last_etl']['datetime'] = etl_end_datetime
        # metadata['current_etl']['initial_data_loading'] = False

        # Write the updated metadata back to the file
        with open(ETL_FILENAME, 'w') as file:
            json.dump(etl_metadata, file, indent=4)  # Indent for pretty formatting


if __name__ == "__main__":
    perform_etl()


