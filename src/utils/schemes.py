from jsonschema import validate, ValidationError

# JSON-Schema for validating incoming changes

MQTT_SETTINGS = {
    "type": "object",
    "properties": {
        "authEnabled": {"type": "boolean"},
        "cleanSession": {"type": "boolean"},
        "clientId": {"type": "string", "format": "uuid"},
        "dataEndpoint": {"type": "string"},
        "host": {"type": "string"},
        "keepAlive": {"type": "integer"},
        "port": {"type": "integer"},
        "qos": {"type": "integer"},
        "tls": {"type": "boolean"},
        "topics": {
            "type": "object",
            "patternProperties": {
                "^action/[^/]+/[^/]+$": {
                    "type": "object",
                    "properties": {
                        "snap": {"type": "string"},
                        "start": {"type": "string"},
                        "stop": {"type": "string"},
                        "video": {"type": "string"},
                        "benchmark_start": {"type": "string"},
                        "benchmark_stop": {"type": "string"},
                        "status": {"type": "string"},
                    },
                    "additionalProperties": False
                }
            },
            "additionalProperties": False
        },
        "willMessage": {"type": "string"},
        "username": {"type": "string"},
        "password": {"type": "string"},
        "deviceName": {"type": "string"},
        "deviceLocation": {"type": "string"},
    },
    "required": ["authEnabled", "deviceName", "deviceLocation", "cleanSession", "clientId", "dataEndpoint", "host", "keepAlive", "port", "qos", "tls", "topics"],
    "additionalProperties": False
}

def validate_mqtt_data(data):
    try:
        validate(instance=data, schema=MQTT_SETTINGS)
    except ValidationError as e:
        raise ValueError(f"Missing fields in MQTT settings: {e.message}")


CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "deviceConfigs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "batch": {"type": "integer"},
                    "conf": {"type": "number"},
                    "deviceType": {"type": "string"},
                    "dynamic": {"type": "boolean"},
                    "imgsz": {"type": "integer"},
                    "iou": {"type": "number"},
                    "keras": {"type": "boolean"},
                    "max_det": {"type": "integer"},
                    "model": {"type": "string"},
                    "modelFormat": {"type": "string"},
                    "nms": {"type": "boolean"},
                    "opset": {"type": ["integer", "null"]},
                    "optimize": {"type": "boolean"},
                    "persist": {"type": "boolean"},
                    "quantization": {"type": "string"},
                    "simplify": {"type": "boolean"},
                    "stream_channel": {"type": "string"},
                    "stream_fps": {"type": ["integer", "string"]},
                    "stream_resolution": {"type": "string"},
                    "stream_source": {"type": "string"},
                    "tracker": {"type": "string"},
                    "vid_stride": {"type": "integer"},
                    "workspace": {"type": "integer"}
                },
                "required": ["id", "batch", "conf","deviceType", "dynamic", "imgsz", "iou", "keras", "max_det", "model", "modelFormat", "nms", "opset", "optimize", "persist", "quantization", "simplify", "stream_channel", "stream_fps", "stream_resolution", "stream_source", "tracker", "vid_stride", "workspace"],
                "additionalProperties": True
            }
        },
        "deviceRois": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "isFormationClosed": {"type": "boolean"},
                    "line_thickness": {"type": "integer"},
                    "deviceId": {"type": "string"},
                    "onRes:": {"type": "string"},
                    "points": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "direction": {"type": "string"},
                                "id": {"type": "string", "format": "uuid"},
                                "roi": {"type": "string", "format": "uuid"},
                                "x": {"type": "number"},
                                "y": {"type": "number"},
                            },
                            "required": ["id", "direction", "roi", "x", "y"],
                            "additionalProperties": False
                        }
                    },
                    "region_color": {"type": "string", "format": "color"},
                    "roiName": {"type": "string"},
                    "tagsInThisRegion": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["id", "isFormationClosed", "line_thickness", "points", "region_color", "roiName", "tagsInThisRegion"],
                "additionalProperties": True
            }
        },
        "deviceTags": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["tags"],
                "additionalProperties": False
            }
        },
        "cuda": {"type": "boolean"},
        "cuda_device_count": {"type": "integer"},
        "cuda_device_name": {"type": "string"},
        "mps_built": {"type": "boolean"},
        "mps_available": {"type": "boolean"}
    },
    "required": ["deviceConfigs", "deviceTags"],
    "additionalProperties": False
}

def validate_config(data):
    try:
        validate(instance=data, schema=CONFIG_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Missing fields in configuration: {e.message}")


SETTINGS_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "auto_start_inference": {"type": "boolean"},
        "auto_start_mqtt_client": {"type": "boolean"},
        "counts_save_intervall": {"type": "integer"},
        "counts_save_intervall_format": {"type": "string"},
        "counts_publish_intervall": {"type": "integer"},
        "counts_publish_intervall_format": {"type": "string"},
        "detect_count_timespan": {"type": "boolean"},
        "blur_humans": {"type": "boolean"},
        
    },
    "required": ["auto_start_inference", "auto_start_mqtt_client",
                 "counts_save_intervall", "counts_save_intervall_format", 
                 "counts_publish_intervall", "counts_publish_intervall_format", 
                 "detect_count_timespan", "blur_humans"],
    "additionalProperties": True
}

def validate_settings(data):
    try:
        validate(instance=data, schema=SETTINGS_SCHEMA)
    except ValidationError as e:
            raise ValueError(f"Missing or invalid fields for settings: {e.message}")

