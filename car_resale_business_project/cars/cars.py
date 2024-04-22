from flask import Blueprint, render_template

cars = Blueprint("cars", __name__, template_folder="templates", static_folder="static")

@cars.route('/search')
def search():
    return render_template("search.html")