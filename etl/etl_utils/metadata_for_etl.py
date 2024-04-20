import logging
import re
import warnings
from datetime import datetime


def check_value(value, restriction, error_code):
    if eval(restriction)(value):
        return value
    exec(error_code)


def calculate_and_check_value(attribute_data, *args):

    calculation_code = attribute_data.get('calculation_code')

    # Not all attributes and metrics have a formula to calculate, but their values should still be checked.
    calculated_value = args[0] if args else None
    if calculation_code != 'NOT SPECIFIED':
        try:
            calculated_value = eval(calculation_code)(*args)
        except Exception as e:
            logging.error(f"Error occurred during calculation {attribute_data['column']}: {e}")
            print(f"Error occurred during calculation {attribute_data['column']}: {e}")
            # Not return, but stop the ETL process - ?
            return
        
    # Check calculated value against value restriction
    value_restriction = attribute_data.get('value_restriction')
    if value_restriction != 'NOT SPECIFIED':
        error_handling = attribute_data.get('error_handling', {})
        
        return check_value(calculated_value, value_restriction, error_handling.get('error_code', ''))
    
    return calculated_value