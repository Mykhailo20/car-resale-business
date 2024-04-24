from flask import Blueprint, render_template, request, redirect, url_for
from car_resale_business_project.cars.forms import SearchByVinForm, SearchByFiltersForm
from car_resale_business_project.models import CarMake, Car

cars = Blueprint("cars", __name__, template_folder="templates", static_folder="static")

@cars.route('/search', methods=['GET', 'POST'])
def search():
    car_vin_form = SearchByVinForm()
    car_filters_form = SearchByFiltersForm()
    print(f"search->method = {request.method}")

    if car_vin_form.identifier.data == "car_vin_form" and car_vin_form.validate_on_submit():
        car_vin = car_vin_form.car_vin.data
        return redirect(url_for('cars.search_results', **{'car_vin': car_vin}))
        return f"<h1>Cars Search Result (car_vin form)</h1><p>You searched for {car_vin}</p>"
    
    
    if car_filters_form.identifier.data == "car_filters_form" and request.method == 'POST': # It is not quite correct
        form_data = request.form.to_dict()
        print(f"Received form data: {form_data}")
        # Extract filters from the form
        filters = {
            'brand': form_data.get('brand'),
            'model': form_data.get('model')
            # Add more filters as needed
        }
        # Redirect to the endpoint that handles dynamic filtering
        return redirect(url_for('cars.search_results', **filters))
    
    return render_template("search.html", car_vin_form=car_vin_form, car_filters_form=car_filters_form)


@cars.route('/search_results', methods=['GET'])
def search_results():
    car_vin = request.args.get('car_vin')
    brand = request.args.get('brand')
    model = request.args.get('model')
    return f"<h1>Cars Search Result</h1><p>You searched for {car_vin} {brand} {model}</p>"