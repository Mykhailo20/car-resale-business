def filter_cars(filters, purchases_data): 
    filtered_purchases = purchases_data   
     # Define filters to apply
    filter_functions = {
        'fromDate': lambda purchase, value: purchase.purchase_date >= value,
        'toDate': lambda purchase, value: purchase.purchase_date <= value,
        'seller': lambda purchase, value: purchase.seller.name == value,
        'location': lambda purchase, value: purchase.seller.address.city.name == value
    }

    for filter_name, filter_value in filters.items():
        if filter_value is None or filter_value == "All":
            continue

        filter_function = filter_functions[filter_name]
        filtered_purchases = [purchase for purchase in filtered_purchases if filter_function(purchase, filter_value)]
    
    return filtered_purchases
