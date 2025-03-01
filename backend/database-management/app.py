"""
   von Maria Schuster
   Endpunkte über die, die Datenbank angesprochen werden kann
"""
import base64
import os

from flask import Flask, jsonify, request, session
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_session import Session
from common.config import Config
from common.middleware import token_required, role_required
from common.utils import load_secrets
from models import db
from crud import (
    create_role, read_role, update_role, delete_role,
    create_user, read_user_by_id, update_user, delete_user,
    create_product, read_product, update_product, delete_product,
    create_qrcode, read_qrcode, delete_qrcode,
    create_failed_classification, read_failed_classifications, delete_failed_classification,
    create_metadata, read_metadata, update_metadata, delete_metadata, read_user_by_name, read_role_by_name,
    read_products_by_name, create_product_without_qr
)

# Flask application initialization
app = Flask(__name__)
app.config.from_object(Config)  # Lade zentrale Config

# Initialisiere Flask-Session
Session(app)

# Database configuration
secrets = load_secrets()
password = secrets.get('POSTGRES_PASSWORD')
DATABASE_URI = "postgresql://postgres:{}@postgres:5432/microservices_db".format(password)
print(f"Loaded DATABASE_URI: {DATABASE_URI}")
engine = create_engine(DATABASE_URI, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


# Bind session to Flask
@app.before_request
def create_db_session():
    db.session = db_session


@app.teardown_request
def shutdown_db_session(exception=None):
    db.session.remove()


# Database Initialization Route
@app.route('/initialize', methods=['POST'])
def initialize_database():
    db.metadata.create_all(bind=engine)
    return jsonify({"status": "Database initialized successfully"}), 201


# --- Rollen (Roles) Routen ---#
@app.route('/roles', methods=['POST'])
def add_role():
    data = request.json
    roles = create_role(db.session, role_name=data['role_name'])
    if roles:
        return jsonify({"id": roles.id, "role_name": roles.role_name}), 201
    return jsonify({"error": "Role already exists"}), 400


@app.route('/roles/<int:role_id>', methods=['GET'])
def get_role(role_id):
    roles = read_role(db.session, role_id=role_id)
    if roles:
        return jsonify({"id": roles.id, "role_name": roles.role_name}), 200
    return jsonify({"error": "Role not found"}), 404


@app.route('/roles/<string:role>', methods=['GET'])
def get_role_by_name(role):
    roles = read_role_by_name(db.session, role_name=role)
    if roles:
        return jsonify({"id": roles.id, "role_name": roles.role_name}), 200
    return jsonify({"error": "Role not found"}), 404


@app.route('/roles/<int:role_id>', methods=['PUT'])
@token_required
@role_required('Admin')
def update_role_info(role_id):
    data = request.json
    roles = update_role(db.session, role_id=role_id, new_role_name=data['role_name'])
    if roles:
        return jsonify({"id": roles.id, "role_name": roles.role_name}), 200
    return jsonify({"error": "Role not found"}), 404


@app.route('/roles/<int:role_id>', methods=['DELETE'])
@token_required
@role_required('Admin')
def delete_role_info(role_id):
    roles = delete_role(db.session, role_id=role_id)
    if roles:
        return jsonify({"status": "Role deleted"}), 200
    return jsonify({"error": "Role not found"}), 404


# --- User Routen ---
@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    users = create_user(db.session, **data)
    if users:
        return jsonify({"id": users.id, "username": users.username}), 201
    return jsonify({"error": "User could not be created"}), 400


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    users = read_user_by_id(db.session, user_id=user_id)
    if users:
        return jsonify({"id": users.id, "username": users.username}), 200
    return jsonify({"error": "User not found"}), 404


@app.route('/users/<string:username>', methods=['GET'])
def get_user_by_name(username):
    users = read_user_by_name(db.session, username=username)
    if users:
        return jsonify({"id": users.id, "username": users.username,
                        "password": users.password, "role_id": users.role_id}), 200
    return jsonify({"error": "User not found"}), 404


@app.route('/users/<int:user_id>', methods=['PUT'])
@token_required
@role_required('Admin')
def update_user_info(user_id):
    data = request.json
    users = update_user(db.session, user_id=user_id, **data)
    if users:
        return jsonify({"id": users.id, "username": users.username}), 200
    return jsonify({"error": "User not found"}), 404


@app.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@role_required('Admin')
def delete_user_info(user_id):
    users = delete_user(db.session, user_id=user_id)
    if users:
        return jsonify({"status": "User deleted"}), 200
    return jsonify({"error": "User not found"}), 404


# --- Product Routen ---
@app.route('/products', methods=['POST'])
@token_required
def add_product():
    data = request.json
    products = create_product(db.session, **data)
    if products:
        return jsonify({"id": products.id, "name": products.name,
                        "description": products.description, "shelf": products.shelf,
                        "price_piece": products.price_piece, "price_kg": products.price_kg,
                        "qr_code_id": products.qr_code_id}), 201
    return jsonify({"error": "Product could not be created"}), 400


@app.route('/products/no-qr', methods=['POST'])
@token_required
def add_product_without_qr():
    data = request.json
    products = create_product_without_qr(db.session, **data)
    if products:
        return jsonify({"id": products.id, "name": products.name,
                        "description": products.description, "shelf": products.shelf,
                        "price_piece": products.price_piece, "price_kg": products.price_kg}), 201
    return jsonify({"error": "Product could not be created"}), 400


@app.route('/products/<string:name>', methods=['GET'])
@token_required
def get_product_by_name(name):
    products = read_products_by_name(db.session, name=name)
    if products:
        return jsonify({"id": products.id, "name": products.name,
                        "description": products.description, "shelf": products.shelf,
                        "price_piece": products.price_piece, "price_kg": products.price_kg,
                        "qr_code_id": products.qr_code_id}), 200
    return jsonify({"error": "Product not found"}), 404


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    products = read_product(db.session, product_id=product_id)
    if products:
        return jsonify({"id": products.id, "name": products.name,
                        "description": products.description, "shelf": products.shelf,
                        "price_piece": products.price_piece, "price_kg": products.price_kg,
                        "qr_code_id": products.qr_code_id}), 200
    return jsonify({"error": "Product not found"}), 404


@app.route('/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product_info(product_id):
    data = request.json
    products = update_product(db.session, product_id=product_id, **data)
    if products:
        return jsonify({"id": products.id, "name": products.name,
                        "description": products.description, "shelf": products.shelf,
                        "price_piece": products.price_piece, "price_kg": products.price_kg,
                        "qr_code_id": products.qr_code_id}), 200
    return jsonify({"error": "Product not found"}), 404


@app.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
@role_required('Admin')
def delete_product_info(product_id):
    products = delete_product(db.session, product_id=product_id)
    if products:
        return jsonify({"status": "Product deleted"}), 200
    return jsonify({"error": "Product not found"}), 404

# --- QRCode Routen ---
@app.route('/qrcodes', methods=['POST'])
@token_required
def add_qrcode():
    data = request.json
    image_blob = base64.b64decode(data['data'])
    qrcodes = create_qrcode(db.session, image_blob)
    if qrcodes:
        return jsonify({"id": qrcodes.id}), 201
    return jsonify({"error": "QRCode could not be created"}), 400


@app.route('/qrcodes/<int:qrcode_id>', methods=['GET'])
def get_qrcode(qrcode_id):
    qrcodes = read_qrcode(db.session, qr_code_id=qrcode_id)
    if qrcodes:
        return jsonify({
            "id": qrcodes.id,
            "data": base64.b64encode(qrcodes.data).decode()  # Konvertiere in Base64 für die API
        }), 200
    return jsonify({"error": "QRCode not found"}), 404


@app.route('/qrcodes/<int:qrcode_id>', methods=['DELETE'])
@token_required
@role_required('Admin')
def delete_qrcode_info(qrcode_id):
    qrcodes = delete_qrcode(db.session, qr_code_id=qrcode_id)
    if qrcodes:
        return jsonify({"status": "QRCode deleted"}), 200
    return jsonify({"error": "QRCode not found"}), 404


# --- FailedClassification Routen ---
@app.route('/failed-classifications', methods=['POST'])
@token_required
def add_failed_classification():
    data = request.json
    failed_classifications = create_failed_classification(db.session, **data)
    if failed_classifications:
        return jsonify({"id": failed_classifications.id, "reason": failed_classifications.reason}), 201
    return jsonify({"error": "Failed Classification could not be created"}), 400


@app.route('/failed-classifications', methods=['GET'])
def get_failed_classifications():
    failed_classifications = read_failed_classifications(db.session)
    return jsonify([{"id": fc.id, "reason": fc.reason} for fc in failed_classifications]), 200


@app.route('/failed-classifications/<int:failed_classification_id>', methods=['DELETE'])
@token_required
@role_required('Admin')
def delete_failed_classification_info(failed_classification_id):
    failed_classifications = delete_failed_classification(db.session, failed_classification_id=failed_classification_id)
    if failed_classifications:
        return jsonify({"status": "Failed Classification deleted"}), 200
    return jsonify({"error": "Failed Classification not found"}), 404


# --- Metadata Routen ---
@app.route('/metadata', methods=['POST'])
@token_required
@role_required('Admin')
def add_metadata():
    data = request.json
    metadata = create_metadata(db.session, **data)
    if metadata:
        return jsonify({"id": metadata.id, "key": metadata.key, "value": metadata.value}), 201
    return jsonify({"error": "Metadata could not be created"}), 400


@app.route('/metadata/<int:metadata_id>', methods=['GET'])
@token_required
@role_required('Admin')
def get_metadata(metadata_id):
    metadata = read_metadata(db.session, metadata_id=metadata_id)
    if metadata:
        return jsonify({"id": metadata.id, "key": metadata.key, "value": metadata.value}), 200
    return jsonify({"error": "Metadata not found"}), 404


@app.route('/metadata/<int:metadata_id>', methods=['PUT'])
@token_required
@role_required('Admin')
def update_metadata_info(metadata_id):
    data = request.json
    metadata = update_metadata(db.session, metadata_id=metadata_id, **data)
    if metadata:
        return jsonify({"id": metadata.id, "key": metadata.key, "value": metadata.value}), 200
    return jsonify({"error": "Metadata not found"}), 404


@app.route('/metadata/<int:metadata_id>', methods=['DELETE'])
@token_required
@role_required('Admin')
def delete_metadata_info(metadata_id):
    metadata = delete_metadata(db.session, metadata_id=metadata_id)
    if metadata:
        return jsonify({"status": "Metadata deleted"}), 200
    return jsonify({"error": "Metadata not found"}), 404

@app.route('/admin/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
