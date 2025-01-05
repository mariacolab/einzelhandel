from flask import request, jsonify
import requests
from auth import hash_password, verify_password
from common.middleware import token_required, generate_token
from flask import Blueprint


def register_routes(app):
    @app.route('/auth/register', methods=['POST'])
    def register():
        data = request.json
        hashed_password, salt = hash_password(data['password'])
        print(f"hashed_password: {hashed_password}, type: {type(hashed_password)}")
        print(f"salt: {salt}, type: {type(salt)}")
        hashed_password = hashed_password.decode('utf-8') if isinstance(hashed_password, bytes) else hashed_password
        salt = salt.decode('utf-8') if isinstance(salt, bytes) else salt
        print(f"hashed_password: {hashed_password}, type: {type(hashed_password)}")
        print(f"salt: {salt}, type: {type(salt)}")
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
    def login():
        data = request.json
        response = requests.get(f"http://database-management:5001/users/{data['username']}")
        if response.status_code != 200:
            return jsonify({"message": "User not found"}), 404

        user = response.json()
        if not verify_password(user['password'], data['password']):
            return jsonify({"message": "Invalid credentials"}), 401

        token = generate_token(identity=user['id'], roles=user['role_id'])
        return jsonify({'token': token}), 200
        # access_token = create_access_token(identity=user['id'])
        # return jsonify({"token": access_token}), 200

    @token_required
    @app.route('/auth/logout', methods=['POST'])
    def logout():
        return jsonify({"message": "Logged out successfully"}), 200


routes = Blueprint('routes', __name__)
