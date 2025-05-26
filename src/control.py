import gc
import json
import os
import time
import threading
from threading import Thread
import cv2
import torch
import numpy as np
import psutil
import GPUtil
from src.core.action_helpers import export_model, real_time_status
from src.core.cryptography import EncryptionManager
from src.core.clients.mqtt import MQTTClient
from src.core.stream.ffmpeg import conversion_in_progress, is_conversion_in_progress
from src.core.stream.yt_live import StreamCatcher
from src.core.stream.stream_solution import StreamSolution
from src.core.inference.benchmark import ModelBenchmark
from src.core.inference.inference import Inference
from src.core.inference.queuemanager import QueueManager
from src.utils.custom_process import CustomProcess
from src.utils.logger import Logger
from src.utils.tools import convert_to_seconds
from src.utils.tools import load_config
from settings import (
    LOG_PATH,
    CONFIG_PATH,
    SYSTEM_SETTINGS_PATH,
    VID_PATH,
    HOME_DIR,
)

logger = Logger("Control", LOG_PATH + "/control.log")

# Global variables, class instances and threads
encryption_manager = EncryptionManager()
yt_live = StreamCatcher()
queue_manager: QueueManager = QueueManager()

mqtt_client: MQTTClient = None
mqtt_thread_instance: Thread = None
mqtt_ready_event = threading.Event()

stream = None
stream_inference: Thread = None

exporting_thread = False
inference: Inference = None
inference_thread: Thread = None

bench: ModelBenchmark = None
bench_process: CustomProcess = None

"""Load and decrypt the configuration data."""
def load_encrypted_config(str):
    encrypted_data = encryption_manager.load_data(str)
    if encrypted_data:
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)
        return json.loads(decrypted_data)
    else:
        #raise FileNotFoundError("Encrypted config file not found.")
        return None
    


def start_stream(only_simulation=False):
    global stream, error, bench_process, yt_live
    error = None

    if stream is None:
        #solutions = load_config(CAM_SOLUTIONS_PATH)
        
        data = load_config(CONFIG_PATH)
        youtube = False
        try:
            stream_source_value = next(config["stream_source"] for config in data["deviceConfigs"])
            stream_url = None
            stream_url_resolution = None

            if stream_source_value == "youtube":
                stream_url = next(config["stream_url"] for config in data["deviceConfigs"])
                stream_url_resolution = next(config["stream_url_resolution"] for config in data["deviceConfigs"])
                yt_live.set_url(stream_url)
                stream = yt_live.set_quality(int(stream_url_resolution))
                stream_url = yt_live.get_video_url()
                resolution, fps = yt_live.get_stream_values()

                # Update the config file with the new stream URL
                data["deviceConfigs"][0]["stream_resolution"] = resolution
                data["deviceConfigs"][0]["stream_fps"] = fps
                with open(CONFIG_PATH, "w") as file:
                    json.dump(data, file, indent=4)

                stream_source_value = stream_url
                youtube = True
            else:
                stream_source_value = int(stream_source_value)

            CameraStream = StreamSolution(only_simulation, youtube)
            if CameraStream is not None:

                if only_simulation:
                    stream_source_value = os.path.join(VID_PATH, "capture.mp4")
                    if not os.path.exists(stream_source_value):
                        warning = "No test video available. Creating a test video..."
                        logger.warning(warning)
                        # Create a test video
                        take_video(15)
                        while not os.path.exists(stream_source_value):
                            time.sleep(1)
                        stream_source_value = os.path.join(VID_PATH, "capture.mp4")
                            
                main_resolution_value = next(config["stream_resolution"] for config in data["deviceConfigs"])
                fps_value = next(config["stream_fps"] for config in data["deviceConfigs"])
                width, height = map(int, main_resolution_value.split('x'))
                stream_channel = next(config["stream_channel"] for config in data["deviceConfigs"])

                stream = CameraStream(source=stream_source_value, main_resolution=(width, height), fps=fps_value, stream_channel=stream_channel)
                stream.start_camera()
                return True, "Stream started."
            else:
                error = "No camera stream solution available."
                logger.error(error)
                return False, error
            
        except Exception as e:
            error = f"Error while starting camera stream: {e}"
            logger.error(error)
            return False, error
    else:
        info = "Camera stream is already active."
        logger.info(info)
        return True, info


def stop_stream():
    global stream
    try:
        if stream is not None:
            stream.stop_camera()
            stream = None
            return True
        return False
    except Exception as e:
        error = f"Error stopping camera: {e}"
        logger.error(error)
        return False, error


# TODO: This needs to be implemented
def stop_exporting():
    pass


def start_counting(params = None):
    global stream, inference, inference_thread, error, exporting_thread, model_path
    error = None
    model_path = None

    if params is None:
        params = {}

    only_simulation = params.get('only_simulation', False)

    if inference_thread is not None and inference_thread.is_alive():
        error = "Counting is already active."
        logger.warning(error)
        return False, error
    if bench_process is not None and bench_process.is_alive():
        error = "Can't start counting, a benchmark is running."
        logger.warning(error)
        return False, error


    if only_simulation:
        stop_stream()
        start_stream(True)
    if stream is None:
        start_stream()
        
    try:
        data = load_config(CONFIG_PATH)
        config = next(config for config in data["deviceConfigs"]) # We had multiple device configs before, for now we only use one

        weights = config['model']
        format = config['modelFormat']
        imgsz = config['imgsz']
        keras = config['keras']
        optimize = config['optimize']
        quantization = config['quantization']
        dynamic = config['dynamic']
        simplify = config['simplify']
        opset = config['opset']
        workspace = config['workspace']
        nms = config['nms']
        batch = config['batch']

    except Exception as e:
        error = f"Error loading config for Counting: {e}"
        logger.error(error)
        raise Exception(error)
    
    # Check if the model exists in the exports directory
    from src.utils.export_helper import check_if_model_exists
    exists, model_path = check_if_model_exists(weights, format, {
        'imgsz': imgsz,
        'keras': keras,
        'optimize': optimize,
        'half': quantization == 'fp16',
        'int8': quantization == 'int8',
        'dynamic': dynamic,
        'simplify': simplify,
        'opset': opset,
        'workspace': workspace,
        'nms': nms,
        'batch': batch
    }) if not format == 'pt' else (False, weights)


    if not exists:
        exporting_thread = True
        if not format == 'pt':
            exp, model_path = export_model({
                'weights': weights,
                'format': format,
                'imgsz': imgsz,
                'keras': keras,
                'optimize': optimize,
                'half': quantization == 'fp16',
                'int8': quantization == 'int8',
                'dynamic': dynamic,
                'simplify': simplify,
                'opset': opset,
                'workspace': workspace,
                'nms': nms,
                'batch': batch,
            }, logger=logger)
            #if err:
            if not exp:
                error = exp
                logger.error(error)
                exporting_thread = False
                return False, error

        exporting_thread = False


    
    inference = Inference(
        model_str=model_path,
        stream=stream,
        only_simulation=only_simulation,
    ) 
    
    def counting_logic():
        global error
        try:
            inference.run()
        except Exception as e:
            error = str(e)
        if only_simulation:
            inference.deactivate()
            import gc
            gc.collect()

    try:
        inference_thread = threading.Thread(target=counting_logic, daemon=True, name="Counting")
        inference_thread.start()
        inference_thread.join(3)
        
        while inference.active and not inference.inference_started_event.is_set():
            inference.inference_started_event.wait(0.5)
        
        #if not inference.inference_started_event.is_set():
        if error or (not inference.inference_started_event.is_set()):
            inference.deactivate()
            inference_thread.join(5)
            inference = None
            inference_thread = None
            if error:
                return False, error
            return False, "Unknown error while starting counting."
        
        if inference_thread.is_alive() and inference.active:
            if only_simulation:
                info = "Simulation started."
            else:
                info = "Counting started."

            logger.info(info)
            return True, info
        else:
            inference.deactivate()
            if inference_thread:
                inference_thread.join()
            inference = None
            inference_thread = None
            if error:
                return False, error
            else:
                return False, "Error while starting counting."

    except Exception as e:
        error = f"Error while starting counting: {e}"
        logger.error(error)
        inference.deactivate()
        inference_thread.join()
        return False, error


def stop_counting():
    global inference, inference_thread
    error = None
    try:
        if inference_thread is not None and inference_thread.is_alive():
            inference.deactivate()
            if inference_thread is not None:
                inference_thread.join()
            inference = None
            inference_thread = None
            info = "Counting stopped."
            logger.info(info)
            gc.collect()
            return True, info
        else:
            logger.warning("Counting is not active.")
            return False
    except Exception as e:
        error = f"Error while stopping counting: {e}"
        logger.error(error)
        return False, error


def take_snapshot():
    global stream
    try:
        if stream is None:
            start_stream()
            time.sleep(1)
        if stream is not None:
            stream.capture_image()
            return True
        else:
            error = "TAKE_SNAPSHOT: Camera stream is not active."
            logger.error(error)
            return False, error
    except Exception as e:
        error = f"TAKE_SNAPSHOT: Exception while taking snapshot: {e}"
        logger.error(error)
        return False, error


def take_video(duration):
    global stream
    if inference is not None and inference_thread.is_alive():
        error = "Can't take video. Counting is active."
        logger.warning(error)
        return False, error
    if stream is not None:
        stop_stream()
        start_stream()
    else:
        start_stream()
    try:
        # status, msg will never arrive here
        status, msg = stream.capture_video(duration)
        stop_stream()
        if status is None and msg is None:
            return True, "Aufzeichnung gestartet."
        return status, msg
    except Exception as e:
        error = f"Exception while taking video: {e}"
        logger.error(error)
        return False, error


def start_model_benchmark():
    """
    Starts a new benchmark process with the given parameters.

    This function first checks if a benchmark process is already running. If so, it logs a warning and returns `False`.
    If no benchmark process is running, it extracts the provided parameters and creates a new instance of `ModelBenchmark`.
    Then, it starts a new CustomProcess that runs the `run` method of the `ModelBenchmark` instance.

    Returns:
        bool: `True` if the benchmark process was successfully started, otherwise `False`.

    Note:
        This function uses multiprocessing to run the benchmark in a separate process.
        This is necessary because the `benchmark` method from `ultralytics` blocks the main thread and does not check for stop events.
        By using a separate process, the benchmark can run independently of the main thread and can be stopped when needed.

        If the device is not a CPU, the function sets the CUDA_VISIBLE_DEVICES environment variable to "0" and uses `torch.multiprocessing` to start the process.
    """
    global bench, bench_process, error
    error = None

    try:
        if bench_process and bench_process.is_alive():
            error = "Can't run benchmark. A benchmark is already running."
            logger.warning(error)
            return False, error
        if inference is not None and inference_thread.is_alive():
            error = "Can't run benchmark. Counting is already active."
            logger.warning(error)
            return False, error

        config = load_config(CONFIG_PATH)
        deviceConfig = config["deviceConfigs"][0]
        torch.device("cpu")

        # Extract the parameters from the deviceConfig
        deviceConfigId = deviceConfig["id"]
        model = deviceConfig["model"]
        quantization = deviceConfig["quantization"]
        imgsz = deviceConfig["imgsz"]
        half = quantization == "fp16"
        int8 = quantization == "int8"
        device = deviceConfig["deviceType"]
        data = None
        verbose = False

        # Create a new instance of ModelBenchmark
        bench = ModelBenchmark(
            deviceConfigId=deviceConfigId,
            model=model,
            imgsz=imgsz,
            half=half,
            int8=int8,
            device=device,
            data=data,
            verbose=verbose
        )

        # If device is CPU, set CUDA_VISIBLE_DEVICES to "" and use a CustomProcess
        if device == "cpu":
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
            torch.cuda.empty_cache()

            bench_process = CustomProcess(target=bench.run, daemon=True, name="Benchmark")
            bench_process.start()
            bench_process.join(5)

            if bench_process.exception:
                exc_type, exc_message = bench_process.exception
                error = f"Exception im Benchmark Process: {exc_type} - {exc_message}"
                logger.error(error)
                bench = None
                bench_process = None
                return False, exc_message
            elif not bench_process.is_alive():
                error = "Benchmark Prozess konnte nicht aktiviert werden."
                logger.error(error)
                bench = None
                bench_process = None
                return False, error

        else:
            #if device != "cpu" and not CUDA_AVAILABLE:
            #    #raise ValueError("Cuda not available. Use CPU instead.")
            #    error = "GPU/CUDA ist auf diesem Gerät nicht verfügbar."
            #    logger.error(error)
            #    return False, error
            
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
            import torch.multiprocessing as mp
            try:
                mp.set_start_method('spawn', force=True)
            except Exception as e:
                pass
            
            # Starte den Benchmark in einem torch.multiprocessing.Process
            bench_process = mp.Process(target=bench.run, name="Benchmark")
            bench_process.start()
            bench_process.join(5)

            exit_code = bench_process.exitcode
            if exit_code is not None and exit_code != 0:
                error = f"CUDA: Benchmark exited with code {exit_code}"
                logger.error(error)
                bench = None
                bench_process = None
                return False, error
            
        # Optional, check if the process is alive
        if not bench_process.is_alive():
            error = "Benchmark process was started but has stopped."
            logger.info(error)
            bench_process.terminate()
            bench = None
            bench_process = None
            return False, error
        
        torch.cuda.empty_cache()

        return True, "Benchmarks started."


    except Exception as e:
        error = f"Error starting benchmark: {e}"
        logger.error(error)
        return False, error
        

def stop_model_benchmark():
    global bench, bench_process

    try:
        if bench_process is not None and bench_process.is_alive():
            bench.deactivate() 
            bench_process.terminate()
            bench_process.join()
            bench = None
            bench_process = None
            logger.info("Benchmarks stopped.")
            return True
        else:
            error = "No active benchmarks to stop."
            logger.warning(error)
            return False, error
    except Exception as e:
        error = f"Error stopping benchmarks: {e}"
        logger.error(error)
        return False, error


def get_gpu_status():
    """
    Returns the status of the GPU, including usage, temperature, and VRAM utilization.
    """
    gpus = GPUtil.getGPUs()
    gpu_status = []

    for gpu in gpus:
        gpu_info = {
            'id': gpu.id,
            'name': gpu.name,
            'load': gpu.load * 100,
            'temperature': gpu.temperature,
            'memory_total': gpu.memoryTotal,
            'memory_used': gpu.memoryUsed,
            'memory_free': gpu.memoryFree,
        }
        gpu_status.append(gpu_info)

    return gpu_status


""" Returns the health status of the system. """
def send_status():
    global mqtt_client, stream, inference, bench_process, conversion_in_progress, queue_manager, exporting_thread

    inference_status = inference is not None and inference.active if inference else False
    benchmark_status = bench_process is not None and bench_process.is_alive() if bench_process else False

    expected_fps = stream.get_details()["fps"] if stream is not None and hasattr(stream, 'get_details') else None
    reached_fps = inference.get_performance_metrics()["avg_fps"] if inference_status else None

    cpu_percent = psutil.cpu_percent() if hasattr(psutil, 'cpu_percent') else None

    #sensor_temps = psutil.sensors_temperatures() if hasattr(psutil, 'sensors_temperatures') else {}
    #cpu_temp = sensor_temps.get('coretemp', []) if sensor_temps else []
    #cpu_temp = cpu_temp[0].current if cpu_temp else None

    ram_available = psutil.virtual_memory().available * 100 / psutil.virtual_memory().total
    ram_total = psutil.virtual_memory().total / 1024 / 1024
    ram_used = psutil.virtual_memory().used / 1024 / 1024

    gpu_status = get_gpu_status()

    cpu = {
        'percent': cpu_percent,
        #'temp': cpu_temp
    }

    ram = {
        'available': ram_available,
        'total': ram_total,
        'used': ram_used
    }

    status = {
        'mqtt': {
            'status': isinstance(mqtt_client, MQTTClient),
            'connected': mqtt_client.is_connected() if mqtt_client and hasattr(mqtt_client, 'is_connected') else False,
            'published_msg': mqtt_client.get_published_messages_since_start() if mqtt_client and hasattr(mqtt_client, 'get_published_messages_since_start') else None
        },
        'camera': {
            'status': stream is not None and stream.isOpened() if stream else False,
            'details': stream.get_details() if stream is not None and hasattr(stream, 'get_details') else None,
            'is_capturing': stream.capturing() if stream is not None and hasattr(stream, 'capturing') else False,
        },
        'inference': {
            'status': inference_status,
            'exporter': exporting_thread,
            'simulation': inference_status and ((inference.only_simulation) if inference else False),
            'details': inference_status and (inference.get_performance_metrics() if inference else None) or False,
            'queue_size': queue_manager.get_counts_queue_size() if isinstance(queue_manager, QueueManager) else 0,
            'real_time': inference_status and real_time_status(reached_fps, expected_fps) if reached_fps is not None and expected_fps is not None else None,
            'simulation_frames_to_process': stream.get_total_frames() if stream is not None and hasattr(stream, 'get_total_frames') else None,
        },
        'benchmark': {
            'status': benchmark_status
        },
        'video_converter': is_conversion_in_progress(),
        'cpu': cpu,
        'ram': ram,
        'gpu': gpu_status
    }

    return status


def start_mqtt_client():
    global mqtt_client, mqtt_thread_instance, mqtt_ready_event

    if mqtt_ready_event is None:
        mqtt_ready_event = threading.Event()

    if mqtt_thread_instance is not None and mqtt_thread_instance.is_alive() and mqtt_client.is_connected():
        info = "MQTT client is already active and connected."
        #logger.info(info)
        return False, info

    status = False
    msg = None

    config = load_encrypted_config("mqtt")
    system_settings = load_config(SYSTEM_SETTINGS_PATH)

    if not config:
        warning = "No MQTT configuration found."
        logger.warning(warning)
        return False, warning

    client_id = str(config.get("clientId"))
    host = str(config.get("host"))
    port = int(config.get("port"))
    username = str(config.get("username"))
    password = str(config.get("password"))
    tls = bool(config.get("tls", False))
    willMsg = str(config.get("willMessage"))
    keepalive = int(config.get("keepAlive", 60))
    cleanSession = bool(config.get("cleanSession", False))
    qos = int(config.get("qos", 0))
    authEnabled = bool(config.get("authEnabled", False))
    topics = config.get("topics", {})
    counts_publish_intervall = system_settings['counts_publish_intervall']
    counts_publish_intervall = convert_to_seconds(counts_publish_intervall, system_settings['counts_publish_intervall_format'])
    deviceName = config.get("deviceName", None)
    deviceLocation = config.get("deviceLocation", None)
    dataendpoint = config.get("dataEndpoint", None)
    dataendpoint = dataendpoint.replace("+", deviceName, 1)
    dataendpoint = dataendpoint.replace("+", deviceLocation, 1)

    def mqtt_thread():
        global mqtt_client
        nonlocal status, msg

        mqtt_client = MQTTClient(dataendpoint, counts_publish_intervall, topics, authEnabled, client_id, host, port, username, password, tls, willMsg, qos, cleanSession, keepalive)
        status, msg = mqtt_client.start()
        mqtt_ready_event.set()

    mqtt_thread_instance = threading.Thread(target=mqtt_thread, daemon=True, name="MQTT")
    mqtt_thread_instance.start()
    mqtt_ready_event.wait()

    if status:
        from src.core.clients.grafana import create_dashboard
        create_dashboard(deviceLocation, deviceName)

    
    return status, msg


def stop_mqtt_client():
    global mqtt_client, mqtt_thread_instance
    try:
        if mqtt_client is not None:
            mqtt_client.client.disconnect()
            mqtt_thread_instance.join()
            mqtt_ready_event.clear()
            mqtt_client = None
            mqtt_thread_instance = None
            logger.info("MQTT client stopped.")
            return True
        else:
            error = "Cant stop MQTT client. It is not running."
            logger.warning(error)
            return False, error
    except Exception as e:
        error = f"Error while stopping MQTT client: {e}"
        logger.error(error)
        return False, error


def restart_server():
    try:
        restart_file_path = HOME_DIR + "/restart.flag"
        # Touch the file to signal a server restart
        with open(restart_file_path, 'w') as f:
            f.write('Restart requested ...')

        info = "Restart successfully signaled."
        logger.info(info)
        
        return True, info
    except Exception as e:
        error = f"Error signaling server restart: {str(e)}"
        logger.error(error)
        return False, error


""" Returns the last inference frame. For visualization purposes. """
def get_last_inference_frame():
    global inference
    if inference is not None:
        sim = inference.is_simulation()
        if sim:
            return None
        
        #inference.change_vars(True, True) # TODO: This does not work expectedly
        frame = inference.get_last_frame()

        if isinstance(frame, np.ndarray) and frame.size > 0:
            ret, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
        else:
            frame = None
        #inference.change_vars(False, False) # TODO: This does not work expectedly
        return frame
    return None
