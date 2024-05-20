from functools import wraps
from flask import session, url_for, render_template, redirect

def login_required(original_function):
    @wraps(original_function)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            return original_function(*args, **kwargs)
        else:
            return redirect(url_for('auth.login'))
    return decorated_function