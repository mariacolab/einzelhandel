import logging
import redis
import jwt
import datetime

import requests
from flask import jsonify, session
from functools import wraps
from flask import request


SECRET_KEY = 'your_secret_key'
logging.basicConfig(level=logging.DEBUG)
TOKEN_BLACKLIST = set()
redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)
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
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
            logging.debug(f"Token: {token}")
        if not token:
            return jsonify({"message": "Token is missing"}), 401

        if redis_client.get(f"blacklist:{token}"):
            logging.debug(f"Token {token} is blacklisted")
            return jsonify({"message": "Token has been revoked"}), 401

        try:
            decoded = decode_token(token)
            logging.debug(f"Decoded Token: {decoded}")
            if 'error' in decoded:
                return jsonify({"message": decoded['error']}), 401

            # Überprüfen, ob der Token in der Blacklist ist
            if token in TOKEN_BLACKLIST:
                logging.debug(f"Token {token} is blacklisted")
                return jsonify({"message": "Token has been revoked"}), 401

            request.user = decoded
        except jwt.ExpiredSignatureError as e:
            return jsonify({"message": f"Token expired. Please refresh your token.: {str(e)}"}), 401
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
            username = request.user.get('username')
            logging.debug(f"Loaded username: {username}")
            if not username:
                return jsonify({"message": "Username missing from token"}), 403

            role_name = request.user.get('role')
            logging.debug(f"Loaded user_role: {role_name}")
            if not role_name:
                return jsonify({"message": "Role missing from token"}), 403

            try:
                # Check if the user has at least one required role
                if role_name not in required_roles:
                    logging.debug(f"Role validation failed for {required_roles} and {role_name}")
                    return jsonify({"message": "Access denied"}), 403

            except requests.RequestException as e:
                logging.debug(f"Role validation exception: {e}")
                return jsonify({"message": f"Failed to validate roles {required_roles}", "details": str(e)}), 500

            return f(*args, **kwargs)

        return decorated

    return decorator



