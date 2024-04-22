from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField

class SearchByVinForm(FlaskForm):
    car_vin = StringField("Enter car vin")
    submit = SubmitField("Search")