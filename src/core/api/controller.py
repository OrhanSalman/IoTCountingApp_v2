class ActionController:
    """
        Controller for handling actions related to the camera, counting, MQTT, and server.
        Used by server.py to manage the state of the application.
    """

    def __init__(self, logger):
        self.logger = logger # server logger
        
    def handle_action(self, action, target, params=None):
        from src.control import (
            start_mqtt_client, stop_mqtt_client, 
            start_stream, stop_stream, 
            take_snapshot, take_video, 
            start_counting, stop_counting, 
            start_model_benchmark, stop_model_benchmark, 
            restart_server
        )
        
        if action not in ['start', 'stop', 'snap', 'video', 'restart']:
            return {"error": "Invalid action."}, 400

        if target not in ['camera', 'counting', 'benchmark', 'mqtt', 'server']:
            return {"error": "Invalid target. Use 'camera', 'counting','benchmark', or 'mqtt'."}, 400

        # Mapping of targets to functions
        action_map = {
            'camera': {
                'start': start_stream,
                'stop': stop_stream,
                'snap': take_snapshot,
                'video': take_video
            },
            'counting': {
                'start': start_counting,
                'stop': stop_counting
            },
            'benchmark': {
                'start': start_model_benchmark,
                'stop': stop_model_benchmark
            },
            'mqtt': {
                'start': start_mqtt_client,
                'stop': stop_mqtt_client
            },
            'server': {
                'restart': restart_server
            }
        }

        # Get the requested function
        func = action_map.get(target, {}).get(action)

        if func is None:
            return {"error": "Action not found for the target."}, 404

        try:
            if target == 'counting' and action == 'start':
                result = func(params or {})
            elif target == 'camera' and action == 'video':
                result = func(
                    duration=params.get('duration', None) if params else None
                )
            else:
                result = func()
            return {"message": result}, 200
        except Exception as e:
            self.logger.error(f"Error during action execution: {e}")
            return {"error": str(e)}, 500