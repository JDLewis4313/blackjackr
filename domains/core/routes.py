from flask import Blueprint, render_template
from flask_login import current_user

core_bp = Blueprint('core', __name__)

@core_bp.route('/')
def index():
    return render_template('core/index.html', user=current_user)
