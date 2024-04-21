from flask import Flask

from car_resale_business_project.purchases.purchases import purchases
from car_resale_business_project.cars.cars import cars

app = Flask(__name__)
app.register_blueprint(purchases, url_prefix="/purchase")
app.register_blueprint(cars, url_prefix="/car")

app.config['SECRET_KEY'] = 'mysecretkey'