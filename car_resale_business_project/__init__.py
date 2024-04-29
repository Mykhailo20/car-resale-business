from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from car_resale_business_project.config.db_config import *

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'

# OLTP DB Config
oltp_config_dict = get_oltp_fill_demonstration_config()
olap_config_dict = get_olap_fill_demonstration_config()
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{oltp_config_dict['user']}:{oltp_config_dict['password']}@localhost:5432/{oltp_config_dict['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from car_resale_business_project.cars.cars import cars

app.register_blueprint(cars, url_prefix="/car")