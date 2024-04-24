from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField

from car_resale_business_project.models import CarMake, CarBodyType, Car, Seller, City, Purchase


class SearchByVinForm(FlaskForm):
    identifier = StringField()
    car_vin = StringField("Enter car vin")
    submit = SubmitField("Search")


class SearchByFiltersForm(FlaskForm):
    identifier = StringField()
    brand = QuerySelectField('Brand', query_factory=lambda: CarMake.query.all(), get_label="name", allow_blank=True, blank_text="Brand")
    # model = QuerySelectField('Model', query_factory=lambda: Car.query.distinct(Car.model).all(), get_label="model", allow_blank=True, blank_text="Model")
    model = QuerySelectField('Model', query_factory=lambda: Car.query.filter(None).all(), get_label="model", allow_blank=True, blank_text="Model")
    body_type = QuerySelectField('Body_Type', query_factory=lambda: CarBodyType.query.all(), get_label="name", allow_blank=True, blank_text="Body Type")
    #transmission = QuerySelectField('Transmission', query_factory=lambda: Car.query.distinct(Car.transmission).all(), get_label="transmission", allow_blank=True, blank_text="Transmission")
    # seller_name = QuerySelectField('Seller', query_factory=lambda: Seller.query.distinct(Seller.name).all(), get_label="name", allow_blank=True, blank_text="Seller")
    city = QuerySelectField('City', query_factory=lambda: City.query.all(), get_label="name", allow_blank=True, blank_text="City")
    # manufacture_year = QuerySelectField('Year From', query_factory=lambda: Car.query.distinct(Car.manufacture_year).all(), get_label="manufacture_year", allow_blank=True, blank_text="Manufacture Year")
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