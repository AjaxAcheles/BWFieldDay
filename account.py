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
import json
from decorators import *
from fetch_data import *
from functions import *

account_bp = Blueprint('account', __name__)


@account_bp.route("/edit_info", methods=['GET', 'POST'])
@login_required
def edit_info():
    if request.method == 'GET':
        parent_info = get_parent_info_with_parent_id(session["parent_id"])
        children_info = get_children_info_with_parent_id(session["parent_id"])
        t_shirt_sizes = get_t_shirt_sizes_from_admin_info()
        return render_template_with_session("edit_info.html", parent_info=parent_info, children_info=children_info, t_shirt_sizes=t_shirt_sizes)
    
    elif request.method == 'POST':
        parent_1_name = request.form.get("parent-1-name").lower()
        parent_email = request.form.get("parent-email").lower()
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
        parent_2_name = request.form.get("parent-2-name").lower()
        if parent_2_name.replace(" ", "") == "" or request.form.get("is-parent-2") == "false":
            parent_2_name = None
            parent_2_t_shirt_size = None
            is_parent_2_volunteering = None
        else:
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
        
        # edit parent info in the database
        edit_parent_info(session["parent_id"], parent_1_name, parent_email, parent_phone_number, parent_1_t_shirt_size, is_parent_1_volunteering, parent_2_name, parent_2_t_shirt_size, is_parent_2_volunteering, number_of_children)

        # load children
        past_child_names = []
        for index in range(1, number_of_children + 1):
            child_new_name = request.form.get(f"child-{index}-name").lower()
            if child_new_name in past_child_names:
                return ["error, name already exists", past_child_names, child_new_name]
            else:
                past_child_names.append(child_new_name)

            # detection for new children.
            try:
                child_old_name = request.form.get(f"child-{index}-old-name").lower()
            except:
                child_name = request.form.get(f"child-{index}-name").lower()
                child_age = int(request.form.get(f"child-{index}-age"))
                if request.form.get(f"child-{index}-t-shirt-option") == "true":
                    child_t_shirt_size = request.form.get(f"child-{index}-t-shirt-size")
                elif request.form.get(f"child-{index}-t-shirt-option") == "false":
                    child_t_shirt_size = None
                child_id = insert_child_info(child_name, child_age, child_t_shirt_size, session["parent_id"])
                add_child(child_name, child_id)
                continue

            child_age = int(request.form.get(f"child-{index}-age"))
            if request.form.get(f"child-{index}-t-shirt-option") == "true":
                child_t_shirt_size = request.form.get(f"child-{index}-t-shirt-size")
            elif request.form.get(f"child-{index}-t-shirt-option") == "false":
                child_t_shirt_size = None

            # remap child id to new child name in session if child name has been changed
            if child_new_name != child_old_name:
                session["children_id"][child_new_name] = session["children_id"][child_old_name] 
                del session["children_id"][child_old_name]
            
            # edit child info in the database
            edit_child_info(session["children_id"][child_new_name], child_new_name, child_age, child_t_shirt_size)
        return redirect(url_for("account.edit_info"))
