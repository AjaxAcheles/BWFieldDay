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
        return render_template("volunteering.html")
    
    elif request.method == 'POST':
        parent_id = get_parent_id()
        number_of_volunteers = get_number_of_volunteers_with_parent_id(parent_id)
        if len(request.form) != number_of_volunteers:
            return render_template("volunteering.html", error=f"Please choose {number_of_volunteers} events")
        else:
            return [request.form]
