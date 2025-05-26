from datetime import datetime, timezone


def ms_to_iso(timestamp_ms):
    dt = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def tracking_entity(session_day, deviceId, counts):

    entity = {
        "id": f"urn:ngsi-ld:TrackingData:{deviceId}:{session_day}",
        "type": "TrackingData",
        "counts": {"type": "Property", "value": {}},
        "partOf": {
            "type": "Relationship", 
            "object": f"urn:ngsi-ld:InferenceSession:{deviceId}:{session_day}"
        },
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ]
    }
    return entity


def create_session_entity(session_day, deviceId, deviceConfigId, started):
    """
    Erstellt eine InferenceSession-Entity und speichert sie optional als Datei.
    
    Args:
        session_day: Das Datum der Session
        deviceId: Die Geräte-ID
        deviceConfigId: Die Konfigurations-ID des Geräts
        started: Der ISO-Zeitstempel des Session-Starts
        save_to_file: Ob die Session in eine Datei gespeichert werden soll (default: True)
    
    Returns:
        dict: Die erstellte Session-Entity
    """
    from settings import INFERENCE_SESSIONS
    import os
    import json
    
    # Die Session-Entity direkt erstellen
    session_entity = {
        "id": f"urn:ngsi-ld:InferenceSession:{deviceId}:{session_day}",
        "type": "InferenceSession",
        "deviceId": {"type": "Property", "value": str(deviceId)},
        "deviceConfigId": {"type": "Property", "value": str(deviceConfigId)},
        "started": {"type": "Property", "value": str(started)},
        "finished": {"type": "Property", "value": 0},
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ]
    }
    
    path = os.path.join(INFERENCE_SESSIONS, str(session_day))
    os.makedirs(path, exist_ok=True)
    
    file = f"session_{deviceId}_{session_day}.json"
    file_path = os.path.join(path, file)
    
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump(session_entity, f, indent=4)
    
    return session_entity


