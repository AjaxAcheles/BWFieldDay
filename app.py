from flask import Flask, render_template, request, redirect, url_for, Blueprint
from fetch_volunteer_data import *
from fetch_data import *
from volunteers import *

app = Flask(__name__)
app.register_blueprint(volunteers_bp)

# At startup, make sure our database tables exist.
with app.app_context():
    create_events_table()
    create_roles_table()
    create_positions_table()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
