from src.core.clients.mqtt import MQTTClient
from src.core.inference.queuemanager import QueueManager

def check_mqtt_client_exists():
    from src.control import mqtt_client
    if isinstance(mqtt_client, MQTTClient) and mqtt_client.is_connected():
        return mqtt_client
    else:
        return False
    
def check_queue_manager_exists():
    from src.control import queue_manager
    if isinstance(queue_manager, QueueManager):
        return queue_manager
    else:
        return False
    
