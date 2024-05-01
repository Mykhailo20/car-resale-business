import typing

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


def parse_request_data(request_data: dict):
    # file
    filename = request_data['export_file_name']
    file_extension = request_data['export_file_extention']
    filename = check_filename(filename=filename)
    filename = filename + '.' + file_extension

    # date filter
    date_filter_list = [request_data.get('filter-date-from', None), request_data.get('filter-date-to', None)]

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

    return filename, date_filter_list, fact_tablename, metrics_list, dim_dict
    