from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, NumberRange, Length, Email
from wtforms_components import DateField, DateRange

from car_resale_business_project.models import CarMake, CarBodyType, Car, Seller, City, Purchase


class SearchByVinForm(FlaskForm):
    identifier = StringField()
    car_vin = StringField("Enter car vin")
    submit = SubmitField("Search")


class SearchByFiltersForm(FlaskForm):
    identifier = StringField()
    brand = QuerySelectField('Brand', query_factory=lambda: CarMake.query.all(), get_label="name", allow_blank=True, blank_text="Brand")

    model = QuerySelectField('Model', query_factory=lambda: Car.query.filter(None).all(), get_label="model", allow_blank=True, blank_text="Model")
    body_type = QuerySelectField('Body_Type', query_factory=lambda: CarBodyType.query.all(), get_label="name", allow_blank=True, blank_text="Body Type")
    city = QuerySelectField('City', query_factory=lambda: City.query.all(), get_label="name", allow_blank=True, blank_text="City")
    condition = SelectField(choices=
                                [
                                  ("__None", "Condition"),
                                  ("1.0-2.0", "Bad"),
                                  ("2.0-3.0", "Normal"),
                                  ("3.0-4.0", "Good"),
                                  ("4.0-5.0", "Excellent")
                                ],
                            )
    odometer = SelectField(choices=
                                [
                                  ("__None", "Odometer"),
                                  ("0-50000", "< 50k"),
                                  ("50000-100000", "50k-100k"),
                                  ("100000-200000", "100k-200k"),
                                  ("200000-inf", "> 200k")
                                ]
                            )
    """
    car_search_choice = SelectField(choices=
                                [
                                  ("__None", "Search Choice"),
                                  ("all", "All"),
                                  ("cars_in_storage", "Cars in Storage"),
                                  ("cars_sold", "Sold Cars")
                                ]
                            )
    """
    car_search_choice = SelectField(choices=
                                [
                                  ("cars_in_storage", "Cars in Storage"),
                                  ("cars_sold", "Sold Cars")
                                ], default=("cars_in_storage", "Cars in Storage")
                            )
    submit = SubmitField("Search")


class AddEstimationForm(FlaskForm):
    identifier = StringField()
    estimated_price = IntegerField('Price', validators=[InputRequired(), NumberRange(min=0)], render_kw={"placeholder": "Estimated Price"})
    submit = SubmitField("Reestimate")


class AddAutoEstimationForm(FlaskForm):
    identifier = StringField()
    submit = SubmitField("Automatic reestimation")