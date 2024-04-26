from car_resale_business_project.databases.classes.OLTP.car import Car
from car_resale_business_project.databases.classes.OLTP.address import Address
from car_resale_business_project.databases.classes.OLTP.employee import Employee
from car_resale_business_project.databases.classes.OLTP.seller import Seller
from car_resale_business_project.databases.classes.OLTP.buyer import Buyer
from car_resale_business_project.databases.classes.OLTP.purchase import Purchase
from car_resale_business_project.databases.classes.OLTP.repair import Repair
from car_resale_business_project.databases.classes.OLTP.sale import Sale


# Define functions to create instances of Car, Seller, Employee, and Address classes
def create_car(row):
    return Car(
        vin=row['c_vin'],
        manufacture_year=row['c_manufacture_year'],
        manufacturer=row['c_make_name'],
        model=row['c_model'],
        trim=row['c_trim'],
        body_type=row['c_cbt_name'],
        transmission=row['c_transmission'],
        color=row['c_color_name']
    )


def create_address(row, prefix):
    return Address(
        address_id=row[f'{prefix}_addr_oltp_id'],
        country=row[f'{prefix}_country'],
        city=row[f'{prefix}_city'],
        street=row[f'{prefix}_street'],
        postal_code=row[f'{prefix}_postal_code']
    )


def create_seller(row):
    address = create_address(row, prefix='s')
    return Seller(
        seller_id=row['s_oltp_id'],
        name=row['s_name'],
        type=row['s_type'],
        address=address
    )


def create_employee(row):
    return Employee(
        employee_id=row['e_oltp_id'],
        first_name=row['e_first_name'],
        last_name=row['e_last_name'],
        middle_name=row['e_middle_name'],
        birth_date=row['e_birth_date'],
        sex=row['e_sex'],
        email=row['e_email'],
        position=row['e_position'],
        salary=row['e_salary'],
        hire_date=row['e_hire_date']
    )


def create_buyer(row):
    address = create_address(row, prefix='b')
    return Buyer(
        first_name=row['b_first_name'],
        last_name=row['b_last_name'],
        middle_name=row['b_middle_name'],
        birth_date=row['b_birth_date'],
        sex=row['b_sex'],
        email=row['b_email'],
        address=address
    )


# Create instances of the Purchase class from the DataFrame data
def create_purchase(row, car=None):
    if car is None:
        car = create_car(row)
    employee = create_employee(row)
    purchase = Purchase(
        car=car,
        seller_id=row['s_id'],
        address_id=row['p_address_id'],
        employee=employee,
        price=row['p_price'],
        odometer=row['p_odometer'],
        condition=row['p_condition'],
        description=None,
        car_image=None,
        car_image_content_type=None,
        purchase_date=row['p_date']
    )
    return purchase


# Create instances of the Repair class from the DataFrame data
def create_repair(row, car=None):
    if car is None:
        car = create_car(row)
    employee = create_employee(row)
    address = create_address(row, prefix='r')
    repair = Repair(
        car=car,
        employee=employee,
        address=address,
        repair_type=row['r_type'],
        cost=row['r_cost'],
        condition=row['r_condition'],
        description=None,
        repair_date=row['r_date']
    )
    return repair


# Create instances of the Purchase class from the DataFrame data
def create_sale(row, car=None):
    if car is None:
        car = create_car(row)
    buyer=create_buyer(row)
    employee = create_employee(row)
    sale = Sale(
        car=car,
        buyer=buyer,
        employee=employee,
        mmr=row['s_mmr'],
        price=row['s_price'],
        odometer=row['s_odometer'],
        condition=row['s_condition'],
        description=None,
        car_image=None,
        car_image_content_type=None,
        sale_date=row['s_date']
    )
    return sale