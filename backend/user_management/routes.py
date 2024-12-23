from flask import request, jsonify
import requests
from flask_jwt_extended import create_access_token, jwt_required
from auth import hash_password, verify_password
from config import Config

def register_routes(app):

    @app.route('/auth/register', methods=['POST'])
    def register():
        data = request.json
        hashed_password = hash_password(data['password'])
        response = requests.post(f"{Config.DATABASE_URL}/users", json={
            "username": data['username'],
            "password": hashed_password,
        })
        return jsonify(response.json()), response.status_code

    @app.route('/auth/login', methods=['POST'])
    def login():
        data = request.json
        response = requests.get(f"{Config.DATABASE_URL}/users/{data['username']}")
        if response.status_code != 200:
            return jsonify({"message": "User not found"}), 404

        user = response.json()
        if not verify_password(user['password'], data['password']):
            return jsonify({"message": "Invalid credentials"}), 401

        access_token = create_access_token(identity=user['id'])
        return jsonify({"token": access_token}), 200

    @app.route('/auth/logout', methods=['POST'])
    @jwt_required()
    def logout():
        return jsonify({"message": "Logged out successfully"}), 200
