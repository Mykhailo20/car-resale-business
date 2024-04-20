from flask import Blueprint, render_template

purchases = Blueprint("purchases", __name__, template_folder="templates", static_folder="static")

@purchases.route('/add')
def add():
    return render_template('add.html')