from car_resale_business_project import app
from flask import redirect, url_for


@app.route('/')
def index():
    return redirect(url_for('purchases.last_purchased'))

if __name__ == '__main__':
    app.run(debug=True)

