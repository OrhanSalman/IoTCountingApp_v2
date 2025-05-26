import os
import mimetypes
import json
import time
from flask import Blueprint, Response, jsonify
from flask import Blueprint, jsonify, send_file, url_for, Response, request
from settings import VID_PATH, IMG_PATH
from src.utils.logger import Logger
from src.control import take_snapshot, get_last_inference_frame

# Logger konfigurieren
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs")
logger = Logger("Files", LOG_PATH + "/server.log")

last_frame_request = 0
request_interval = 10

files_bp = Blueprint('files', __name__)

@files_bp.route('/api/video/sample', methods=['GET'])
def get_sample_video():
    sample_video_path = os.path.join(VID_PATH, "capture.mp4")
    if os.path.exists(sample_video_path):
        return send_file(sample_video_path, mimetype='video/mp4')
    else:
        return jsonify({'error': 'Sample video not found'}), 404

@files_bp.route('/api/file/<path:filename>', methods=['GET'])
def get_file(filename):
    if 'simvid_' in filename:
        file_path = os.path.join(VID_PATH, filename)
    else:
        return jsonify({'error': 'File not found'}), 404

    if os.path.exists(file_path):
        # Bestimme den MIME-Typ dynamisch
        mime_type, _ = mimetypes.guess_type(file_path)

        if not mime_type:
            mime_type = 'application/octet-stream'
        
        response = send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=False,
            conditional=True
        )
        
        response.headers['Accept-Ranges'] = 'bytes'
        return response
    else:
        return jsonify({'error': 'File not found'}), 404

@files_bp.route('/api/image', methods=['GET', 'POST'])
def api_image():
    image_path = IMG_PATH + "/capture.jpg"
    
    if request.args.get('snap') == 'true':
        logger.info('Received GET on /api/image with snap=true. Taking Snapshot...')
        take_snapshot()
    else:
        if not os.path.exists(image_path):
            logger.info('Received GET on /api/image with snap=false but no image found. Taking Snapshot...')
            take_snapshot()

    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            image = f.read()
        return Response(image, mimetype='image/jpeg')
    else:
        logger.error('Image not found.')
        return Response(status=404)

@files_bp.route('/api/inference/frame', methods=['GET'])
def get_inference_frame():
    global last_frame_request
    current_time = time.time()

    if current_time - last_frame_request < request_interval:
        return jsonify({'error': 'Too many requests.'}), 429
    
    last_frame_request = current_time

    frame = get_last_inference_frame()
    if frame is not None:
        return Response(frame, mimetype='image/jpeg')
    else:
        return jsonify({'error': 'No frame found.'}), 404
    
@files_bp.route('/api/simulations', methods=['GET', 'DELETE'])
def simulations():
    if request.method == 'GET':
        simulation_data = []
        sim_type = request.args.get('type')

        if sim_type == 'simvid':
            path = VID_PATH
        else:
            return jsonify({'error': 'Invalid type parameter'}), 400

        for filename in os.listdir(path):
            if filename.endswith('.json'):
                base_filename = filename.replace('.json', '')
                json_file = filename
                jpg_file = f"{base_filename}.jpg"
                json_file_path = os.path.join(path, json_file)
                jpg_file_path = os.path.join(path, jpg_file)

                if os.path.exists(jpg_file_path):
                    with open(json_file_path, 'r') as f:
                        json_content = json.load(f)

                    data_entry = {
                        'config': json_content,
                        'image_url': url_for('files.get_file', filename=jpg_file, _external=True),
                    }

                    if sim_type == 'simvid':
                        mp4_file = f"{base_filename}.mp4"
                        mp4_file_path = os.path.join(path, mp4_file)
                        if os.path.exists(mp4_file_path):
                            data_entry['video_url'] = url_for('files.get_file', filename=mp4_file, _external=True)

                    simulation_data.append(data_entry)

        return jsonify(simulation_data)
    
    if request.method == 'DELETE':
        sim_type = request.args.get('type')
        if sim_type == 'simvid':
            path = VID_PATH
        else:
            return jsonify({'error': 'Invalid type parameter'}), 400

        for filename in os.listdir(path):
            if filename.endswith('.json'):
                base_filename = filename.replace('.json', '')
                json_file = filename
                jpg_file = f"{base_filename}.jpg"
                json_file_path = os.path.join(path, json_file)
                jpg_file_path = os.path.join(path, jpg_file)

                if os.path.exists(jpg_file_path):
                    os.remove(jpg_file_path)
                    os.remove(json_file_path)

                if sim_type == 'simvid':
                    mp4_file = f"{base_filename}.mp4"
                    mp4_file_path = os.path.join(path, mp4_file)
                    if os.path.exists(mp4_file_path):
                        os.remove(mp4_file_path)

        return jsonify({'message': 'Deleted all simulation files.'}), 200