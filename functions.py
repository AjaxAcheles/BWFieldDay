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

def render_template_with_session(template_name, *args, **kwargs):
    return render_template(template_name, session=session, *args, **kwargs)


def get_parent_id():
    return session.get("parent_id")


def set_logged_in(parent_id, children_id:dict):
    session["logged_in"] = True
    session["parent_id"] = parent_id
    session["children_id"] = children_id


def set_logged_out():
    session.clear()


def get_parent_id():
    return session.get("parent_id")


def is_logged_in():
    return session.get("logged_in")

