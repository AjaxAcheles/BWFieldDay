from flask import (
    Blueprint, 
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    session, 
    g
)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    elif request.method == "POST":
        return request.form


@auth_bp.route("/login", methods=['GET', 'POST'])
def login_page():
    return render_template('login.html')