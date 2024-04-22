from flask import redirect, url_for, request, render_template

from car_resale_business_project import app
from car_resale_business_project.models import Car



@app.route('/')
def index():
    return redirect(url_for('purchases.last_purchased'))


@app.route('/get_car_brand_models')
def get_car_brand_models():
    make_id = request.args.get("brand", type=int)
    car_unique_models = Car.query.filter_by(make_id=make_id).distinct(Car.model).all()
    print(f"car_unique_models = {car_unique_models}")
    return render_template("car_model_options.html", cars=car_unique_models)



if __name__ == '__main__':
    app.run(debug=True)

