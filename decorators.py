from functools import wraps
from flask import session, url_for, render_template, redirect

def login_required(original_function):
    @wraps(original_function)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            return original_function(*args, **kwargs)
        else:
            return render_template("login.html", error="You are not logged in")
    return decorated_function


def logged_out_required(original_function):
    @wraps(original_function)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in') is False:
            return original_function(*args, **kwargs)
        else:
            return render_template("login.html", error="You are already logged in. Please log out first.")
    return decorated_function
