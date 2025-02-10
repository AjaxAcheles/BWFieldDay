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
@admin_logged_out_required
def login():
    if request.method == "POST":
        # if not already logged in
        if not is_logged_in():
            phone_number = request.form.get("phone-number")
            ids_dict = get_parent_id_and_children_id_with_phone_number(phone_number)
            # if valid then set logged in and continue
            if ids_dict:
                set_logged_in(ids_dict["parent_id"], ids_dict["children_info_dict"])
            else:
                # if entered phone number is not valid then return error
                flash("Invalid phone number", "error")
                return redirect(url_for("admin.login"))
        
        # if entered phone number is not valid then return error and stop 
        if not get_phone_number_with_parent_id(get_parent_id()):
            flash("Invalid phone number", "error")
            return redirect(url_for("admin.login"))
            
        # check matching email 
        if get_email_with_parent_id(get_parent_id()) != request.form.get("email"):
            flash("Invalid email", "error")
            return redirect(url_for("admin.login"))
            
        # check for valid admin credentials 
        if is_valid_admin(request.form.get("email"), request.form.get("password")) is True:
            set_admin_logged_in(request.form.get("email"))
            flash(f"Login successful.", "message")
            return redirect(url_for("admin.dashboard"))
        # check if this is first time logging in
        elif is_admin(request.form.get("email")) is True:
            # remove old placeholder admin where password was none and replace with new password
            remove_admin(request.form.get("email"), None)
            add_valid_admin(request.form.get("email"), request.form.get("password"))
            set_admin_logged_in(request.form.get("email"))
            flash(f"Congrats, this is your FIRST successful login! Your password has been set.", "message")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for("admin.login"))

    elif request.method == "GET":
        return render_template_with_session('admin_login.html')


@admin_bp.route("/admin_dashboard", methods=['GET', 'POST'])
@admin_login_required
def dashboard():
    return render_template_with_session('admin_dashboard.html')


@admin_bp.route("/admin_manage_events", methods=['GET', 'POST'])
@admin_login_required
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
    parent_t_shirts = get_parent_t_shirts()
    child_t_shirts = get_child_t_shirts()
    t_shirt_sizes = get_t_shirt_sizes_from_admin_info()
    flattened_parent_t_shirts = [size for sublist in parent_t_shirts for size in sublist]
    flattened_child_t_shirts = [size for sublist in child_t_shirts for size in sublist]
    all_t_shirts = {}
    for t_shirt_size in t_shirt_sizes:
        # count how many times t_shirt_size appears in both parent_t_shirts and child_t_shirts
        # then add them in a counter to all_t_shirts. example result should look like this. all_t_shirts = {"XL": 2, "L": 1, "M": 0}
        count_in_parents = flattened_parent_t_shirts.count(t_shirt_size)
        count_in_children = flattened_child_t_shirts.count(t_shirt_size)
        all_t_shirts[t_shirt_size] = count_in_parents + count_in_children

    return render_template_with_session("admin_t_shirt_management.html", all_t_shirts=all_t_shirts)


@admin_bp.route("/admin_manage_or_add_admins", methods=['GET', 'POST'])
@admin_login_required
def manage_admins():
    if request.method == "GET":
        return render_template_with_session("admin_manage_or_add_admins.html")
    elif request.method == "POST":
        if request.form.get("type") == "add":
            email = request.form.get("email")
            phone_number = request.form.get("phone-number")
            # Check to see if account is already an admin
            if is_admin(email) is True:
                flash(f"Admin account already exists.", "message")
                return redirect(url_for("admin.manage_admins"))
            # Check to see if base account even exists
            elif is_parent_exits(phone_number) is False:
                flash(f"Account doen't exist.", "message")
                return redirect(url_for("admin.manage_admins"))
            # Add admin
            else:
                add_valid_admin(email, None)
                flash(f"Admin account added successfully! The new admin will be prompted to create a password upon first login to their ADMIN DASHBOARD", "message")
                return redirect(url_for("admin.manage_admins"))
        elif request.form.get("type") == "remove":
            email = request.form.get("email")
            phone_number = request.form.get("phone-number")
            # Check to see if base account even exists
            if is_parent_exits(phone_number) is False:
                flash(f"Account doen't exist.", "message")
                return redirect(url_for("admin.manage_admins"))
            # Check to see if account is not an admin
            elif is_admin(email) is False:
                flash(f"Account not an admin level account.", "message")
                return redirect(url_for("admin.manage_admins"))
            else:
                remove_admin_blind(email)
                flash(f"Admin account removed successfully!", "message")



@admin_bp.route("/admin_database_management", methods=['GET', 'POST'])
@admin_login_required
def manage_database():
    if request.method == "GET":
        # Get all tables from database.db and store them in a Json-style python dict.
        tables = get_all_tables()
        return render_template_with_session("admin_database_management.html", tables=tables)
    elif request.method == "POST":
        # save the destroyer's family
        family = get_family(session["parent_id"])

        # reset the database
        current_admin_info = [session["email"], get_admin_password_with_email(session["email"])]
        reset_all_databases(current_admin_info)
        
        # ressurect the destroyer's family
        parents = family["parents"]
        children = family["children"]

        parent_1_name = parents[1]
        parent_email = parents[2]
        parent_phone_number = parents[3]
        parent_1_t_shirt_size = parents[4]
        is_parent_1_volunteering = parents[5]
        parent_2_name = parents[6]
        parent_2_t_shirt_size = parents[7]
        is_parent_2_volunteering = parents[8]
        number_of_children = parents[9]
        insert_parent_info(parent_1_name, parent_email, parent_phone_number, parent_1_t_shirt_size, is_parent_1_volunteering, parent_2_name, parent_2_t_shirt_size, is_parent_2_volunteering, number_of_children)
        
        for child in children:
            child_name = child[1]
            child_age = child[2] 
            child_t_shirt_size = child[3]
            parent_id = child[4]
            insert_child_info(child_name, child_age, child_t_shirt_size, parent_id)

        return redirect(url_for("admin.dashboard"))


