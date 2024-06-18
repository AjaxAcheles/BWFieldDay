from flask import (
    Blueprint, 
    Flask, 
    request, 
    redirect, 
    url_for, 
    session, 
    g,
    flash
)
from decorators import *
from fetch_data import *
from functions import *

admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/admin_login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        return request.form
    elif request.method == "GET":
        return render_template_with_session('admin_login.html')


@admin_bp.route("/admin_dashboard", methods=['GET', 'POST'])
@admin_login_required
def dashboard():
    return render_template_with_session('admin_dashboard.html')



@admin_bp.route("/admin_manage_events", methods=['GET', 'POST'])
# @admin_login_required
def manage_events():
    if request.method == 'GET':
        events = get_events_from_admin_info()
        occupied_positions = get_occupied_positions()
        return render_template_with_session("admin_event_management.html", events=events, occupied_positions=occupied_positions)
    else:
        return request.form


@admin_bp.route("/admin_t_shirt_management", methods=['GET', 'POST'])
@admin_login_required
def manage_t_shirts():
    return render_template_with_session("admin_t_shirt_management.html")


@admin_bp.route("/admin_manage_or_add_admins", methods=['GET', 'POST'])
@admin_login_required
def manage_admins():
    return render_template_with_session("admin_manage_or_add_admins.html")


@admin_bp.route("/admin_database_management", methods=['GET', 'POST'])
@admin_login_required
def manage_database():
    return render_template_with_session("admin_database_management.html")


