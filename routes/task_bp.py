from flask import Blueprint

from controllers.TaskController import get_all, create, delete, turn_off, edit

task_bp = Blueprint('task_bp', __name__)

task_bp.route('/all', methods=['GET'])(get_all)

task_bp.route('/create', methods=['POST'])(create)

task_bp.route('/<int:id>/edit', methods=['POST'])(edit)

task_bp.route('/<int:id>/delete', methods=['DELETE'])(delete)

task_bp.route('/<int:id>/turn_off', methods=['POST'])(turn_off)