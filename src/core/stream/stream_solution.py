from src.utils.logger import Logger
import json
import time
from settings import (
    LOG_PATH,
    CONFIG_PATH,
    CAM_SOLUTIONS_PATH,
    CV2_INSTALLED,
    PICAMERA2_INSTALLED,
)

"""
    This module is more likely like a factory/test for the camera solutions.
    It will try to open the camera with PiCamera2 and/or OpenCV.
    If one of them is available, it will return the class for the camera stream
"""

logger = Logger("Stream", LOG_PATH + "/stream.log")

def StreamSolution(only_simulation=False, youtube=False):
    try:
        with open(CONFIG_PATH, "r") as file:
            data = json.load(file)
            source = next(config["stream_source"] for config in data["deviceConfigs"])
    except FileNotFoundError:
        logger.warning("config.json not found.")
        return None

    if only_simulation:
        from src.core.stream.cv2.stream_cv2 import CameraStream as cv2_stream
        return cv2_stream
    elif youtube:
        from src.core.stream.cv2.stream_cv2 import CameraStream as cv2_stream
        return cv2_stream
    elif PICAMERA2_INSTALLED and int(source) == 0:
        from src.core.stream.picamera.stream_pi import CameraStream as picamera_stream
        return picamera_stream
    elif CV2_INSTALLED:
        from src.core.stream.cv2.stream_cv2 import CameraStream as cv2_stream
        return cv2_stream
    else:
        error = "No camera solution available."
        return False, error


def initialize_camera_solutions():
    try:
        with open(CAM_SOLUTIONS_PATH, "r") as file:
            cam_solutions = json.load(file)
    except FileNotFoundError:
        cam_solutions = {"cv2": False, "picam2": False}
        with open(CAM_SOLUTIONS_PATH, "w") as file:
            json.dump(cam_solutions, file, indent=2)

    try:
        from src.core.stream.picamera.stream_pi import CameraStream as picamera_stream
        stream = picamera_stream(0, (640, 480), 30, "RGB888")
        time.sleep(1)
        if stream.isOpened():
            ret, frame = stream.capture_image()
            if ret:
                stream.stop_camera()
                cam_solutions["picam2"] = True
                logger.info("picamera2 camera solution is available.")
            else:
                cam_solutions["picam2"] = False
        else:
            cam_solutions["picam2"] = False
    except Exception as e:
        logger.warning(f"Error with picamera2: {e}")
        cam_solutions["picam2"] = False

    if not cam_solutions["picam2"]:
        try:
            from src.core.stream.cv2.stream_cv2 import CameraStream as cv2_stream
            stream = cv2_stream(0, (640, 480), 30, "RGB888")
            time.sleep(1)
            if stream.isOpened():
                ret, frame = stream.capture_image()
                if ret:
                    stream.stop_camera()
                    cam_solutions["cv2"] = True
                    logger.info("cv2 camera solution is available.")
                else:
                    cam_solutions["cv2"] = False
            else:
                cam_solutions["cv2"] = False
        except Exception as e:
            logger.warning(f"Error with cv2: {e}")
            cam_solutions["cv2"] = False

    with open(CAM_SOLUTIONS_PATH, "w") as file:
        json.dump(cam_solutions, file, indent=2)

    return cam_solutions

def load_current_settings():
    return json.load(open(CAM_SOLUTIONS_PATH, "r"))
