from car_resale_business_project import app
from flask import render_template


@app.route('/')
def index():
    return render_template('base.html', title="Car Resale Business")

if __name__ == '__main__':
    app.run(debug=True)

