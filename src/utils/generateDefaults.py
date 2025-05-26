import os, json
from src.utils.tools import generateUUID
from settings import (
    CV2_INSTALLED,
    PICAMERA2_INSTALLED,
    CUDA_AVAILABLE,
    CUDA_DEVICE_COUNT,
    CUDA_DEVICE_NAME,
    MPS_AVAILABLE,
    MPS_BUILT,
    CONFIG_PATH,
    SYSTEM_SETTINGS_PATH
)

id = generateUUID()

config_data = {
    "id": id,
    "deviceConfigs": [
        {
            "id": generateUUID(),
            "batch": 1,
            "conf": 0.25,
            "deviceType": "cpu",
            "dynamic": False,
            "imgsz": 320,
            "iou": 0.7,
            "keras": False,
            "max_det": 300,
            "model": "yolo11n",
            "modelFormat": "pt",
            "nms": False,
            "opset": None,
            "optimize": False,
            "persist": False,
            "quantization": "default",
            "simplify": False,
            "stream_channel": "RGB888",
            "stream_fps": 30,
            "stream_resolution": "640x480",
            "stream_source": "0" if CV2_INSTALLED or PICAMERA2_INSTALLED else "youtube",
            "tracker": "botsort.yaml",
            "vid_stride": 1,
            "workspace": 4,
            "webcam_available": True if CV2_INSTALLED or PICAMERA2_INSTALLED else False,
        }
    ],
    "deviceTags": [
        {
            "tags": ["0", "1", "2", "3", "5",]
        }
    ],
    "cuda": CUDA_AVAILABLE,
    "cuda_device_count": CUDA_DEVICE_COUNT,
    "cuda_device_name": CUDA_DEVICE_NAME,
    "mps_available": MPS_AVAILABLE,
    "mps_built": MPS_BUILT,
}


def generateDefaultConfigIfNotExists():
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as file:
            json.dump(config_data, file)


system_settings_data = {
    "device_id": id,
    "auto_start_inference": False,
    "auto_start_mqtt_client": False,
    "counts_save_intervall": 1,
    "counts_save_intervall_format": "min",
    "counts_publish_intervall": 1,
    "counts_publish_intervall_format": "min",
    "detect_count_timespan": False,
    "blur_humans": True,
}

def generateDefaultSystemSettingsIfNotExists():
    if not os.path.exists(SYSTEM_SETTINGS_PATH):
        with open(SYSTEM_SETTINGS_PATH, "w") as file:
            json.dump(system_settings_data, file)