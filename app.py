from car_resale_business_project import app, db
from car_resale_business_project.models import Car
from flask import redirect, url_for


@app.route('/')
def index():
    first_car = db.session.query(Car).first()
    print(f"first_car = {first_car}")
    return redirect(url_for('purchases.last_purchased'))

if __name__ == '__main__':
    app.run(debug=True)

