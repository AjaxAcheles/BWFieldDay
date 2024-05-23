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


def set_logged_in(parent_id):
    session["logged_in"] = True
    session["parent_id"] = parent_id


def set_logged_out():
    session.clear()


def get_parent_id():
    return session.get("parent_id")


def is_logged_in():
    return session.get("logged_in")


