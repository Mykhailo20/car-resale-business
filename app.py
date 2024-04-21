from car_resale_business_project import app, db
from car_resale_business_project.models import Purchase
from flask import redirect, url_for


@app.route('/')
def index():
    first_10_purchases = db.session.query(Purchase).limit(10).all()
    for purchase in first_10_purchases:
        print(purchase)
    return redirect(url_for('purchases.last_purchased'))

if __name__ == '__main__':
    app.run(debug=True)

