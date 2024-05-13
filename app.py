from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    session,
    g
)
from fetch_data import *


app = Flask(__name__)

with app.app_context():
    create_parent_info_table()
    create_child_info_table()

app.secret_key = "NJMFTGEWTRIOPHGFVFXGDCljkfgtre45tiophufhgyju435u8o9324i09dfhkujg"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register")
def register():
    return render_template("home.html")

@app.route("/edit_info")
def edit_info():
    parent_data = get_parent_data()
    child_data = get_child_data()
    return parent_data, child_data

@app.route("/volunteering")
def volunteering():
    return render_template("home.html")
