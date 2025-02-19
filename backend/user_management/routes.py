import json
import logging
import os
from datetime import datetime, timedelta
from flask import request, jsonify, session
import requests
from flask_cors import cross_origin
from auth import hash_password, verify_password
from common.middleware import token_required, generate_token, generate_refresh_token, TOKEN_BLACKLIST, redis_client, \
    decode_token
from flask import Blueprint

logging.basicConfig(level=logging.DEBUG)


def register_routes(app):
    @app.route('/auth/register', methods=['POST'])
    @cross_origin(origins=["http://localhost:4200"], supports_credentials=True)
    def register():
        data = request.json
        hashed_password, salt = hash_password(data['password'])
        logging.debug(f"hashed_password: {hashed_password}, type: {type(hashed_password)}")
        logging.debug(f"salt: {salt}, type: {type(salt)}")
        hashed_password = hashed_password.decode('utf-8') if isinstance(hashed_password, bytes) else hashed_password
        salt = salt.decode('utf-8') if isinstance(salt, bytes) else salt
        logging.debug(f"hashed_password: {hashed_password}, type: {type(hashed_password)}")
        logging.debug(f"salt: {salt}, type: {type(salt)}")
        role = data.get("role", "Kunde")
        try:
            role_response = requests.get(f"http://database-management:5001/roles/{role}")
            role_response.raise_for_status()
            role_data = role_response.json()
            role_id = role_data.get("id")

            response = requests.post("http://database-management:5001/users", json={
                "username": data['username'],
                "password": hashed_password,
                "salt": salt,
                "role_id": role_id,
            })
            response.raise_for_status()
            return jsonify(response.json()), response.status_code

        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Service unavailable", "details": str(e)}), 500

    @app.route('/auth/login', methods=['POST'])
    @cross_origin(origins=["http://localhost:4200"], supports_credentials=True)
    def login():
        data = request.json
        response = requests.get(f"http://database-management:5001/users/{data['username']}")
        if response.status_code != 200:
            return jsonify({"message": "User not found"}), 404

        user = response.json()
        logging.debug(user)
        if not verify_password(user['password'], data['password']):
            return jsonify({"message": "Invalid credentials"}), 401

        role_response = requests.get(f"http://database-management:5001/roles/{user['role_id']}")
        role_response.raise_for_status()
        role_data = role_response.json()
        role_name = role_data.get("role_name")
        logging.debug(role_name)

        token = generate_token(username=user['username'], role=role_name)
        refresh_token = generate_refresh_token(username=user['username'])

        #Session speichern
        session['logged_in'] = True
        session['username'] = user['username']
        session['role'] = role_name
        session['token'] = token

        logging.debug(f"Session created for {user['username']} with role {role_name}")

        logging.debug(f"token: {token}")
        logging.debug(f"refresh_token: {refresh_token}")
        logging.debug(f"Session Data After Login: {dict(session)}")
        return jsonify({'role': role_name}), 200


    @app.route('/check-session', methods=['GET'])
    def check_session():
        return jsonify(dict(session))


    @app.route('/auth/logout', methods=['POST'])
    @cross_origin(origins=["http://localhost:4200"], supports_credentials=True)
    @token_required
    def logout():
        token = session.get('token')
        if token:
            # Token zur Redis-Blacklist hinzufügen mit Ablaufzeit
            exp_time = decode_token(token).get('exp')
            # Ablaufzeit in der Zukunft
            exp_time = datetime.utcnow() + timedelta(hours=3)
            # Berechnung der TTL in Sekunden
            ttl = int((exp_time - datetime.utcnow()).total_seconds())
            logging.info(f"Time-to-Live (TTL) in Sekunden: {ttl}")  # Berechne TTL in Sekunden
            redis_client.setex(f"blacklist:{token}", ttl, "revoked")
            logging.debug(f"Token {token} has been added to Redis blacklist with TTL {ttl} seconds")

        session.pop('logged_in', None)
        session.pop('username', None)
        session.pop('role', None)
        session.pop('token', None)
        session.clear()
        return jsonify({"message": "Logged out successfully"}), 200

    @app.route('/auth/token/verify', methods=['POST'])
    def verify_token():
        token = request.json.get('token')
        if token in TOKEN_BLACKLIST:
            return jsonify({"message": "Token is invalid or expired"}), 401
        return jsonify({"message": "Token is valid"}), 200


routes = Blueprint('routes', __name__)
