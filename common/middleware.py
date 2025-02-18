import logging
import os
import jwt
import datetime

import requests
from flask import jsonify, session
from functools import wraps
from flask import request
import redis

# Lade das Redis-Passwort aus der Umgebung
redis_password = os.getenv("REDIS_PASSWORD", None)

redis_client = redis.StrictRedis(
    host='redis',
    port=6379,
    db=0,
    decode_responses=True,
    password=redis_password  # Passwort setzen
)

SECRET_KEY = 'your_secret_key'
logging.basicConfig(level=logging.DEBUG)
TOKEN_BLACKLIST = set()

def generate_token(username, role):
    return jwt.encode({
        'username': username,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    }, SECRET_KEY, algorithm='HS256')


def generate_refresh_token(username):
    return jwt.encode({
        'username': username,
        'type': 'refresh',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, SECRET_KEY, algorithm='HS256')


def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        logging.debug(f"Session before access: {dict(session)}")  # DEBUG
        token = session.get('token')  # Token aus der Session holen
        if not token:
            return jsonify({"message": "Unauthorized: No active session"}), 401

        logging.debug(f"Token from session: {token}")

        if redis_client.get(f"blacklist:{token}"):
            logging.debug(f"Token {token} is blacklisted")
            return jsonify({"message": "Token has been revoked"}), 401

        try:
            decoded = decode_token(token)
            logging.debug(f"Decoded Token: {decoded}")
            if 'error' in decoded:
                return jsonify({"message": decoded['error']}), 401

            request.user = decoded  # Benutzerinformationen im Request speichern

        except jwt.ExpiredSignatureError as e:
            return jsonify({"message": f"Token expired. Please log in again: {str(e)}"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"message": f"Invalid token: {str(e)}"}), 401
        except Exception as e:
            return jsonify({"message": f"Token validation failed: {str(e)}"}), 401

        return f(*args, **kwargs)

    return decorated


def role_required(*required_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            role_name = session.get('role')  # Rolle aus der Session holen
            logging.debug(f"Session role: {role_name}")

            if not role_name:
                return jsonify({"message": "Unauthorized: No role found"}), 403

            if role_name not in required_roles:
                logging.debug(f"Access denied for role {role_name}, required: {required_roles}")
                return jsonify({"message": "Access denied"}), 403

            return f(*args, **kwargs)

        return decorated

    return decorator


def get_user_role_from_token():
    decoded_token = decode_token(session.get('token'))
    if 'error' in decoded_token:
        logging.debug(f"Error decoding token: {decoded_token['error']}")
        return None
    return decoded_token.get('role')
