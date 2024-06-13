from functools import wraps
from flask import session, url_for, render_template, redirect
from functions import *

def login_required(original_function):
    @wraps(original_function)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            return original_function(*args, **kwargs)
        else:
            return render_template_with_session("login.html", error="You are not logged in")
    return decorated_function


def logged_out_required(original_function):
    @wraps(original_function)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            return render_template_with_session("login.html", error="You are already logged in. Please log out first.")
        else:
            return original_function(*args, **kwargs)
    return decorated_function


def admin_login_required(original_function):
    @wraps(original_function)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in') and session.get('admin_logged_in'):
            return original_function(*args, **kwargs)
        else:
            return render_template_with_session("admin_login.html", error="You are not logged in as an admin")
    return decorated_function
