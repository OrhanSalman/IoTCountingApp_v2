import multiprocessing
import os
import signal
import settings
import asyncio
import gc
from src.utils.logger import Logger
from src.control import start_counting, start_model_benchmark, start_mqtt_client, stop_stream
from src.core.api.server import app
from hypercorn.config import Config
from hypercorn.asyncio import serve

multiprocessing.set_start_method('spawn', force=True)

cleanup_done = False

logger = Logger("Main", settings.LOG_PATH + "/main.log")


def create_app():
    return app

"""Start services based on environment variables."""
def initialize_services():

    if settings.AUTO_START_MQTT_CLIENT:
        logger.info("Autostart des MQTT Clients ist aktiviert.")
        start_mqtt_client()

    if not settings.BENCHED and not settings.APP_DEV_MODE:
        logger.info("Starte erstes Benchmarking. Ein Neustart im Anschluss ist empfohlen.")
        start_model_benchmark()
    elif settings.AUTO_START_INFERENCE:
        logger.info("Autostart der Inferenz ist aktiviert.")
        start_counting()
    else:
        pass


# Konfiguration für Hypercorn
config = Config()
config.bind = [f"0.0.0.0:{settings.APP_PORT}"]
config.workers = 1 # Leave it as it is, otherwise modules won't find each other (e.g. inference and camera)
config.read_timeout = 30
config.startup_timeout = 30
config.shutdown_timeout = 30
config.keep_alive_timeout = 5
config.graceful_timeout = 30
config.use_reloader = False
config.loglevel = "info"


def cleanup():
    global cleanup_done
    if cleanup_done:
        return True, None

    from src.control import stop_counting, stop_model_benchmark, stop_mqtt_client
    logger.info("Cleanup started...")
    try:
        stop_counting()
        stop_mqtt_client()
        stop_model_benchmark()
        stop_stream()
        
        gc.collect()
        if settings.CUDA_AVAILABLE:
            try:
                import torch
                torch.cuda.empty_cache()
            except Exception:
                pass
        
        logger.info("Cleanup finished.")
        cleanup_done = True
        return True, None
    except Exception as e:
        error = f"Error while doing cleanup: {e}"
        logger.error(error)
        return False, error


def force_kill():
    """Force SIGKILL the process if SIGTERM fails.""" 
    logger.error("SIGTERM failed, trying SIGKILL...")
    os.kill(os.getpid(), signal.SIGKILL)

def signal_handler(sig):
    """Register signal handler for SIGINT and SIGTERM."""
    global cleanup_done
    if cleanup_done:
        return
    
    # RAM Release
    gc.collect()

    logger.info(f"Signal {sig} received, trying to shut down application...")
    success, error_message = cleanup()
    
    if not success:
        logger.error(f"Cleanup failed: {error_message}")
    else:
        logger.info("Application shut down cleanly.")
    exit(0)



if __name__ == "__main__":
    """Main entry point for the application."""

    # Ensure that the settings are loaded before we start the application.
    settings.settings_loaded_event.wait()
    # Create the application instance
    application = create_app()
    initialize_services()

    # Signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)



    try:
        # Write the PID of the process to a file for the restart script
        with open("server.pid", "w") as f:
            f.write(str(os.getpid()))

        """ PRODUCTION/DEVELOPMENT MODE """
        if settings.APP_DEV_MODE: # Development mode, debugging
            application.run(host="0.0.0.0", port=settings.APP_PORT, debug=True, use_reloader=True)
        else:
            asyncio.run(serve(application, config=config)) # Production mode with Hypercorn

    except Exception as e:
        logger.error(f"Error while running server: {e}")
    finally:
        success, error_message = cleanup()
        if not success:
            logger.error(f"Error during final cleanup: {error_message}")

        if os.path.exists("server.pid"):
            os.remove("server.pid")
            logger.info("PID file removed.")

        logger.info("Application terminated.")
