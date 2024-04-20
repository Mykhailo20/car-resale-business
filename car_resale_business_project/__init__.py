from flask import Flask

from car_resale_business_project.purchases.purchases import purchases

app = Flask(__name__)
app.register_blueprint(purchases, url_prefix="/purchase")

app.config['SECRET_KEY'] = 'mysecretkey'