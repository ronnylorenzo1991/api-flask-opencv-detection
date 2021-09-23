from flask import Blueprint

from controllers.DefaultController import get_lists

default_bp = Blueprint('default_bp', __name__)

default_bp.route('/lists', methods=['GET'])(get_lists)
