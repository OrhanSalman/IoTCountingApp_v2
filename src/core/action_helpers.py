
import threading
from src.core.inference.exporter import export
from src.utils.logger import Logger


# Some helper functions for the control.py

error = None
export_thread: threading.Thread = None

# Function to export the model with given parameters
def export_model(parameters, logger: Logger):
    global error, export_thread, model_path
    error = None
    model_path = None

    def target():
        global error, model_path
        try:
            logger.info(f"Exporting with parameters: {parameters}")
            model_path = export(**parameters)
        except Exception as e:
            error = str(e)
            logger.error(f"Exception in export: {error}")

    export_thread = threading.Thread(target=target, daemon=True)
    export_thread.start()
    export_thread.join()

    if error:
        logger.error(f"Error in export: {error}")
        return False, error
    return True, model_path


# Function to determine real-time status based on reached and expected FPS
def real_time_status(reached_fps, expected_fps):
    global real_time
    real_time = None

    if expected_fps is None or reached_fps is None:
        return None

    tolerated_fps = expected_fps * 0.9
    acceptable_fps = expected_fps * 0.75

    if reached_fps >= expected_fps:
        real_time = 2 # Real-time
    elif tolerated_fps <= reached_fps < expected_fps:
        real_time = 2 # Real-time
    elif acceptable_fps <= reached_fps < tolerated_fps:
        real_time = 1 # Tolerated
    else:
        real_time = 0 # Not real-time

    return real_time
