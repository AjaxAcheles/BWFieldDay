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
    elif request.method == 'POST':

        cleaned_request_form = {key.strip(): request.form[key].strip() for key in request.form}

        old_events_dict = get_events_from_admin_info()
        updated_events_dict = {}

        to_manage_events = [key.strip().split("--")[1].replace("-", " ") for key in cleaned_request_form if key.startswith("event--")]

        # check for duplicate event names
        check_for_duplicate_event_names = [cleaned_request_form[key].strip() for key in cleaned_request_form if key.startswith("event")]
        for event_name in check_for_duplicate_event_names:
            if to_manage_events.count(event_name) > 1:
                flash(f"Duplicate event names: {event_name}", "error")
                return redirect(url_for("admin.manage_events"))
        del check_for_duplicate_event_names

        # update existing events, roles, and positions
        for old_event_name in old_events_dict:
            old_event_id = old_event_name.replace(" ", "-")
            updated_event_name = cleaned_request_form["event--" + old_event_id]

            updated_role_dict = {}
            for old_role_name in old_events_dict[old_event_name]:
                old_role_id = old_role_name.replace(" ", "-")
                updated_role_name = cleaned_request_form["role--" + old_event_id + "--" + old_role_id]
                updated_number_of_positions = int(cleaned_request_form["positions--" + old_event_id + "--" + old_role_id])
                updated_role_dict[updated_role_name] = updated_number_of_positions

            updated_events_dict[updated_event_name] = updated_role_dict
            to_manage_events.remove(old_event_name)
        
        # add new events, roles, and positions
        new_events_dict = {}
        for new_cleaned_event_id in to_manage_events:
            event_id = new_cleaned_event_id.replace(" ", "-")
            event_name = cleaned_request_form["event--" + event_id]

            new_role_dict = {}
            for role in cleaned_request_form:
                if role.startswith("role--" + event_id):
                    new_role_id = role.split("--")[2]
                    new_role_name = cleaned_request_form[role]
                    new_number_of_positions = int(cleaned_request_form["positions--" + event_id + "--" + new_role_id])
                    new_role_dict[new_role_name] = new_number_of_positions

            new_events_dict[event_name] = new_role_dict
            to_manage_events.remove(new_cleaned_event_id)

        updated_events_dict.update(new_events_dict)
        update_events_in_admin_info(updated_events_dict)
        
        flash("Events updated successfully!", "message")
        return redirect(url_for("admin.manage_events"))


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


