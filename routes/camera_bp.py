from flask import Blueprint

from controllers.CameraController import get_all, get, create, edit, delete, show, turn_off

camera_bp = Blueprint('camera_bp', __name__)

camera_bp.route('/all', methods=['GET'])(get_all)

camera_bp.route('/<int:id>/get', methods=['GET'])(get)

camera_bp.route('/create', methods=['POST'])(create)

camera_bp.route('/<int:id>/show', methods=['GET'])(show)

camera_bp.route('/<int:id>/edit', methods=['POST'])(edit)

camera_bp.route('/<int:id>/delete', methods=['DELETE'])(delete)

camera_bp.route('/<int:id>/turn_off', methods=['POST'])(turn_off)
