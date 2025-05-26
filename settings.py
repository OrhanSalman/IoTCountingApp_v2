import os
import json
import secrets
import threading
from dotenv import load_dotenv

load_dotenv(override=True)

"""Global settings for the application. See README.md for more information."""

settings_loaded_event = threading.Event()

APP_DEV_MODE = os.getenv("APP_DEV_MODE", "False").lower() == "true"
APP_PORT = os.getenv("APP_PORT", 5000)
APP_DOMAIN = os.getenv("APP_DOMAIN", "0.0.0.0") 
APP_REDIS_SERVER = os.getenv("APP_REDIS_SERVER", "False").lower() == "true"
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
BENCHED = os.getenv("BENCHED", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(16))

encryption_key_env = os.getenv("ENCRYPTION_KEY")
if encryption_key_env:
    ENCRYPTION_KEY = encryption_key_env
else:
    from cryptography.fernet import Fernet
    ENCRYPTION_KEY = Fernet.generate_key().decode()

from src.env import manage_env_variable
manage_env_variable("SECRET_KEY", SECRET_KEY)
manage_env_variable("ENCRYPTION_KEY", ENCRYPTION_KEY)


""" OIDC settings for OpenID Connect authentication. (Optional, tested with Keycloak) """
USE_OIDC = os.getenv("USE_OIDC", "False").lower() == "true"
OIDC_HOST = os.getenv("OIDC_HOST")
OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID")
OIDC_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET")
OIDC_ISSUER = f"{OIDC_HOST}{os.getenv('OIDC_ISSUER')}"
OIDC_USERINFO_URI = f"{OIDC_HOST}{os.getenv('OIDC_USERINFO_URI')}"
OIDC_TOKEN_INTROSPECTION_URI = f"{OIDC_HOST}{os.getenv('OIDC_TOKEN_INTROSPECTION_URI')}"
OIDC_SERVER_METADATA_URL = f"{OIDC_HOST}{os.getenv('OIDC_SERVER_METADATA_URL')}"
OIDC_SCOPES = os.getenv("OIDC_SCOPES").split(",") if os.getenv("OIDC_SCOPES") else []
OIDC_ID_TOKEN_COOKIE_SECURE = True


""" CORS settings for the application. """
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []
ALLOWED_ORIGINS.append(APP_DOMAIN)
ALLOWED_ORIGINS.append(OIDC_HOST) if USE_OIDC else None
ALLOWED_ORIGINS.append("http://localhost:3000") if APP_DEV_MODE else None


# Define paths
HOME_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(HOME_DIR, "data/imgs")
VID_PATH = os.path.join(HOME_DIR, "data/vids")
LOG_PATH = os.path.join(HOME_DIR, "data/logs")
CONFIG_FOLDER_PATH = os.path.join(HOME_DIR, "data/configs")
YOLO_PREDICTIONS_PATH = os.path.join(HOME_DIR, "runs/detect")
BUILD_PATH = os.path.join(HOME_DIR, "build")
BENCHMARKS_PATH = os.path.join(HOME_DIR, "data/benchmarks")
DATASET_PATH = os.path.join(HOME_DIR, "datasets")
EXPORTS_PATH = os.path.join(HOME_DIR, "exports")
TMP_PATH = os.path.join(HOME_DIR, "data/tmp")
INFERENCE_SESSIONS = os.path.join(HOME_DIR, "data/sessions")

# Define files
CONFIG_PATH = os.path.join(HOME_DIR, "data/configs/config.json")
CAM_SOLUTIONS_PATH = os.path.join(HOME_DIR, "data/configs/cam_solutions.json")
SYSTEM_SETTINGS_PATH = os.path.join(HOME_DIR, "data/configs/settings.json")

# Ensure the directories exist
for path in [CONFIG_FOLDER_PATH, INFERENCE_SESSIONS, IMG_PATH, TMP_PATH, VID_PATH, LOG_PATH, BENCHMARKS_PATH, YOLO_PREDICTIONS_PATH, DATASET_PATH, EXPORTS_PATH]:
    os.makedirs(path, exist_ok=True)


# Ensure the json files exist
for path in [CAM_SOLUTIONS_PATH]:
    if not os.path.exists(path):
        with open(path, "w") as file:
            json.dump({}, file)


# Camera solutions
CV2_INSTALLED = False
PICAMERA2_INSTALLED = False

# Function to load camera solutions from the JSON file
def load_camera_solutions():
    try:
        with open(CAM_SOLUTIONS_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"cv2": False, "picam2": False}

# Function to update camera solutions
def update_camera_solutions():
    from src.core.stream.stream_solution import initialize_camera_solutions, load_current_settings
    initialize_camera_solutions()
    cam_solutions = load_current_settings()
    return cam_solutions



cam_solutions = load_camera_solutions()

# Ensure that cam_solutions is not None and contains the necessary keys
if not cam_solutions.get("cv2", False) and not cam_solutions.get("picam2", False):
    cam_solutions = update_camera_solutions()

CV2_INSTALLED = cam_solutions.get("cv2", False)
PICAMERA2_INSTALLED = cam_solutions.get("picam2", False)



# If you have a CUDA-enabled GPU, you can use it for inference. Ensure to uncomment the lines in the Compose-File.
try:
    import torch
    CUDA_AVAILABLE = torch.cuda.is_available()
    CUDA_DEVICE_COUNT = torch.cuda.device_count()
    CUDA_DEVICE_NAME = torch.cuda.get_device_name()
except Exception as e:
    CUDA_AVAILABLE = False
    CUDA_DEVICE_COUNT = 0
    CUDA_DEVICE_NAME = "None"

# If you have a MPS-enabled GPU on Macbooks with M1 chip and later, you can use it for inference also. This is not tested fully yet, but should run at least with PyTorch. """
try:
    import torch.backends.mps
    MPS_AVAILABLE = torch.backends.mps.is_available() if torch.backends.mps.is_available() else False
    MPS_BUILT = torch.backends.mps.is_built() if torch.backends.mps.is_built() else False
    MPS_MACOS13_OR_NEWER = torch.backends.mps.is_macos13_or_newer() if torch.backends.mps.is_macos13_or_newer() else False
except Exception as e:
    MPS_AVAILABLE = False
    MPS_BUILT = False
    MPS_MACOS13_OR_NEWER = False


from src.utils.generateDefaults import generateDefaultConfigIfNotExists, generateDefaultSystemSettingsIfNotExists
generateDefaultConfigIfNotExists() # This will create a config.json file with default settings
generateDefaultSystemSettingsIfNotExists() # This will create a settings.json file with default settings

from src.utils.tools import load_config
data = load_config(CONFIG_PATH)
DEVICE_ID = data.get("id", "") # ID of the device, you will need it to control the application over MQTT (starting/stopping inference, etc.)
# docker exec -it iot-app /bin/bash
# cd data/configs
# cat settings.json


# Autostart values in settings.json
with open(SYSTEM_SETTINGS_PATH, "r") as file:
    system_settings = json.load(file)
    AUTO_START_INFERENCE = system_settings.get("auto_start_inference", False)
    AUTO_START_MQTT_CLIENT = system_settings.get("auto_start_mqtt_client", False)


if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as file:
        config = json.load(file)
        DEVICE_ID = config.get("id", None)

# Finish loading settings, the app.py will continue from here
settings_loaded_event.set()
