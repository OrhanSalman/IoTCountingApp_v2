import os
import json
from flask import Blueprint, request, jsonify
from src.core.cryptography import EncryptionManager
from src.utils.schemes import validate_mqtt_data
from src.utils.logger import Logger

# Logger konfigurieren
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs")
logger = Logger("MQTT", LOG_PATH + "/server.log")

mqtt_bp = Blueprint('mqtt', __name__)
encryption_manager = EncryptionManager()

@mqtt_bp.route('/api/mqtt', methods=['POST', 'DELETE', 'GET'])
def mqtt():
    if request.method == "POST":
        data = request.json
        
        # Lade die vorhandenen Daten, wenn die Datei existiert
        encrypted_data = encryption_manager.load_data("mqtt") if os.path.exists(encryption_manager.MQTT_DATA_FILE) else None
        
        # Bestehende Daten entschlüsseln
        if encrypted_data:
            existing_data = json.loads(encryption_manager.decrypt_data(encrypted_data))
            
            # Altes Passwort aus den bestehenden Daten holen
            existing_password = existing_data.get("password")

            # Prüfen, ob ein neues Passwort gesetzt ist
            new_password = data.get("password")
            
            # Wenn ein Passwort in den Daten vorhanden ist und das neue Passwort ist ***,
            # dann soll das alte Passwort verwendet werden
            if new_password and new_password == "*" * len(new_password):
                data["password"] = existing_password

        # Validierung der Daten
        try:
            validate_mqtt_data(data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        # Speichere die aktualisierten Daten
        encrypted_data = encryption_manager.encrypt_data(json.dumps(data))
        encryption_manager.save_data(encrypted_data, "mqtt")
        
        from src.control import mqtt_client
        status = mqtt_client.is_connected() if mqtt_client and hasattr(mqtt_client, 'is_connected') else False

        return jsonify({"message": "Gespeichert." + (" Neustart des MQTT-Clients empfohlen." if status else "")}), 200
    
    if request.method == "DELETE":
        # Lösche die gespeicherte verschlüsselte Konfiguration
        if os.path.exists(encryption_manager.MQTT_DATA_FILE):
            os.remove(encryption_manager.MQTT_DATA_FILE)
        return jsonify({"message": "Gelöscht."}), 200

    if request.method == "GET":
        # Lade die verschlüsselte Konfiguration
        encrypted_data = encryption_manager.load_data("mqtt")
        if encrypted_data:
            data = json.loads(encryption_manager.decrypt_data(encrypted_data))
            password = data.get("password")
            data["password"] = "*"*len(password) if password else None
            return jsonify(data)
        else:
            return jsonify({"message": "Keine Konfiguration gefunden"}), 404