from flask import Blueprint

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health', methods=['GET'])
def health():
    from src.control import send_status
    return send_status()