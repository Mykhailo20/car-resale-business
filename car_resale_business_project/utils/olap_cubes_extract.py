import json
import logging
import csv

import psycopg2 as pg2

from car_resale_business_project.config.files_config import CUBES_EXPORT_LOGGING_FILENAME

def cubes_extract_configure_logging():
    cubes_export_logger = logging.getLogger('oltp')
    cubes_export_logger.setLevel(logging.DEBUG)
    cubes_export_handler = logging.FileHandler(CUBES_EXPORT_LOGGING_FILENAME)
    cubes_export_handler.setLevel(logging.DEBUG)
    cubes_export_formatter = logging.Formatter('[%(asctime)s] - %(levelname)s: %(message)s')
    cubes_export_handler.setFormatter(cubes_export_formatter)
    cubes_export_logger.addHandler(cubes_export_handler)
    return cubes_export_logger


def check_filename(filename: str):
    # Check if filename already contains an extension
    if '.' in filename:
        # Split the filename based on the period ('.')
        parts = filename.split('.')
        # Check if the last part is an extension
        if len(parts) > 2:  # Assuming extensions are no longer than 4 characters
            raise ValueError(f"Invalid filename: {filename}")
            
        filename = parts[0]

    return filename

def get_min_max_date(config_dict):
    conn = pg2.connect(database=config_dict['database'], user=config_dict['user'], password=config_dict['password'])

    # View some data from db
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT 
	                    MIN(date) AS min_date,
	                    MAX(date) AS max_date
                    FROM 
                        dim_date;
                    """)
        data = cur.fetchall()
    min_date = data[0][0]
    max_date = data[0][1]
    conn.close()
    return min_date, max_date
    

def parse_request_data(request_data: dict):
    # file
    filename = request_data['export_file_name']
    file_extension = request_data['export_file_extention']
    filename = check_filename(filename=filename)
    filename = filename + '.' + file_extension

    # date filter
    date_filter_dict = {
        "filter-date-from": request_data.get('filter-date-from', None), 
        "filter-date-to": request_data.get('filter-date-to', None), 
    }

    # fact table
    fact_tablename = request_data['cube_name']

    metrics_list = []
    dim_dict = {}

    for key, value in request_data.items():
        print(f"key = {key}; value={value}")
        if 'level' in key:  # Levels will be found for each dimension below
            continue

        # Check if the key corresponds to a metric
        if 'metric' in key and value == 'on':
            metric_name = key.replace('metric_', '')  # Remove the 'metric_' prefix
            metrics_list.append(metric_name)
        
        # Check if the key corresponds to a dimension and its hierarchy level
        if key.startswith('dim_'):
            if value != 'on':
                continue
            
            dimension = key
            # Find the corresponding hierarchy level
            level_key = f'level-{dimension}'
            print(f"level_key = {level_key}")
            if level_key in request_data.keys():
                dim_dict[dimension] = request_data[level_key]  # Assuming only one hierarchy level for simplicity

    return filename, file_extension, date_filter_dict, fact_tablename, metrics_list, dim_dict


def create_cube_extract_query(fact_tablename, date_filter_dict, metrics_list, dim_dict, metadata_filename):
    print(f"create cube extract query")
    with open(metadata_filename) as file:
        cubes_metadata = json.load(file)
    cube_metadata = cubes_metadata["facts"][fact_tablename]

    # SELECT PART
    column_names = []
    select_part = 'SELECT '
    select_columns = []             # will be used for group by
    dimensions = []
    for dim in dim_dict.keys():
        dimensions.append(dim)
        dim_hierarchies_list = dim_dict[dim].split(',')
        dim_hierarchies_list = dim_hierarchies_list[1:] # 0-th element = name of entity
        for hierarchy in dim_hierarchies_list: 
            full_select_column_name = dim + '.' + hierarchy
            select_columns.append(full_select_column_name)

            select_column_name_alias = dim + '_' + hierarchy
            column_names.append(select_column_name_alias)
            
            select_part += f"\n    {full_select_column_name} AS {select_column_name_alias}, "
    
    for metric in metrics_list:
        metric_aggr_func = cube_metadata['metrics'][metric]['aggregation_function']
        full_select_column_name_command = metric_aggr_func + '(' + fact_tablename + '.' + metric + ')' # SUM(fact_car_sale.price)
        # select_columns_commands.append(full_select_column_name_command)

        select_column_name_alias = metric + '_' + metric_aggr_func.lower() # for example gross_profit_amount_sum
        column_names.append(select_column_name_alias)

        select_part += f"\n    {full_select_column_name_command} AS {select_column_name_alias},"

    select_part = select_part[:-1]  # remove the last comma
    select_part += f"\n FROM {fact_tablename} "
    print(f"select_part = {select_part}")

    # JOIN part
    fact_dimension_keys = cube_metadata['dimensions_key_fields']
    join_part = ''
    for dim in dimensions:
        join_fact_key = fact_dimension_keys[dim]['column']
        join_dim_key = fact_dimension_keys[dim]['dimension_key_column']
        join_part += f"\n JOIN {dim} ON {fact_tablename}.{join_fact_key} = {dim}.{join_dim_key} "

    
    where_part = None

    # LIMIT by dim_date
    if (date_filter_dict['filter-date-from']) or (date_filter_dict['filter-date-to']):
        if 'dim_date' not in dimensions:
            dim = 'dim_date'
            join_fact_key = fact_dimension_keys[dim]['column']
            join_dim_key = fact_dimension_keys[dim]['dimension_key_column']
            join_part += f"\n JOIN {dim} ON {fact_tablename}.{join_fact_key} = {dim}.{join_dim_key} "

        if (date_filter_dict['filter-date-from']) and (date_filter_dict['filter-date-to']):
            where_part = "\n WHERE dim_date.date BETWEEN '{}' AND '{}'".format(date_filter_dict['filter-date-from'], date_filter_dict['filter-date-to'])
        elif (date_filter_dict['filter-date-from']) and (date_filter_dict['filter-date-to'] == ''):
            where_part = "\n WHERE dim_date.date >= '{}'".format(date_filter_dict['filter-date-from'])
        elif (date_filter_dict['filter-date-from'] == '') and (date_filter_dict['filter-date-to']):
            where_part = "\n WHERE dim_date.date <= '{}'".format(date_filter_dict['filter-date-to'])

    print(f"join_part = {join_part}")

    if where_part:
        print(f"where_part = {where_part}")

    group_by_part = '\n GROUP BY ' + ', '.join(select_columns) + ';'
    print(f"group_by_part = {group_by_part}")

    query = select_part + join_part + group_by_part
    if where_part is not None:
        query = select_part + join_part + where_part + group_by_part

    return query, column_names

def get_data_from_db(config_dict, query):
    conn = pg2.connect(database=config_dict['database'], user=config_dict['user'], password=config_dict['password'])

    # View some data from db
    with conn.cursor() as cur:
        cur.execute(query)
        data = cur.fetchall()
    conn.close()
    return data


def save_to_csv(filename, data, column_names):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)  # Write header
        writer.writerows(data)  # Write data


def save_to_json(filename, data, column_names):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)