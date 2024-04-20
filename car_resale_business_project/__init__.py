from flask import Flask

app = Flask(__name__)

# Often people will also separate these into a separate config.py file 
app.config['SECRET_KEY'] = 'mysecretkey'