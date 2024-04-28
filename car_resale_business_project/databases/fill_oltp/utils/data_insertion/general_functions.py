import re
from random import choice

import pandas as pd

import psycopg2 as pg2


def insert_data(conn, query, data, table_name, logger):
    num_records_inserted = 1
    try:
        with conn.cursor() as cur:
            if isinstance(data, list):
                cur.executemany(query, data)
                num_records_inserted = len(data)
            else:
                cur.execute(query, data)
                
            conn.commit()
            logger.info(f"{num_records_inserted} record(s) successfully inserted into table '{table_name}'!")
            print(f"{num_records_inserted} record(s) successfully inserted into table '{table_name}'!")
            
    except (Exception, pg2.DatabaseError) as error:
        logger.error(f"Error inserting data into table '{table_name}': {error}")
        print(f"Error inserting data into table '{table_name}':", error)
        conn.rollback()


def get_seller_type(seller_name, type_dict):
    for seller_type, patterns in type_dict.items():
        for pattern in patterns:
            if re.search(pattern, seller_name.lower()):
                return seller_type
                
    return choice(list(type_dict.keys())[:-1])


def create_employee_df(employees_list):
    employees_data = {
        'first_name': [employee.first_name for employee in employees_list],
        'last_name': [employee.last_name for employee in employees_list],
        'middle_name': [employee.middle_name for employee in employees_list],
        'birth_date': [employee.birth_date for employee in employees_list],
        'sex': [employee.sex for employee in employees_list],
        'email': [employee.email for employee in employees_list],
        'position': [employee.position for employee in employees_list],
        'salary': [employee.salary for employee in employees_list],
        'hire_date': [employee.hire_date for employee in employees_list]
    }

    # Create DataFrame
    employees_df = pd.DataFrame(employees_data)
    return employees_df


def get_db_enum_values(conn, enum_name):
    with conn.cursor() as cur:
        # Execute the query to get the enum values
        cur.execute("SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = %s)", (enum_name, ))
        enum_values = cur.fetchall()
    
    enum_values = [row[0] for row in enum_values]
    return enum_values


def get_employee_obj(car_employees_list,  df_employee_row):
    for buyer in car_employees_list:
        if (buyer.first_name == df_employee_row.first_name.item() and
            buyer.last_name == df_employee_row.last_name.item() and
            buyer.middle_name == df_employee_row.middle_name.item() and
            buyer.birth_date == df_employee_row.birth_date.item() and
            buyer.sex == df_employee_row.sex.item() and
            buyer.email == df_employee_row.email.item() and
            buyer.position == df_employee_row.position.item() and
            buyer.salary == df_employee_row.salary.item() and
            buyer.hire_date == df_employee_row.hire_date.item()):
            
            matching_buyer = buyer
            break
    return matching_buyer