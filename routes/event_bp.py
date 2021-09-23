from flask import Blueprint

from controllers.EventController import get_all, create, delete, total_by_source, get_image, total_by_month, total_by_score, totals_by_classes

event_bp = Blueprint('event_bp', __name__)

event_bp.route('/all', methods=['GET'])(get_all)

event_bp.route('/create', methods=['POST'])(create)

event_bp.route('/<int:id>/delete', methods=['DELETE'])(delete)

event_bp.route('/totals_by_source', methods=['GET'])(total_by_source)

event_bp.route('/totals_by_month', methods=['GET'])(total_by_month)

event_bp.route('/totals_by_score', methods=['GET'])(total_by_score)

event_bp.route('/totals_by_classes', methods=['GET'])(totals_by_classes)

event_bp.route('/get_image/<name>', methods=['GET'])(get_image)
