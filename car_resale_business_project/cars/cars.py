from flask import Blueprint, render_template, request
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
        
        return f"<h1>Cars Search Result (car_vin form)</h1><p>You searched for {car_vin}</p>"
    if car_filters_form.identifier.data == "car_filters_form" and car_filters_form.validate_on_submit():
        print(f"Cars Search Result (car_filters form)")
        car_brand = car_filters_form.brand.data
        return f"<h1>Cars Search Result (car_filters form)</h1><p>You searched for {car_brand}</p>"
    
    return render_template("search.html", car_vin_form=car_vin_form, car_filters_form=car_filters_form)