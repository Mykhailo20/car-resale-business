DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'
TIMESTAMP_PATTERN = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'

MIN_CAR_SALE_PRICE = 4000
FILL_OLTP_BATCH_SIZE = 1000
FILL_OLTP_CAR_CITY_CHANGE_FREQUENCY = 50
FILL_OLTP_CAR_REPAIR_FREQUENCY = 10

CAR_RELATIVE_CONDITION_DICT = lambda condition: (
    'Bad' if 1.0 <= condition < 2.0 else
    'Normal' if 2.0 <= condition < 3.0 else
    'Good' if 3.0 <= condition < 4.0 else
    'Excellent' if 4.0 <= condition <= 5.0 else None
)

CITY_TO_COUNTRY_DICT = {
    'Sacramento': 'United States of America',
    'Austin': 'United States of America',
    'Saint Paul': 'United States of America',
    'Phoenix': 'United States of America',
    'Madison': 'United States of America',
    'Nashville': 'United States of America',
    'Annapolis': 'United States of America',
    'Harrisburg': 'United States of America',
    'Tallahassee': 'United States of America',
    'Lincoln': 'United States of America',
    'Columbus': 'United States of America',
    'Lansing': 'United States of America',
    'Trenton': 'United States of America',
    'Richmond': 'United States of America',
    'Columbia': 'United States of America',
    'Indianapolis': 'United States of America',
    'Springfield': 'United States of America',
    'Denver': 'United States of America',
    'Salt Lake City': 'United States of America',
    'Jefferson City': 'United States of America',
    'Atlanta': 'United States of America',
    'Carson City': 'United States of America',
    'Boston': 'United States of America',
    'San Juan': 'United States of America',
    'Raleigh': 'United States of America',
    'Albany': 'United States of America',
    'Salem': 'United States of America',
    'Baton Rouge': 'United States of America',
    'Olympia': 'United States of America',
    'Honolulu': 'United States of America',
    'Oklahoma City': 'United States of America',
    'Jackson': 'United States of America',
    'Santa Fe': 'United States of America',
    'Montgomery': 'United States of America'
}

SELLER_TYPE_DICT = {
    'car_manufacturing_company': ['motors', 'manufacturing', 'inc'],
    'financial_institution': ['financial', 'services', 'bank'],
    'car_rental_company': ['rental', 'enterprise', 'hertz', 'avis'],
    'dealership': ['auto sales', 'dealer', 'group'],
    'individual': ['individual']
}
