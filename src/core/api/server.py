
import time
from redis import Redis
from flask import (Flask, jsonify, redirect, request, send_from_directory, session, url_for)
from flask_cors import CORS
from flask_session import Session
from src.core.cryptography import EncryptionManager
from src.utils.logger import Logger
from settings import APP_DEV_MODE, LOG_PATH, BUILD_PATH, REDIS_HOST, REDIS_PORT, APP_REDIS_SERVER, SECRET_KEY, ALLOWED_ORIGINS, USE_OIDC
from src.core.api.controller import ActionController
from src.core.api.routes.config import config_bp
from src.core.api.routes.files import files_bp
from src.core.api.routes.mqtt import mqtt_bp
from src.core.api.routes.health import health_bp
from src.core.api.routes.logs import logs_bp
from src.core.api.routes.action import action_bp
from src.core.api.routes.auth import auth_bp, init_oauth, introspect_token
from src.core.api.routes.benchmarks import benchmarks_bp
from src.core.api.routes.youtube import youtube_bp


logger = Logger("Server", LOG_PATH + "/server.log")

encryption_manager = EncryptionManager()

ALLOWED_ORIGINS = ALLOWED_ORIGINS
SECRET_KEY = SECRET_KEY
action_controller = ActionController(logger)

app = Flask(__name__, static_folder=BUILD_PATH, static_url_path="/")
app.debug = APP_DEV_MODE
app.config['SECRET_KEY'] = SECRET_KEY

if not APP_DEV_MODE and APP_REDIS_SERVER:
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_REDIS'] = Redis.from_url(f'redis://{REDIS_HOST}:{REDIS_PORT}')
    Session(app)

CORS(
    app,
    resources={r"/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
)

app.register_blueprint(auth_bp)
app.register_blueprint(config_bp)
app.register_blueprint(files_bp)
app.register_blueprint(mqtt_bp)
app.register_blueprint(action_bp)
app.register_blueprint(health_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(benchmarks_bp)
app.register_blueprint(youtube_bp)


if USE_OIDC:
    init_oauth(app)


@app.before_request
def require_auth():
    if not USE_OIDC:
        return
        
    # Endpoints that do not require authentication
    if request.endpoint in ['auth.login', 'auth.auth', 'auth.logout']:
        return  # No authentication for these routes

    
    # Check if the user has a valid session
    if 'oidc_auth_token' in session:
        token = session['oidc_auth_token'].get('access_token')
        expires_at = session['oidc_auth_token'].get('expires_at')
        
        # If token exists but is expired
        if not token or (expires_at and time.time() > expires_at):
            session.clear()  # Clear session
            return redirect(url_for('auth.login'))
            
        # Token introspection to verify validity
        if not introspect_token(token):
            session.clear()
            return redirect(url_for('auth.login'))
            
        return  # User is logged in and token is valid

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        if introspect_token(token):
            return
        else:
            return jsonify({"error": "Unauthorized"}), 401
            
    # No valid authentication, redirect to login
    return redirect(url_for('auth.login'))

@app.route("/")
def serve():
    if not USE_OIDC:
        return send_from_directory(app.static_folder, "index.html")
    if 'oidc_auth_token' not in session:
        return redirect(url_for('auth.login'))
    return send_from_directory(app.static_folder, "index.html")


@app.errorhandler(404)
def not_found_error(error):
    return send_from_directory(app.static_folder, "index.html")


@app.route('/api/action', methods=['POST'])
def action():
    data = request.json
    action = data.get('action')
    target = data.get('target')
    params = data.get('params', {})
    
    result, status_code = action_controller.handle_action(action, target, params)
    return jsonify(result), status_code
