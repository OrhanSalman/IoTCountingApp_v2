import os
from flask import Blueprint, request, jsonify
from settings import LOG_PATH
from src.utils.logger import Logger

logger = Logger("Logs", LOG_PATH + "/server.log")

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/api/logs', methods=['GET'])
def logs():
    limit = request.args.get('limit', default=50, type=int)
    date_filter = request.args.get('date', None)  # Optionaler Tag-Parameter im Format YYYY-MM-DD

    if os.path.exists(LOG_PATH):
        log_files = [f for f in os.listdir(LOG_PATH) if f.endswith(".log")]
        # entferne SYSTEM_RESTART.log
        log_files = [f for f in log_files if f != "SYSTEM_RESTART.log"]
        # entferne BENCHMARK
        log_files = [f for f in log_files if f != "BENCHMARK.log"]
        
        if log_files:
            logs_data = []
            for log_file in log_files:
                with open(os.path.join(LOG_PATH, log_file), 'r') as f:
                    lines = f.readlines()

                # Filtere nach Datum, wenn gesetzt
                if date_filter:
                    lines = [line for line in lines if date_filter in line]
                
                # Begrenze die Anzahl der Zeilen nach dem Datum
                last_lines = lines[-limit:]
                last_lines.reverse()
                logs_data.append({log_file: last_lines})
                
            return jsonify(logs_data)
        else:
            return jsonify({"message": "Keine Log-Dateien gefunden."}), 200
    else:
        return jsonify({"message": "Keine Log-Dateien gefunden."}), 200