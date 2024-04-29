from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from sqlalchemy import desc

from car_resale_business_project import db
from car_resale_business_project.cars.forms import SearchByVinForm, SearchByFiltersForm
from car_resale_business_project.cars.utils.filters import *
from car_resale_business_project.models import Car, CarMake, Seller, Purchase, Sale, Repair
from car_resale_business_project.config.data_config import CAR_RELATIVE_CONDITION_DICT
from car_resale_business_project.config.website_config import CAR_CARDS_PER_PAGE

cars = Blueprint("cars", __name__, template_folder="templates", static_folder="static")

@cars.route('/<vin>')
def car_page(vin):
    # Query the database to retrieve car details
    car = Car.query.filter_by(vin=vin).first()
    
    # Query the database to retrieve purchase details
    purchase = Purchase.query.filter_by(car_vin=vin).first()
    
    # Query the database to retrieve sale details
    sale = Sale.query.filter_by(car_vin=vin).first()

    # Query the database to retrieve repair details
    repairs = Repair.query.filter_by(car_vin=vin).order_by(Repair.repair_date).all()

    # Initialize the list to store condition deltas
    repairs_condition_delta_list = []
    relative_conditions_list = [CAR_RELATIVE_CONDITION_DICT(purchase.condition)]
    if sale is not None:
        relative_conditions_list.append(CAR_RELATIVE_CONDITION_DICT(sale.condition)) # because we don't know how many repairs
        
    repairs_cost = 0
    car_condition = purchase.condition
    car_rel_condition = CAR_RELATIVE_CONDITION_DICT(purchase.condition)

    # Iterate through repairs to calculate condition deltas
    for i, repair in enumerate(repairs):
        if i == 0:  # First repair
            condition_delta = repair.condition - purchase.condition
        else:
            previous_repair = repairs[i - 1]
            condition_delta = previous_repair.condition - repair.condition

        repairs_cost += repair.cost
        car_condition = repair.condition
        # Append the condition delta to the list
        repairs_condition_delta_list.append(condition_delta)
        repair_rel_condition = CAR_RELATIVE_CONDITION_DICT(repair.condition)
        car_rel_condition = repair_rel_condition 
        relative_conditions_list.append(repair_rel_condition)
    
    gross_profit_amount = None
    if sale is not None:
        gross_profit_amount = sale.price - purchase.price - repairs_cost

    print(f"repairs_condition_delta_list = {repairs_condition_delta_list}")
    return render_template('car_page.html', car=car, purchase=purchase, repairs=repairs, repairs_condition_delta_list=repairs_condition_delta_list, relative_conditions_list=relative_conditions_list, car_condition=car_condition, car_rel_condition=car_rel_condition, sale=sale, gross_profit_amount=gross_profit_amount)

@cars.route('/last_purchased')
def last_purchased():

    page = request.args.get('page', 1, type=int)
    base_query = Purchase.query.order_by(desc(Purchase.purchase_date))
    last_purchases = construct_query(base_query=base_query, transaction_name='Purchase', page=page)
    filter_values_dict = get_filter_values(session.get('purchase_brand', None), session.get('purchase_model', None))

    return render_template('purchased_cars.html', filter_values_dict=filter_values_dict, purchased_cars=last_purchases, main_page=True)


@cars.route('/last_purchased/filter', methods=['POST'])
def last_purchased_filter():
    filters = request.json
    renew_session_filters(filters)
    print(f"/last_purchased/filter: session = {session}")

    base_query = Purchase.query.order_by(desc(Purchase.purchase_date))
    base_query = construct_query(base_query=base_query, transaction_name='Purchase', page=1)
    # Execute the query and fetch the results
    filtered_purchases = [purchase for purchase in base_query.items]
    filtered_purchases_dict = [purchase.to_dict() for purchase in filtered_purchases]

    pages = list(base_query.iter_pages())
    urls = {
        'last_purchased': {},
        'search_results': {}
    }
    for page_num in pages:
        if page_num is None:
            continue
        urls['last_purchased'][page_num] = url_for('cars.last_purchased', page=page_num)
        urls['search_results'][page_num] = url_for('cars.search_results', search_place_choice='cars_in_storage', page=page_num)

    return jsonify(
        {
            "purchasesData": filtered_purchases_dict,
            "mainPage": True,
            "pages": pages,
            "urls": urls
        })


@cars.route('/search_results/last_purchased/filter', methods=['POST'])
def search_results_last_purchased_filter():
    filters = request.json
    renew_session_filters(filters)
    print(f"search_results/last_purchased/filter: session = {session}")

    # base_query = Purchase.query.order_by(desc(Purchase.purchase_date))
    base_query = Purchase.query.filter(Purchase.car_vin.not_in(Sale.query.with_entities(Sale.car_vin))).order_by(desc(Purchase.purchase_date))
    base_query = construct_query(base_query=base_query, transaction_name='Purchase', page=1)
    # Execute the query and fetch the results
    filtered_purchases = [purchase for purchase in base_query.items]
    filtered_purchases_dict = [purchase.to_dict() for purchase in filtered_purchases]

    pages = list(base_query.iter_pages())
    urls = {
        'last_purchased': {},
        'search_results': {}
    }
    for page_num in pages:
        if page_num is None:
            continue
        urls['last_purchased'][page_num] = url_for('cars.last_purchased', page=page_num)
        urls['search_results'][page_num] = url_for('cars.search_results', search_place_choice='cars_in_storage', page=page_num)

    return jsonify(
        {
            "purchasesData": filtered_purchases_dict,
            "mainPage": False,
            "pages": pages,
            "urls": urls
        })


@cars.route('/last_sold')
def last_sold():
    page = request.args.get('page', 1, type=int)
    filter_operations = get_sale_filter_operations()

    base_query = Sale.query.order_by(desc(Sale.sale_date))

    # Apply filters directly in the database query
    for filter_name, filter_value in session.items():
        if filter_value and filter_value != 'All':
            filter_operation = filter_operations.get(filter_name)
            if filter_operation:
                base_query = base_query.filter(filter_operation(filter_value))

    last_sales = base_query.paginate(page=page, per_page=CAR_CARDS_PER_PAGE)
    filter_values_dict = get_filter_values(session.get('sale_brand', None), session.get('sale_model', None))
    return render_template('sold_cars.html', filter_values_dict=filter_values_dict, transaction_cars=last_sales, main_page=True)


@cars.route('/last_sold/filter', methods=['POST'])
def last_sold_filter():
    filters = request.json
    renew_session_filters(filters)
    print(f"/last_sold/filter: session = {session}")

    base_query = Sale.query.order_by(desc(Sale.sale_date))
    base_query = construct_query(base_query=base_query, transaction_name='Sale', page=1)
    # Execute the query and fetch the results
    filtered_sales = [sale for sale in base_query.items]
    filtered_sales_dict = [sale.to_dict() for sale in filtered_sales]

    pages = list(base_query.iter_pages())
    urls = {
        'last_transaction': {},
        'search_results': {}
    }
    for page_num in pages:
        if page_num is None:
            continue
        urls['last_transaction'][page_num] = url_for('cars.last_sold', page=page_num)
        urls['search_results'][page_num] = url_for('cars.search_results', search_place_choice='cars_sold', page=page_num)

    return jsonify(
        {
            "transactionName": "Sale",
            "transactionData": filtered_sales_dict,
            "mainPage": True,
            "pages": pages,
            "urls": urls
        })

@cars.route('/search_results/last_sold/filter', methods=['POST'])
def search_results_last_sold_filter():
    filters = request.json
    renew_session_filters(filters)
    print(f"search_results/last_sold/filter: session = {session}")

    base_query = Sale.query.order_by(desc(Sale.sale_date))
    base_query = construct_query(base_query=base_query, transaction_name='Sale', page=1)
    # Execute the query and fetch the results
    filtered_sales = [sale for sale in base_query.items]
    filtered_sales_dict = [sale.to_dict() for sale in filtered_sales]

    pages = list(base_query.iter_pages())
    urls = {
        'last_transaction': {},
        'search_results': {}
    }
    for page_num in pages:
        if page_num is None:
            continue
        urls['last_transaction'][page_num] = url_for('cars.last_sold', page=page_num)
        urls['search_results'][page_num] = url_for('cars.search_results', search_place_choice='cars_sold', page=page_num)

    return jsonify(
        {
            "transactionName": "Sale",
            "transactionData": filtered_sales_dict,
            "mainPage": False,
            "pages": pages,
            "urls": urls
        })


@cars.route('/search', methods=['GET', 'POST'])
def search():
    # session.clear()
    remove_session_car_filters()
    car_vin_form = SearchByVinForm()
    car_filters_form = SearchByFiltersForm()
    if car_vin_form.identifier.data == "car_vin_form" and request.method == 'POST': # It is not quite correct
        car_vin = car_vin_form.car_vin.data
        session['purchase_car_vin'] = car_vin
        session['sale_car_vin'] = car_vin
        print(f"car_vin_form.identifier.data == 'car_vin_form': session = {session}")
        return redirect(url_for('cars.search_results', search_place_choice='cars_sold', **{'car_vin': car_vin}))
    
    if car_filters_form.identifier.data == "car_filters_form" and request.method == 'POST': # It is not quite correct
        form_data = request.form.to_dict()
        filters = {}
        for key, value in form_data.items():
            if key in ['csrf_token', 'identifier', 'submit', 'car_search_choice']:
                continue

            if value != '__None':
                filters[key] = value

        return redirect(url_for('cars.search_results', search_place_choice=form_data['car_search_choice'], **filters))

    if request.form.get('identifier') == 'navbar_search_form' and request.method == 'POST': # It is not quite correct
        search_field_value = request.form.get('navbar_search_field')
        # Split the search field value into brand and model
        search_values = search_field_value.split(' ', 1)
        brand = search_values[0]
        model = None
        brand = CarMake.query.filter_by(name=brand).first()
        if len(search_values) == 2:
            model = search_values[1]
        filters = {
            'brand': brand.car_make_id if brand else -1, # # It is not quite correct
            'model': model
        }
        return redirect(url_for('cars.search_results', search_place_choice='cars_sold', **filters))
        # return redirect(url_for('cars.search_results.last_sold.filter', **filters))
    car_filters = get_filter_values(session.get('purchase_brand', None), session.get('purchase_model', None))

    return render_template("search.html", car_vin_form=car_vin_form, car_filters_form=car_filters_form, car_filters=car_filters)


@cars.route('/search_results/<search_place_choice>', methods=['GET'])
def search_results(search_place_choice):

    page = request.args.get('page', 1, type=int)
    # Retrieve filter parameters from the AJAX request
    filters = request.args

    base_query = Purchase.query.filter(Purchase.car_vin.not_in(Sale.query.with_entities(Sale.car_vin))).order_by(desc(Purchase.purchase_date))
    # base_query = Purchase.query.order_by(desc(Purchase.purchase_date))
    transaction_name = 'Purchase'
    # Check if the "car_search_choice" filter is set to "cars_sold"
    if search_place_choice == 'cars_sold':
        base_query = Sale.query.order_by(desc(Sale.sale_date))
        transaction_name = 'Sale'

    for filter_name, filter_value in filters.items():
        if filter_name in ['csrf_token']:
            continue
        filter_name = 'sale_' + filter_name if search_place_choice == 'cars_sold' else 'purchase_' + filter_name
        session[filter_name] = filter_value

    print(f"/search_results/{search_place_choice}: session = {session}")
    filtered_transaction_records = construct_query(base_query, transaction_name, page=page)
    print(f"filtered_transaction_records = {filtered_transaction_records}")

    filter_values_dict = get_filter_values(session.get('purchase_brand', None), session.get('purchase_model', None))
    if search_place_choice == 'cars_in_storage':
        return render_template('purchased_cars.html', filter_values_dict=filter_values_dict, purchased_cars=filtered_transaction_records, main_page=False)
    return render_template('sold_cars.html', filter_values_dict=filter_values_dict, transaction_cars=filtered_transaction_records, main_page=False)
