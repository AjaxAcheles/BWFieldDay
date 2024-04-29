from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    session
)

app = Flask(__name__)
app.secret_key = "NJMFTGEWTRIOPHGFVFXGDCljkfgtre45tiophufhgyju435u8o9324i09dfhkujg"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register")
def register():
    return render_template("home.html")

@app.route("/edit_info")
def edit_info():
    return render_template("home.html")

@app.route("/volunteering")
def volunteering():
    return render_template("home.html")



