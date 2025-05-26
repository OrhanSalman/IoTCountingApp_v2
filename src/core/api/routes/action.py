from flask import Blueprint, request, jsonify

action_bp = Blueprint('action', __name__)

"""Action Controller
    Handle the incoming API requests from the UI and call the appropriate methods in the ActionController (controller.py).
    Args:
        action (str): The action to be performed.
        target (str): The target of the action.
        params (dict): The parameters for the action.

    Example:
        {
            "action": "start",
            "target": "camera",
            "params": {}
    Returns:
        dict: The result of the action.
        int: The HTTP status code.
"""
@action_bp.route('/api/action', methods=['POST'])
def action():
    from src.core.api.controller import ActionController
    from src.utils.logger import Logger
    import os
    
    # Logger konfigurieren
    LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs")
    logger = Logger("Action", LOG_PATH + "/server.log")
    
    action_controller = ActionController(logger)
    
    data = request.json
    action = data.get('action')
    target = data.get('target')
    params = data.get('params', {})
        
    result, status_code = action_controller.handle_action(action, target, params)
    return jsonify(result), status_code