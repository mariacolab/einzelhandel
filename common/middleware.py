import jwt
import datetime
from flask import jsonify
from functools import wraps
from flask import request

SECRET_KEY = 'your_secret_key'

def generate_token(username, role):
    return jwt.encode({{
        'username': username,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }}, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {{"error": "Token expired"}}
    except jwt.InvalidTokenError:
        return {{"error": "Invalid token"}}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({{"message": "Token is missing"}}), 401
        decoded = decode_token(token)
        if 'error' in decoded:
            return jsonify({{"message": decoded['error']}}), 401
        request.user = decoded
        return f(*args, **kwargs)
    return decorated

# def role_required(required_role):
#     def decorator(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             if request.user.get('role') != required_role:
#                 return jsonify({{"message": "Access denied"}}), 403
#             return f(*args, **kwargs)
#         return decorated
#     return decorator

def role_required(*required_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_roles = request.user.get('roles', [])
            # Check if user has at least one required role
            if not any(role in user_roles for role in required_roles):
                return jsonify({"message": "Access denied"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator