from flask import (
    Blueprint, 
    Flask, 
    request, 
    redirect, 
    url_for, 
    session, 
    g
)
from decorators import *
from fetch_data import *
from functions import *

account_bp = Blueprint('account', __name__)


@account_bp.route("/edit_info", methods=['GET', 'POST'])
@login_required
def edit_info():
    parent_data = get_parent_info()
    return parent_data

@account_bp.route("/volunteering", methods=['GET', 'POST'])
@login_required
def volunteering():
    if request.method == 'GET':
        parent_id = get_parent_id()
        volunteering_parents = get_volunteering_parents_with_parent_id(parent_id)
        return render_template_with_session("volunteering.html", volunteering_parents=volunteering_parents)
    
    elif request.method == 'POST':
        parent_id = get_parent_id()
        number_of_volunteers = len(get_volunteering_parents_with_parent_id(parent_id))
        if len(request.form) != number_of_volunteers:
            return render_template_with_session("volunteering.html", error=f"Please choose {number_of_volunteers} events")
        else:
            return [request.form]