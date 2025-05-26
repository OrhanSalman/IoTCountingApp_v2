from datetime import datetime
import os
import json
import time
import urllib.parse
import requests
from flask import Blueprint, jsonify, redirect, request, session, url_for, Response
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError, MismatchingStateError
from settings import OIDC_ISSUER, OIDC_CLIENT_ID, OIDC_CLIENT_SECRET, OIDC_USERINFO_URI, APP_DOMAIN, USE_OIDC, OIDC_SCOPES, OIDC_SERVER_METADATA_URL, OIDC_TOKEN_INTROSPECTION_URI
from src.utils.logger import Logger
from settings import LOG_PATH


logger = Logger("Auth", LOG_PATH + "/server.log")

auth_bp = Blueprint('auth', __name__)
oauth = None

# Library
def init_oauth(app):
    global oauth
    if USE_OIDC:
        oauth = OAuth(app)
        oauth.register(
            name='oidc',
            client_id=OIDC_CLIENT_ID,
            client_secret=OIDC_CLIENT_SECRET,
            server_metadata_url=OIDC_SERVER_METADATA_URL,
            client_kwargs={
                'scope': OIDC_SCOPES,
            }
        )

"""Introspect Token
    Args:
        token (str): The token to be introspected.
    Returns:
        bool: True if the token is valid, False otherwise.
"""
def introspect_token(token):
    if not USE_OIDC:
        return True
    
    introspect_url = OIDC_TOKEN_INTROSPECTION_URI
    client_id = OIDC_CLIENT_ID
    client_secret = OIDC_CLIENT_SECRET
    data = {
        'token': token,
        "grant_type": "client_credentials",
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(introspect_url, data=data)

    if response.status_code == 200:
        token_info = response.json()

        if token_info.get('active'):
            exp = token_info.get('exp')
            if exp and exp > int(time.time()):
                return True # Token is valid and not expired
            else:
                return False # Token is expired
        else:
            return False # Token is not active
    else:
        return False # Introspection failed, treat as invalid token


@auth_bp.route('/login')
def login():
    if not USE_OIDC:
        return jsonify({"message": "OIDC not configured."}), 200
    redirect_uri = url_for('auth.auth', _external=True)
    return oauth.oidc.authorize_redirect(redirect_uri)


@auth_bp.route('/auth')
def auth():
    if not USE_OIDC:
        return jsonify({"message": "OIDC not configured."}), 200
    
    try:
        token = oauth.oidc.authorize_access_token()
    except MismatchingStateError as e:
        logger.error(f"MismatchingStateError: {str(e)}")
        return jsonify({"error": "Authentication failed due to a CSRF error.", "details": "State parameter mismatch."}), 401
    except OAuthError as e:
        logger.error(f"OAuthError: {str(e)}")
        return jsonify({"error": "Authentication failed.", "details": str(e)}), 401
    
    if token:
        userinfo_url = OIDC_USERINFO_URI
        userinfo_response = requests.get(userinfo_url, headers={"Authorization": f"Bearer {token['access_token']}"})

        if userinfo_response.status_code == 200:
            userinfo = userinfo_response.json()
            session['oidc_auth_token'] = {
                'access_token': token['access_token'],
                'refresh_token': token.get('refresh_token'),
                'expires_at': time.time() + token['expires_in'],
                'id_token': token['id_token'],
                **userinfo
            }
            return redirect('/')
    
    return Response("Authentication failed.", status=401)


@auth_bp.route('/signout', methods=['POST'])
def logout():
    if request.method == 'POST':
        if not USE_OIDC:
            return jsonify({"message": "OIDC not configured."}), 200

        id_token = session.get('oidc_auth_token', {}).get('id_token')

        if id_token:
            logout_url = (
                f"{OIDC_ISSUER}/protocol/openid-connect/logout?"
                f"id_token_hint={urllib.parse.quote(id_token)}&"
                f"post_logout_redirect_uri={urllib.parse.quote(APP_DOMAIN + '/', safe='')}"
            )
            try:
                logout_response = requests.get(logout_url)

                print(f"Logout URL: {logout_response}")

                if logout_response.status_code == 200:
                    session.clear()
                    logger.info("User logged out successfully.")
                    return Response(url_for('auth.login'), status=200)
                else:
                    logger.error(f"Logout failed with status code: {logout_response.status_code}")
                    return Response("Logout failed on external server.", status=500)
            except Exception as e:
                logger.error(f"Error during logout request: {str(e)}")
                return Response(f"Error during logout request: {str(e)}", status=500)

        else:
            logger.warning("No ID token found in session for logout.")
            return Response("No Session found.", status=404)


@auth_bp.route('/api/userinfo', methods=['GET'])
def userinfo():
    if not USE_OIDC:
        return jsonify({"message": "OIDC not configured."}), 200
    
    if not refresh_access_token():
        return jsonify({"error": "Token refresh failed."}), 401
    
    oidc_session_info = {
        "sub": session['oidc_auth_token'].get("sub"),
        "email_verified": session['oidc_auth_token'].get("email_verified"),
        "roles": session['oidc_auth_token'].get("roles"),
        "groups": session['oidc_auth_token'].get("groups"),
        "preferred_username": session['oidc_auth_token'].get("preferred_username"),
        "given_name": session['oidc_auth_token'].get("given_name"),
        "family_name": session['oidc_auth_token'].get("family_name"),
        "email": session['oidc_auth_token'].get("email"),
        "token_expires_at": session['oidc_auth_token'].get("expires_at"),
    }

    return json.dumps(oidc_session_info), 200


def refresh_access_token():
    try:
        token_endpoint = f"{OIDC_ISSUER}/protocol/openid-connect/token"
        refresh_token = session['oidc_auth_token'].get('refresh_token')
        
        if not refresh_token:
            return False
            
        data = {
            'grant_type': 'refresh_token',
            'client_id': OIDC_CLIENT_ID,
            'client_secret': OIDC_CLIENT_SECRET,
            'refresh_token': refresh_token
        }
        
        response = requests.post(token_endpoint, data=data)
        
        if response.status_code == 200:
            new_token = response.json()
            
            userinfo_response = requests.get(
                OIDC_USERINFO_URI,
                headers={"Authorization": f"Bearer {new_token['access_token']}"}
            )
            
            if userinfo_response.status_code == 200:
                userinfo = userinfo_response.json()
                session['oidc_auth_token'] = {
                    'access_token': new_token['access_token'],
                    'refresh_token': new_token.get('refresh_token', refresh_token),
                    'expires_at': time.time() + new_token['expires_in'],
                    'id_token': new_token.get('id_token'),
                    **userinfo
                }
                return True
        return False
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        return False