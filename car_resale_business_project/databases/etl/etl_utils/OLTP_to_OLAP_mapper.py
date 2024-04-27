import logging
from datetime import datetime, date

from car_resale_business_project.databases.classes.OLTP.purchase import Purchase
from car_resale_business_project.databases.classes.OLTP.seller import Seller
from car_resale_business_project.databases.classes.OLTP.car import Car
from car_resale_business_project.databases.classes.OLTP.employee import Employee
from car_resale_business_project.databases.classes.OLTP.address import Address

from car_resale_business_project.databases.classes.OLAP.dimensions import *
from car_resale_business_project.databases.classes.OLAP.facts import *

from car_resale_business_project.databases.etl.etl_utils.metadata_for_etl import calculate_and_check_value
from car_resale_business_project.databases.etl.etl_utils.create_OLTP_class_instances import *


def OLTP_to_OLAP_dim(dim_metadata, dim_attrs_dict):
    res_dict = {}
    dim_attrs = dim_metadata['attributes']
    for attr_name in dim_attrs:
        attr_metadata =  dim_metadata['attributes'][attr_name]
        try:
            attr_value = calculate_and_check_value(attr_metadata, *dim_attrs_dict[attr_name]) if isinstance(dim_attrs_dict[attr_name], (list, tuple, set, dict)) else calculate_and_check_value(attr_metadata, dim_attrs_dict[attr_name])

            res_dict[attr_name] = attr_value
        except Exception as e:
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.error(f"[{current_datetime}] Error occurred during value checking {attr_metadata['column']}: {e}")
            print(f"[{current_datetime}] Error occurred during value checking {attr_metadata['column']}: {e}")
            print("Error handled according to error code.")
    return res_dict


def OLTP_to_OLAP_car(oltp_car: Car, car_metadata: dict):
    attributes_dict = {
        'vin': oltp_car.vin,
        'manufacture_year': oltp_car.manufacture_year,
        'make': oltp_car.manufacturer,
        'model': oltp_car.model,
        'trim': oltp_car.trim,
        'body': oltp_car.body_type,
        'transmission': oltp_car.transmission,
        'color': oltp_car.color
    }
    res_dict = OLTP_to_OLAP_dim(car_metadata, attributes_dict)

    return CarDim(
        vin=res_dict['vin'],
        manufacture_year=res_dict['manufacture_year'],
        make=res_dict['make'],
        model=res_dict['model'],
        trim=res_dict['trim'],
        body_type=res_dict['body'],
        transmission=res_dict['transmission'],
        color=res_dict['color']
    )


def OLTP_to_OLAP_seller(oltp_seller: Seller, seller_metadata: dict):
    attributes_dict = {
        'name': oltp_seller.name,
        'type': oltp_seller.type,
        'oltp_id': oltp_seller.seller_id
    }
    res_dict = OLTP_to_OLAP_dim(seller_metadata, attributes_dict)
    return SellerDim(name=res_dict['name'], type=res_dict['type'], oltp_id=res_dict['oltp_id'])


def OLTP_to_OLAP_employee(oltp_employee: Employee, transaction_date: date, employee_metadata: dict):
    employee_birth_date = oltp_employee.birth_date
    employee_age = transaction_date.year - employee_birth_date.year - ((transaction_date.month, transaction_date.day) < (employee_birth_date.month, employee_birth_date.day))
    attributes_dict = {
        'first_name': oltp_employee.first_name,
        'age': (transaction_date, oltp_employee.birth_date),
        'age_group': employee_age,
        'sex': oltp_employee.sex,
        'salary': oltp_employee.salary,
        'work_experience': (transaction_date, oltp_employee.hire_date),
        'oltp_id': oltp_employee.employee_id
    }
    res_dict = OLTP_to_OLAP_dim(employee_metadata, attributes_dict)
    return EmployeeDim(
        first_name=res_dict['first_name'], age=res_dict['age'], age_group=res_dict['age_group'],
        sex=res_dict['sex'], salary=res_dict['salary'], work_experience=res_dict['work_experience'],
        oltp_id=res_dict['oltp_id']
    )

def OLTP_to_OLAP_buyer_df(df_row, buyer_metadata: dict):
    sale_date = df_row['s_sale_date']
    buyer_birth_date = df_row['b_birth_date']
    buyer_age = sale_date.year - buyer_birth_date.year - ((sale_date.month, sale_date.day) < (buyer_birth_date.month, buyer_birth_date.day))
    attributes_dict = {
        'first_name': df_row['b_first_name'],
        'age': (df_row['s_sale_date'], df_row['b_birth_date']),
        'age_group': buyer_age,
        'sex': df_row['b_sex'],
        'oltp_id': df_row['b_oltp_id']
    }
    res_dict = OLTP_to_OLAP_dim(buyer_metadata, attributes_dict)
    return BuyerDim(
        first_name=res_dict['first_name'],
        age=res_dict['age'],
        age_group=res_dict['age_group'],
        sex=res_dict['sex'],
        oltp_id=res_dict['oltp_id']
    )


def OLTP_to_OLAP_location(oltp_address: Address, location_metadata: dict):
    attributes_dict = {
        'country': oltp_address.country,
        'city': oltp_address.city,
        'oltp_id': oltp_address.address_id
    }
    res_dict = OLTP_to_OLAP_dim(location_metadata, attributes_dict)
    return LocationDim(country=res_dict['country'], city=res_dict['city'], oltp_id=res_dict['oltp_id'])


def OLTP_to_OLAP_date(df_row, prefix: str, fact_name: str, date_metadata: dict):
    attributes_dict = {
        'date': df_row[f'{prefix}_date'],
        'year': df_row[f'{prefix}_date'],
        'month': df_row[f'{prefix}_date'],
        'day': df_row[f'{prefix}_date'],
        'week_day': df_row[f'{prefix}_date'],
        'oltp_id': df_row[f'c_vin'],
        'fact_name': fact_name
    }
    res_dict = OLTP_to_OLAP_dim(date_metadata, attributes_dict)
    return DateDim(
        date=res_dict['date'],
        year=res_dict['year'],
        month=res_dict['month'],
        day=res_dict['day'],
        week_day=res_dict['week_day'],
        oltp_id=res_dict['oltp_id'],
        fact_name=res_dict['fact_name']
    )


def OLTP_to_OLAP_repair_type(df_row, car_repair_type_metadata, prefix='c'):
    attributes_dict = {
        'repair_type': df_row[f'{prefix}_repair_type']
    }
    res_dict = OLTP_to_OLAP_dim(car_repair_type_metadata, attributes_dict)
    return CarRepairTypeDim(repair_type=res_dict['repair_type'])



def OLTP_to_OLAP_purchase_df(df_row, metadata: dict):
    car_obj = create_car(df_row)
    dim_car_obj = OLTP_to_OLAP_car(car_obj, metadata['dimensions']['dim_car'])
    employee_obj = create_employee(df_row)
    dim_employee_obj = OLTP_to_OLAP_employee(employee_obj, transaction_date=df_row['p_purchase_date'], employee_metadata=metadata['dimensions']['dim_employee'])
    dim_date_obj = OLTP_to_OLAP_date(df_row, prefix='p_purchase', fact_name='purchase', date_metadata=metadata['dimensions']['dim_date'])

    purchase_metadata = metadata['facts']['fact_car_purchase'] 
    # Calculate metric values
    metrics_dict = {
        'price': df_row['p_price'], 'car_years': (df_row['p_purchase_date'].year, df_row['c_manufacture_year']), 'odometer': df_row['p_odometer'],
        'condition': df_row['p_condition'], 'employee_experience': (df_row['p_purchase_date'], df_row['e_hire_date'])
    }
    if df_row['p_purchase_date'].year < df_row['c_manufacture_year']:
        print(f"metrics_dict = {metrics_dict}")

    res_metrics_dict = {}
    for metric_name in metrics_dict.keys():
        metric_metadata =  purchase_metadata['metrics'][metric_name]
        try:
            fact_purchase_metric_value = calculate_and_check_value(metric_metadata, *metrics_dict[metric_name]) if isinstance(metrics_dict[metric_name], (list, tuple, set, dict)) else calculate_and_check_value(metric_metadata, metrics_dict[metric_name])
            
            res_metrics_dict[metric_name] = fact_purchase_metric_value
        except Exception as e:
            logging.error(f"Error occurred during value checking {metric_metadata['column']}: {e}")
            print(f"Error occurred during value checking {metric_metadata['column']}: {e}")
            print("Error handled according to error code.")

    return CarPurchaseFact(
        car_dim=dim_car_obj,
        seller_id=df_row['s_id'],
        employee_dim=dim_employee_obj,
        location_id=df_row['p_address_id'],
        date_dim=dim_date_obj,
        price=res_metrics_dict['price'],
        car_years=res_metrics_dict['car_years'],
        odometer=res_metrics_dict['odometer'],
        condition=res_metrics_dict['condition'],
        employee_experience=res_metrics_dict['employee_experience']
    )


def OLTP_to_OLAP_repair_df(df_row, metadata: dict):
    employee_obj = create_employee(df_row)
    dim_employee_obj = OLTP_to_OLAP_employee(employee_obj, transaction_date=df_row['r_repair_date'], employee_metadata=metadata['dimensions']['dim_employee'])
    address_obj = create_address(df_row, prefix='r')
    dim_location_obj = OLTP_to_OLAP_location(address_obj, location_metadata=metadata['dimensions']['dim_location'])
    dim_date_obj = OLTP_to_OLAP_date(df_row, prefix='r_repair', fact_name='repair', date_metadata=metadata['dimensions']['dim_date'])
    dim_car_repair_type_obj = OLTP_to_OLAP_repair_type(df_row, car_repair_type_metadata=metadata['dimensions']['dim_car_repair_type'], prefix='r')

    repair_metadata = metadata['facts']['fact_car_repair'] 
    # Calculate metric values
    metrics_dict = {
        'cost': df_row['r_cost'], 
        'condition_delta': (df_row['r_condition'], df_row['p_condition']),
        'oltp_id': df_row['r_oltp_id']
    }

    res_metrics_dict = {}
    for metric_name in metrics_dict.keys():
        metric_metadata =  repair_metadata['metrics'][metric_name]
        try:
            fact_repair_metric_value = calculate_and_check_value(metric_metadata, *metrics_dict[metric_name]) if isinstance(metrics_dict[metric_name], (list, tuple, set, dict)) else calculate_and_check_value(metric_metadata, metrics_dict[metric_name])
            
            res_metrics_dict[metric_name] = fact_repair_metric_value
        except Exception as e:
            logging.error(f"Error occurred during value checking {metric_metadata['column']} (fact_car_repair): {e}")
            print(f"Error occurred during value checking {metric_metadata['column']} (fact_car_repair): {e}")
            print("Error handled according to error code.")

    return CarRepairFact(
        car_vin=df_row['c_vin'],
        employee_dim=dim_employee_obj,
        location_dim=dim_location_obj,
        date_dim=dim_date_obj,
        car_repair_type_dim=dim_car_repair_type_obj,
        cost=res_metrics_dict['cost'],
        condition_delta=res_metrics_dict['condition_delta'],
        oltp_id=res_metrics_dict['oltp_id']
    )


def OLTP_to_OLAP_sale_df(df_row, metadata: dict):
    dim_buyer_obj = OLTP_to_OLAP_buyer_df(df_row, buyer_metadata=metadata['dimensions']['dim_buyer'])

    employee_obj = create_employee(df_row)
    dim_employee_obj = OLTP_to_OLAP_employee(employee_obj, transaction_date=df_row['s_sale_date'], employee_metadata=metadata['dimensions']['dim_employee'])

    address_obj = create_address(df_row, prefix='s')
    dim_location_obj = OLTP_to_OLAP_location(address_obj, location_metadata=metadata['dimensions']['dim_location'])

    dim_date_obj = OLTP_to_OLAP_date(df_row, prefix='s_sale', fact_name='sale', date_metadata=metadata['dimensions']['dim_date'])

    sale_metadata = metadata['facts']['fact_car_sale'] 
    gross_profit_amount =  df_row['s_price'] - (df_row['p_price'] + df_row['r_cost'])

    # Calculate metric values
    metrics_dict = {
        'price': df_row['s_price'], 
        'gross_profit_amount': (df_row['p_price'], df_row['s_price'], df_row['r_cost']),
        'gross_profit_percentage': (gross_profit_amount, df_row['s_price']),
        'mmr': df_row['s_mmr'],
        'price_margin': (df_row['s_price'], df_row['s_mmr']),
        'car_years': (df_row['s_sale_date'].year, df_row['c_manufacture_year']), 
        'odometer': df_row['s_odometer'],
        'condition': df_row['s_condition'], 
        'employee_experience': (df_row['s_sale_date'], df_row['e_hire_date']),
        'service_time': (df_row['s_sale_date'], df_row['p_purchase_date']),
        'service_cost': (df_row['p_price'], df_row['r_cost'])
    }
    if df_row['p_purchase_date'].year < df_row['c_manufacture_year']:
        print(f"metrics_dict = {metrics_dict}")

    res_metrics_dict = {}
    for metric_name in metrics_dict.keys():
        metric_metadata =  sale_metadata['metrics'][metric_name]
        try:
            fact_purchase_metric_value = calculate_and_check_value(metric_metadata, *metrics_dict[metric_name]) if isinstance(metrics_dict[metric_name], (list, tuple, set, dict)) else calculate_and_check_value(metric_metadata, metrics_dict[metric_name])
            
            res_metrics_dict[metric_name] = fact_purchase_metric_value
        except Exception as e:
            logging.error(f"Error occurred during value checking {metric_metadata['column']}: {e}")
            print(f"Error occurred during value checking {metric_metadata['column']}: {e}")
            print("Error handled according to error code.")

    return CarSaleFact(
        car_vin=df_row['c_vin'],
        buyer_dim=dim_buyer_obj,
        employee_dim=dim_employee_obj,
        location_dim=dim_location_obj,
        date_dim=dim_date_obj,
        price=res_metrics_dict['price'],
        gross_profit_amount=res_metrics_dict['gross_profit_amount'],
        gross_profit_percentage=res_metrics_dict['gross_profit_percentage'],
        mmr=res_metrics_dict['mmr'],
        price_margin=res_metrics_dict['price_margin'],
        car_years=res_metrics_dict['car_years'],
        odometer=res_metrics_dict['odometer'],
        condition=res_metrics_dict['condition'],
        employee_experience=res_metrics_dict['employee_experience'],
        service_time=res_metrics_dict['service_time'],
        service_cost=res_metrics_dict['service_cost']
    )