import logging
import os
from threading import Thread
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from common.middleware import token_required, role_required
from producer import send_message
import asyncio

app = Flask(__name__)
app.config['DEBUG'] = True
logging.basicConfig(level=logging.DEBUG)


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
        if event not in ["ImageUploaded", "ImageValidated", "ClassificationCompleted", "QRCodeGenerated"]:
            logging.debug("Event not recognized")
            return jsonify({"error": "Event not recognized"}), 400

        if event == "ImageUploaded":
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

            # Speichern der Datei
            save_path = f"/shared/uploads/{file.filename}"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Sicherstellen, dass das Verzeichnis existiert
            file.save(save_path)
            logging.debug(f"File {file.filename} saved to {save_path}")

            token = request.headers.get('Authorization', '')
            # Nachricht senden
            message = {
                "type": "ProcessFiles",
                "data": {
                    "filename": file.filename,
                    "path": save_path,
                    "token": token
                }
            }
            asyncio.run(send_message(message))

            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            #asyncio.run(send_message({"type": "ProcessFiles", "data": {}}))
            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"File {file.filename} uploaded successfully."}), 200

        if event == "ImageValidated":
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

            # Validieren des Dateiformats
            allowed_extensions = {'.jpg', '.jpeg', '.png'}
            if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
                logging.debug(f"Invalid file format: {file.filename}")
                return jsonify({"error": "Only JPG and PNG files are allowed"}), 400

            # Speichern der Datei
            save_path = f"/downloads/{file.filename}"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Sicherstellen, dass das Verzeichnis existiert
            file.save(save_path)
            logging.debug(f"File {file.filename} saved to {save_path}")

            # Nachricht senden
            message = {
                "type": "ImageValidated",
                "data": {
                    "file": file.filename,
                    "path": save_path
                }
            }
            asyncio.run(send_message(message))

            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            asyncio.run(send_message({"type": "ValidatedFiles", "data": {}}))
            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"File {file.filename} uploaded successfully."}), 200

        if event == "ClassificationCompleted":
            logging.debug(f"Headers: {request.headers}")
            body = request.get_data(as_text=True)  # Retrieve raw body data as text
            logging.debug(f"Body: {body}")

            # Nachricht senden
            message = {
                "type": f"{event}",
                "body": f"{body}"
            }
            asyncio.run(send_message(message))

            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            asyncio.run(send_message({"type": "ClassFiles", "data": {}}))
            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"Body {body} uploaded successfully."}), 200

        if event == "QRCodeGenerated":
            logging.debug(f"Headers: {request.headers}")
            body = request.get_data(as_text=True)  # Retrieve raw body data as text
            logging.debug(f"Body: {body}")

            # Nachricht senden
            message = {
                "type": f"{event}",
                "body": f"{body}"
            }
            asyncio.run(send_message(message))

            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            asyncio.run(send_message({"type": "ProcessQrcode", "data": {}}))
            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"Body {body} uploaded successfully."}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
