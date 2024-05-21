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

def render_template_with_session(template_name):
    return render_template(template_name, session=session)


def set_logged_in():
    session["logged_in"] = True


def set_logged_out():
    session["logged_in"] = False

def is_logged_in():
    return session.get("logged_in")


