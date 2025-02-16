import logging
import os
from flask import Flask, jsonify, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from common.DriveFolders import DriveFolders
from common.config import Config
from common.google_drive import google_save_file_in_folder
from common.middleware import token_required, role_required, get_user_role_from_token
from producer import send_message
import asyncio

app = Flask(__name__)
app.config.from_object(Config)  # Lade zentrale Config


# Initialisiere Flask-Session
Session(app)

@app.route("/")
def home():
    return "Welcome to the Eventing"


def role_based_key():
    try:
        user_role = request.user.get("role", "default")
        remote_addr = get_remote_address()
        logging.debug(f"User role for rate limiting: {user_role}, IP: {remote_addr}")
        return f"{user_role}:{remote_addr}"
    except AttributeError:
        logging.error("Role-based key generation failed. Defaulting to remote address.")
        return get_remote_address()


limiter = Limiter(
    key_func=role_based_key,
    app=app,
    # storage_uri="redis://redis:6379",
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/publish/<event>', methods=['POST'])
@token_required
@role_required('Admin', 'Mitarbeiter', 'Kunde')
@limiter.limit("60 per minute",
               key_func=lambda: f"Admin:{get_remote_address()}" if request.user.get('role') == 'Admin' else None,
               override_defaults=True)
@limiter.limit("20 per minute", key_func=lambda: f"Mitarbeiter:{get_remote_address()}" if request.user.get(
    'role') == 'Mitarbeiter' else None, override_defaults=True)
@limiter.limit("10 per minute",
               key_func=lambda: f"Kunde:{get_remote_address()}" if request.user.get('role') == 'Kunde' else None,
               override_defaults=True)
def publish_event(event):
    # Map event types to messages
    try:
        logging.debug(f"Processing event: {event}")

        # Event-Typen
        if event not in ["ImageUploaded", "ImageValidated", "ClassificationCompleted",
                         "QRCodeGenerated", "CorrectedClassification", "MisclassificationReported"]:
            logging.debug("Event not recognized")
            return jsonify({"error": "Event not recognized"}), 400

        elif event == "ImageUploaded":
            logging.debug(f"Headers: {request.headers}")
            logging.debug(f"Form: {request.form}")
            logging.debug(f"Files: {request.files}")

            # Datei aus `form-data` abrufen
            if 'filename' not in request.files:
                logging.debug("No file part in the request.")
                return jsonify({"error": "No file part in the request"}), 400

            file = request.files['filename']

            # Überprüfen, ob eine Datei ausgewählt wurde
            if file.filename == '':
                logging.debug("No file selected.")
                return jsonify({"error": "No selected file"}), 400

            # Validieren des Dateiformats
            allowed_extensions = {'.jpg', '.jpeg', '.png'}
            if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
                logging.debug(f"Invalid file format: {file.filename}")
                return jsonify({"error": "Only JPG and PNG files are allowed"}), 400

            google_save_file_in_folder(DriveFolders.UPLOAD.value, file)

            cookie = request.headers.get('Cookie', '')
            message_type = request.form.get('type', '')
            logging.debug(f"Type {message_type}")
            # Nachricht senden
            message = {
                "type": message_type,
                "filename": file.filename,
                "cookie": cookie,
            }
            logging.debug(f"Message ImageUploaded: {message}")
            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            asyncio.run(send_message(message))
            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"File {file.filename} uploaded successfully."}), 200

        elif event == "ImageValidated":
            logging.debug(f"Headers: {request.headers}")
            logging.debug(f"Form: {request.form}")
            logging.debug(f"Files: {request.files}")

            # Datei aus `form-data` abrufen
            if 'file' not in request.files:
                logging.debug("No file part in the request.")
                return jsonify({"error": "No file part in the request"}), 400

            file = request.files['file']

            # Überprüfen, ob eine Datei ausgewählt wurde
            if file.filename == '':
                logging.debug("No file selected.")
                return jsonify({"error": "No selected file"}), 400

            user_role = get_user_role_from_token()

            cookie = request.headers.get('Cookie', '')
            message_type = request.form.get('type', '')
            logging.debug(f"Type {message_type}")
            # Nachricht senden
            message = {
                "type": message_type,
                "file": file.filename,
                "role": user_role,
                "cookie": cookie
            }
            logging.debug(f"Message ImageValidated: {message}")
            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            asyncio.run(send_message(message))
            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"File {file.filename} uploaded successfully."}), 200

        elif event == "ClassificationCompleted":
            logging.debug(f"Headers: {request.headers}")
            logging.debug(f"Form: {request.form}")

            cookie = request.headers.get('Cookie', '')
            message_type = request.form.get('type', '')
            result = request.form.get('result', '')
            logging.debug(f"result {result}")
            logging.debug(f"Type {message_type}")
            # Nachricht senden
            message = {
                "type": message_type,
                "result": result,
                "cookie": cookie
            }
            logging.debug(f"Message ClassificationCompleted: {message}")
            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            asyncio.run(send_message(message))
            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"Result {result} uploaded successfully."}), 200

        elif event == "QRCodeGenerated":
            logging.debug(f"Headers: {request.headers}")
            logging.debug(f"Form: {request.form}")
            logging.debug(f"Files: {request.files}")

            cookie = request.headers.get('Cookie', '')
            message_type = request.form.get('type', '')
            image_blob = request.form.get('image_blob', '')
            logging.debug(f"data {image_blob}")
            logging.debug(f"Type {message_type}")
            # Nachricht senden
            message = {
                "type": message_type,
                "image_blob": image_blob,
                "cookie": cookie
            }
            logging.debug(f"Message Encoded: {message}")
            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            asyncio.run(send_message(message))
            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"Type {message_type} uploaded successfully."}), 200

        elif event == "MisclassificationReported":
            logging.debug(f"Headers: {request.headers}")
            logging.debug(f"Form: {request.form}")

            cookie = request.headers.get('Cookie', '')
            message_type = request.form.get('type', '')
            filename = request.form.get('filename', '')
            product_data = request.form.get('product_data', '')
            role = request.form.get('role', '')
            classification = request.form.get('classification', '')
            logging.debug(f"Type {message_type}")
            # Nachricht senden
            message = {
                "type": message_type,
                "filename": filename,
                "classification": classification,
                "product_data": product_data,
                "role": role,
                "cookie": cookie
            }
            logging.debug(f"Message MisclassificationReported: {message}")
            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            asyncio.run(send_message(message))
            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"Type {message_type} uploaded successfully."}), 200

        elif event == "CorrectedClassification":
            logging.debug(f"Headers: {request.headers}")
            logging.debug(f"Form: {request.form}")

            cookie = request.headers.get('Cookie', '')
            message_type = request.form.get('type', '')
            classification = request.form.get('classification', '')
            filename = request.form.get('filename', '')
            class_correct = request.form.get('is_classification_correct', '')
            logging.debug(f"Type {message_type}")
            # Nachricht senden
            message = {
                "type": message_type,
                "is_classification_correct": class_correct,
                "classification": classification,
                "filename": filename,
                "cookie": cookie
            }
            logging.debug(f"Message CorrectedClassification: {message}")
            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            asyncio.run(send_message(message))

            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"Type {message_type} uploaded successfully."}), 200

        elif event == "Training":
            logging.debug(f"Headers: {request.headers}")
            logging.debug(f"Form: {request.form}")

            cookie = request.headers.get('Cookie', '')
            message_type = request.form.get('type', '')
            classification = request.form.get('classification', '')
            filename = request.form.get('filename', '')
            fileid = request.form.get('fileid', '')
            class_correct = request.form.get('is_classification_correct', '')
            logging.debug(f"Type {message_type}")
            # Nachricht senden
            message = {
                "type": message_type,
                "is_classification_correct": class_correct,
                "classification": classification,
                "filename": filename,
                "fileid": fileid,
                "cookie": cookie
            }
            logging.debug(f"Message CorrectedClassification: {message}")
            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            asyncio.run(send_message(message))

            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"Type {message_type} uploaded successfully."}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500

@app.route('/debug/session', methods=['GET'])
def debug_session():
    return jsonify(dict(session))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
