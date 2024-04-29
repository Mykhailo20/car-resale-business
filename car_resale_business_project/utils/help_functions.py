import csv
import json

import psycopg2 as pg2


def get_file_length(filename):
    with open(filename, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        row_count = 0
        for row in csv_reader:
            row_count += 1

        # The first row contains the record headers
        return row_count - 1
    

def renew_fill_oltp_metadata(filename, last_filling_datetime):
    with open(filename) as file:
        databases_metadata = json.load(file)
    databases_metadata['fill_oltp']['last_filling']['datetime'] = last_filling_datetime
    with open(filename, 'w') as file:
        json.dump(databases_metadata, file, indent=4)


def renew_main_page_metadata(filename, page_name):
    with open(filename) as file:
        databases_metadata = json.load(file)
    databases_metadata['main_page'] = page_name

    with open(filename, 'w') as file:
        json.dump(databases_metadata, file, indent=4)


def check_db_filled(db_config_dict, query):
    db_conn = pg2.connect(database=db_config_dict['database'], user=db_config_dict['user'], password=db_config_dict['password'])
    with db_conn.cursor() as cur:
        cur.execute(query)
        # Fetch the results
        data = cur.fetchall()
    db_conn.close()

    if len(data) > 0:
        return True
    return False
