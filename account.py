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
        return request.form
