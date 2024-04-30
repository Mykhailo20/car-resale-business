import random
import typing

from car_resale_business_project.databases.classes.OLTP.employee import *
from car_resale_business_project.databases.classes.OLTP.buyer import *


def generate_random_employee(faker, detector, logger, employee_hire_date_range, employee_salary_range, encountered_names:set, position='Manager'):
    
    # Generate random date of birth between 18 and 45 years ago
    birth_date = faker.date_of_birth(minimum_age=28, maximum_age=55)
    
    # Generate random first and last names
    first_name = faker.first_name()
    last_name = faker.last_name()
    
    while first_name + ' ' + last_name in encountered_names:
        logger.warning(f"Random Employee Generation: the generated employee name = {first_name + ' ' + last_name} have already met before, therefore, to ensure the correctness of the program's operation, repeated random generation of the employee's first and last name was carried out.")
        print(f"Random Employee Generation: the generated employee name = {first_name + ' ' + last_name} have already met before, therefore, to ensure the correctness of the program's operation, repeated random generation of the employee's first and last name was carried out.")
        first_name = faker.first_name()
        last_name = faker.last_name()

    encountered_names.add(first_name + ' ' + last_name)
    # Determine sex based on first name
    sex = detector.get_gender(first_name)
    
    # Convert gender to 'M' or 'F'
    sex = 'M' if sex in ['male', 'mostly_male', 'andy'] else 'F'
    
    # Generate random middle name
    middle_name = faker.first_name() if sex == 'F' else faker.first_name_male()
    
    # Generate a random hire date within the specified range
    hire_date = faker.date_between(start_date=employee_hire_date_range[0], end_date=employee_hire_date_range[1])
    
    salary = faker.random_int(employee_salary_range[0], employee_salary_range[1])
    
    employee = Employee(
        employee_id=None,
        first_name=first_name, last_name=last_name, middle_name=middle_name,
        birth_date=birth_date, sex=sex, email=f"{first_name.lower()}.{last_name.lower()}@gmail.com", 
        position=position, salary=salary, hire_date=hire_date
    )
    return employee, encountered_names


def generate_random_buyer(faker, detector, city):
    
    # Generate random date of birth between 16 and 45 years ago
    birth_date = faker.date_of_birth(minimum_age=26, maximum_age=55)
    
    # Generate random first and last names
    first_name = faker.first_name()
    last_name = faker.last_name()
    
    # Determine sex based on first name
    sex = detector.get_gender(first_name)
    
    # Convert gender to 'M' or 'F'
    sex = 'male' if sex in ['male', 'mostly_male', 'andy'] else 'female'
    
    # Generate random middle name
    middle_name = faker.first_name() if sex == 'female' else faker.first_name_male()
    
    # Generate fake address
    street = faker.street_address()
    postal_code = faker.zipcode()
    
    # Create Address and Buyer instances
    address = Address(address_id=None, country=None, city=city, street=street, postal_code=postal_code)
    buyer = Buyer(buyer_id=None, first_name=first_name, last_name=last_name, middle_name=middle_name,
                  birth_date=birth_date, sex=sex, email=f"{first_name.lower()}.{last_name.lower()}@gmail.com", address=address)
    return buyer


def generate_random_price(min_value, max_value):
    # Generate a random integer in the specified range
    random_integer = random.randint(min_value, max_value)
    
    # Round up to the nearest multiple of 50
    result = round(random_integer / 50) * 50
    
    return result

def select_new_random_value(current_value, values_list):
    # Exclude the current color from the colors list
    remaining_values = [value for value in values_list if value != current_value]
    # Pick a random color from the remaining colors
    new_value = random.choice(remaining_values)
    return new_value