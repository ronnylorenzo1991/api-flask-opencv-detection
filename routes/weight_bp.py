from flask import Blueprint

from controllers.WeightController import get_all, create, edit, delete

weight_bp = Blueprint('weight_bp', __name__)

weight_bp.route('/all', methods=['GET'])(get_all)

weight_bp.route('/create', methods=['POST'])(create)

weight_bp.route('/<int:id>/edit', methods=['POST'])(edit)

weight_bp.route('/<int:id>/delete', methods=['DELETE'])(delete)
