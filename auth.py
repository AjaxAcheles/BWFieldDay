from flask import (
    Blueprint, 
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    session, 
    g
)
from fetch_data import *
from functions import *
from decorators import *

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=['GET', 'POST'])
@logged_out_required
def register():
    if request.method == "GET":
        return render_template_with_session("register.html", t_shirt_sizes=["Youth S", "Youth M", "Youth L", "Youth XL", "XS", "S", "M", "L", "XL", "XXL", "XXXL"])
    
    elif request.method == "POST":
        parent_1_name = request.form.get("parent-1-name")
        parent_email = request.form.get("parent-email")
        parent_phone_number = int(request.form.get("parent-phone-number"))
        # parent 1 t-shirt size
        parent_1_t_shirt_option = request.form.get("parent-1-t-shirt-option")
        if parent_1_t_shirt_option == "true":
            parent_1_t_shirt_size = request.form.get("parent-1-t-shirt-size")
        elif parent_1_t_shirt_option == "false":
            parent_1_t_shirt_size = None
        # is parent 1 volunteering?
        if request.form.get("is-parent-1-volunteering") == "true":
            is_parent_1_volunteering = True
        else:
            is_parent_1_volunteering = False
        # parent 2 name
        parent_2_name = request.form.get("parent-2-name")
        # parent 2 t-shirt size
        parent_2_t_shirt_option = request.form.get("parent-2-t-shirt-option")
        if parent_2_t_shirt_option == "true":
            parent_2_t_shirt_size = request.form.get("parent-2-t-shirt-size")
        elif parent_2_t_shirt_option == "false":
            parent_2_t_shirt_size = None
        # is parent 2 volunteering?
        if request.form.get("is-parent-2-volunteering") == "true":
            is_parent_2_volunteering = True
        else:
            is_parent_2_volunteering = False

        # set number_of_children
        number_of_children = int(request.form.get("number-of-children"))
        
        # add to database
        insert_parent_info(parent_1_name, parent_email, parent_phone_number, parent_1_t_shirt_size, is_parent_1_volunteering, parent_2_name, parent_2_t_shirt_size, is_parent_2_volunteering, number_of_children)

        # get parent id
        parent_id = int(get_parent_id_with_email(parent_email)[0])

        # load children
        children_id = {}
        for index in range(1, number_of_children + 1):
            child_name = request.form.get(f"child-{index}-name")
            child_age = int(request.form.get(f"child-{index}-age"))
            if request.form.get(f"child-{index}-t-shirt-option") == "true":
                child_t_shirt_size = request.form.get(f"child-{index}-t-shirt-size")
            elif request.form.get(f"child-{index}-t-shirt-option") == "false":
                child_t_shirt_size = None
            child_id = insert_child_info(child_name, child_age, child_t_shirt_size, parent_id)
            children_id[child_name] = child_id

        set_logged_in(parent_id, children_id)

        if is_parent_1_volunteering is True or is_parent_2_volunteering is True:
            return redirect(url_for("account.volunteering"))
        else:
            return redirect(url_for("home"))

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template_with_session('login.html')

    elif request.method == "POST":
        phone_number = request.form.get("phone-number")
        ids_dict = get_parent_id_and_children_id_with_phone_number(phone_number)
        if ids_dict:
            set_logged_in(ids_dict["parent_id"], ids_dict["children_info_dict"])
            return redirect(url_for("home"))
        else:
            return render_template_with_session("login.html", error="Invalid phone number")

@auth_bp.route("/logout")
def logout():
    if is_logged_in():
        set_logged_out()
        return render_template_with_session('login.html', message="You have been logged out")
    else:
        return render_template_with_session('login.html', message="You are not logged in")
