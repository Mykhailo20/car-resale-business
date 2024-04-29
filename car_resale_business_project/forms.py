from datetime import datetime, date

import psycopg2 as pg2

from sqlalchemy import func
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField, FloatField, DateField,TextAreaField
from wtforms.validators import InputRequired, NumberRange
from wtforms_components import DateField, DateRange

from wtforms_sqlalchemy.fields import QuerySelectField

from car_resale_business_project import oltp_config_dict
from car_resale_business_project.databases.fill_oltp.utils.data_insertion.general_functions import get_db_enum_values
from car_resale_business_project.models import CarMake, CarBodyType, Car, Seller, Employee, Color


class AddPurchaseForm(FlaskForm):
    identifier = StringField()

    # Seller
    seller_name = QuerySelectField(
        'Seller',
        query_factory=lambda: Seller.query
            .distinct(Seller.name)
            .order_by(Seller.name)  # Sort sellers alphabetically ignoring case
            .all(),
        get_label="name",
        allow_blank=True,
        blank_text="Seller",
        validators=[InputRequired()]
    )

    # Emplyee
    employee_query = lambda: Employee.query.distinct(Employee.first_name, Employee.last_name).all()
    employee_name = QuerySelectField('Employee', query_factory=employee_query, get_label=lambda emp: f"{emp.first_name} {emp.last_name}", allow_blank=True, blank_text="Employee", validators=[InputRequired()])

    # Car 
    car_vin = StringField("Enter car vin", validators=[InputRequired()], render_kw={"placeholder": "Enter car vin"})
    brand = QuerySelectField('Brand', query_factory=lambda: CarMake.query.order_by(CarMake.name).all(), get_label="name", allow_blank=True, blank_text="Brand", validators=[InputRequired()])
    model = QuerySelectField('Model', query_factory=lambda: Car.query.filter(None).all(), get_label="model", allow_blank=True, blank_text="Model", validators=[InputRequired()])
    trim = QuerySelectField('Trim', query_factory=lambda: Car.query.filter(None).all(), get_label="trim", allow_blank=True, blank_text="Trim")
    body_type = QuerySelectField('Body_Type', query_factory=lambda: CarBodyType.query.order_by(CarBodyType.name).all(), get_label="name", allow_blank=True, blank_text="Body Type", validators=[InputRequired()])
    color = QuerySelectField('Color', query_factory=lambda: Color.query.order_by(Color.name).all(), get_label="name", allow_blank=True, blank_text="Color", validators=[InputRequired()])

    manufacture_year = SelectField(choices=[(year, year) for year in range(1990, datetime.now().year + 1)], default=2010, validators=[InputRequired()])

    # Read unique values for transmission field from the transmission_enum in OLTP DB
    oltp_db_conn = pg2.connect(database=oltp_config_dict['database'], user=oltp_config_dict['user'], password=oltp_config_dict['password'])
    transmission_values = get_db_enum_values(oltp_db_conn, enum_name='transmission_enum')
    oltp_db_conn.close()
    transmission = SelectField(choices=[(transmission, transmission) for transmission in transmission_values], validators=[InputRequired()])

    condition = SelectField(choices=[(condition / 10, condition / 10) for condition in range(10, 51)], render_kw={"placeholder": "Condition"})
    # condition = FloatField('Condition', validators=[InputRequired(), NumberRange(min=1, max=5)])
    odometer = IntegerField('Odometer', validators=[InputRequired(), NumberRange(min=0)], render_kw={"placeholder": "Odometer"})
    purchase_date = DateField('Date', format='%Y-%m-%d', default=date.today(), validators=[
        InputRequired(),
        DateRange(
            min=date(2010, 1, 1),
            max=date.today()
        )
    ])
    purchase_price = IntegerField('Price', validators=[InputRequired(), NumberRange(min=0)], render_kw={"placeholder": "Price"})
    description = TextAreaField('Description', render_kw={"placeholder": "Description"})
    submit = SubmitField("Submit")