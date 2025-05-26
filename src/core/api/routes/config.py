import os
import json
from flask import Blueprint, request, jsonify, Response
from settings import CONFIG_PATH, SYSTEM_SETTINGS_PATH, CAM_SOLUTIONS_PATH
from src.utils.schemes import validate_config, validate_settings
from src.utils.tools import generateUUID
from src.utils.logger import Logger

# Logger konfigurieren
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs")
logger = Logger("Config", LOG_PATH + "/server.log")

config_bp = Blueprint('config', __name__)

@config_bp.route('/api/config', methods=['GET', 'POST'])
def config():
    if request.method == "GET":
        with open(CONFIG_PATH, "r") as file:
            return json.load(file)

    elif request.method == "POST":
        data = request.json
        if not data.get("id"):
            data["id"] = generateUUID()

        # points to int
        for roi in data.get("deviceRois", []):
            for point in roi.get("points", []):
                if point.get("x"):
                    point["x"] = int(point["x"])
                if point.get("y"):
                    point["y"] = int(point["y"])

        try:
            validate_config(data)
        except ValueError as e:
            return Response(str(e), status=400)

        with open(CONFIG_PATH, "w") as file:
            json.dump(data, file)

        return Response(status=200)

@config_bp.route('/api/systemsettings', methods=['GET', 'POST'])
def systemsettings():
    from src.utils.generateDefaults import generateDefaultSystemSettingsIfNotExists
    generateDefaultSystemSettingsIfNotExists()
    
    if request.method == "GET":
        with open(SYSTEM_SETTINGS_PATH, "r") as file:
            return json.load(file)
    elif request.method == "POST":
        data = request.json
        try:
            validate_settings(data)
        except ValueError as e:
            return Response(json.dumps({"error": str(e)}), status=400, mimetype='application/json')

        with open(SYSTEM_SETTINGS_PATH, "w") as file:
            json.dump(data, file)
            return Response(json.dumps({"message": "Gespeichert."}), status=200, mimetype='application/json')

