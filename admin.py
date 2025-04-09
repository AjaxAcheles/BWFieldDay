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
import fetch_volunteer_data


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
        if str(get_phone_number_with_parent_id(get_parent_id())) != str(request.form.get("phone-number")):
            flash("Invalid phone number", "error")
            return redirect(url_for("admin.login"))
            
        # check matching email 
        if str(get_email_with_parent_id(get_parent_id())) != str(request.form.get("email")):
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
    children = get_children_by_age_group()
    return render_template_with_session('admin_dashboard.html', children=children)


@admin_bp.route("/admin_t_shirt_management", methods=['GET', 'POST'])
@admin_login_required
def manage_t_shirts():
    if request.method == "GET":
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

        should_enable_t_shirt_orders = get_value_from_admin_info("enable_t_shirt_orders")[0].strip().lower() == "true"
        return render_template_with_session("admin_t_shirt_management.html", all_t_shirts=all_t_shirts, should_enable_t_shirt_orders=should_enable_t_shirt_orders)
    
    elif request.method == "POST":
        should_enable_t_shirt_orders = request.form.get("enable-t-shirt-orders").strip().lower() == "true"
        old_enable_t_shirt_orders = get_value_from_admin_info("enable_t_shirt_orders")[0].strip().lower() == "true"
        if should_enable_t_shirt_orders != old_enable_t_shirt_orders:
            edit_all_keys_in_admin_table("enable_t_shirt_orders", should_enable_t_shirt_orders)
        return redirect(url_for("admin.manage_t_shirts"))


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
                return redirect(url_for("admin.manage_admins"))



@admin_bp.route("/admin_database_management", methods=['GET', 'POST'])
@admin_login_required
def manage_database():
    if request.method == "GET":
        # Get all tables from database.db and store them in a Json-style python dict.
        tables = get_all_tables()
        tables = tables | fetch_volunteer_data.get_all_tables()
        return render_template_with_session("admin_database_management.html", tables=tables)
    elif request.method == "POST":
        # save the destroyer's family
        family = get_family(session["parent_id"])

        # reset the database
        current_admin_info = [session["email"], get_admin_password_with_email(session["email"])]
        reset_all_databases(current_admin_info)
        fetch_volunteer_data.reset_all_volunteer_databases()
        
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


