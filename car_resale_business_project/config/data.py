DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'
TIMESTAMP_PATTERN = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'

classify_condition = lambda condition: (
    'Bad' if 1.0 <= condition < 2.0 else
    'Normal' if 2.0 <= condition < 3.0 else
    'Good' if 3.0 <= condition < 4.0 else
    'Excellent' if 4.0 <= condition <= 5.0 else None
)