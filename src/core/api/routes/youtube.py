from flask import Blueprint, request, jsonify

youtube_bp = Blueprint('youtube', __name__)

@youtube_bp.route('/api/youtube', methods=['GET'])
def youtube_stream():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided.'}), 400
    try:
        from src.control import yt_live
        yt_live.set_url(url)
        formats = yt_live.get_formats()
        return jsonify(formats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500