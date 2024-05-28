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
from auth import *
from account import *
from decorators import *

app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(account_bp)

with app.app_context():
    create_parent_info_table()
    create_child_info_table()

app.secret_key = "NJMFTGEWTRIOPHGFVFXGDCljkfgtre45tiophufhgyju435u8o9324i09dfhkujg"

@app.route("/")
def home():
    return render_template_with_session("home.html")

@app.route("/FAQ")
def frequently_asked_questions():
    return render_template_with_session("frequently_asked_questions.html")

