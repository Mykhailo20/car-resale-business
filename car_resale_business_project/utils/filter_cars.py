def filter_cars(filters, cars_data): 
    filtered_cars = cars_data   
     # Define filters to apply
    filter_functions = {
        'fromDate': lambda car, value: car.get('purchase_date') >= value,
        'toDate': lambda car, value: car.get('purchase_date') <= value
    }

    for filter_name, filter_value in filters.items():
        print(f"filter_name = {filter_name}")
        print(f"filter_value = {filter_value}")
        print(f"filtered_cars before filter = {filtered_cars}")
        if filter_value is None or filter_value == "All":
            continue
        if "Date" in filter_name:
            
            filter_function = filter_functions[filter_name]
            filtered_cars = [car for car in filtered_cars if filter_function(car, filter_value)]
        else:
            filtered_cars = [car for car in filtered_cars if car[filter_name] == filter_value]
        print(f"filtered_cars after filter = {filtered_cars}")
    return filtered_cars
