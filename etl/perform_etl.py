import logging
import json
import os
from datetime import datetime
import time

import numpy as np
import pandas as pd
import psycopg2 as pg2

from config.db_config import get_oltp_test_config, get_olap_test_config, test_db_connection
from config.files_config import METADATA_FILENAME
from config.data_formats import *
from etl_utils.extract import *

from etl_utils.etl import *

    
def main():
    logging_filename = 'logging/etl_logging.log'
    logging.basicConfig(filename=logging_filename, level=logging.INFO)
    oltp_config_dict = get_oltp_test_config()
    olap_config_dict = get_olap_test_config()
    # Record the ETL start time in the log file
    logging.info(f"ETL process started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with open(METADATA_FILENAME) as file:
        metadata = json.load(file)

    initial_data_loading = metadata['current_etl']['initial_data_loading']
    try:
        if initial_data_loading:
            print(f"Initial data loading")
            seller_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading)
            # purchase_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading)
            # repair_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading)
            # sale_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading)
        else:
            # seller_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading)
            # location_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading)
            # purchase_etl(oltp_config_dict, olap_config_dict, metadata, initial_data_loading)
            print(f"Incremental data loading")
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
        metadata['last_etl']['datetime'] = etl_end_datetime
        # metadata['current_etl']['initial_data_loading'] = False

        # Write the updated metadata back to the file
        with open(METADATA_FILENAME, 'w') as file:
            json.dump(metadata, file, indent=4)  # Indent for pretty formatting


if __name__ == "__main__":
    """
    config_dict = get_olap_test_config()
    query = "SELECT * FROM dim_car;"
    test_db_connection(config_dict, query=query, message="Testing connection to database 'car_resale_business_OLAP_coursework'")
    """
    main()


