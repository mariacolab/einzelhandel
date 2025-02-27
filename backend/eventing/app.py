"""
    von Maria Schuster
    Events werden mit den Messages gemappt
"""
import logging
import os
from flask import Flask, jsonify, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from common.SharedFolders import SharedFolders
from common.config import Config
from common.middleware import token_required, role_required, get_user_role_from_token
from common.shared_drive import save_file_in_folder
from producer import send_message
from flask_cors import cross_origin
import asyncio

app = Flask(__name__)
app.config.from_object(Config)  # Lade zentrale Config

# Initialisiere Flask-Session
Session(app)


@app.route("/")
def home():
    return "Welcome to the Eventing"

#fügt das Rate Limiting einer bestimmten Rolle zu
def role_based_key():
    try:
        user_role = request.user.get("role", "default")
        remote_addr = get_remote_address()
        logging.debug(f"User role for rate limiting: {user_role}, IP: {remote_addr}")
        return f"{user_role}:{remote_addr}"
    except AttributeError:
        logging.error("Role-based key generation failed. Defaulting to remote address.")
        return get_remote_address()

#konfiguration Rate Limiting
limiter = Limiter(
    key_func=role_based_key,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)
#Events die alle Rollen ausführen können
@app.route('/publish/<event>', methods=['POST'])
@cross_origin(origins=["http://localhost:4200"], supports_credentials=True)
@token_required
@role_required('Admin', 'Mitarbeiter', 'Kunde')
@limiter.limit("30 per minute", key_func=lambda: f"Mitarbeiter:{get_remote_address()}" if request.user.get(
    'role') == 'Mitarbeiter' else None, override_defaults=True)
@limiter.limit("10 per minute",
               key_func=lambda: f"Kunde:{get_remote_address()}" if request.user.get('role') == 'Kunde' else None,
               override_defaults=True)
def publish_event(event):
    """
        mapping von Eventtypen zu den Messages

        :param event: Bezeichnung des erhaltenen Events
    """
    try:
        logging.debug(f"Processing event: {event}")

        # Event-Typen
        if event not in ["ImageUploaded", "ImageValidated", "ClassificationCompleted",
                         "QRCodeGenerated", "CorrectedClassification", "ClassificationReported"]:
            logging.debug("Event not recognized")
            return jsonify({"error": "Event not recognized"}), 400
        #hochladen des Fotos
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

            save_file_in_folder(SharedFolders.UPLOAD.value, file)

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
        #validierung des Fotos
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
        #Klassifiezierung ist abgeschlossen
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
        #Klassifiezierung war korrekt und QR-Code kann erzeugt oder geladen werden
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
        #Klassifiezierung wird an das Frontend gesendet
        elif event == "ClassificationReported":
            logging.debug(f"Headers: {request.headers}")
            logging.debug(f"Form: {request.form}")
            logging.debug(f"Files: {request.files}")

            cookie = request.headers.get('Cookie', '')
            message_type = request.form.get('type', '')
            filename = request.form.get('filename', '')
            product = request.form.get('product', '')
            info = request.form.get('info', '')
            shelf = request.form.get('shelf', '')
            price_piece = request.form.get('price_piece', '')
            price_kg = request.form.get('price_kg', '')
            role = request.form.get('role', '')
            classification = request.form.get('classification', '')
            mixed_results = request.form.get('mixed_results', '')
            logging.debug(f"Type {message_type}")
            # Nachricht senden
            message = {
                "type": message_type,
                "filename": filename,
                "classification": classification,
                "product": product,
                "info": info,
                "shelf": shelf,
                "price_piece": price_piece,
                "price_kg": price_kg,
                "role": role,
                "cookie": cookie,
                "mixed_results" : mixed_results
            }
            logging.debug(f"Message ClassificationReported: {message}")
            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            asyncio.run(send_message(message))
            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"Type {message_type} uploaded successfully."}), 200
        #Klassifizierung wurde durch das Frontend korrigiert oder bestätigt und an die KI zurückgesendet
        elif event == "CorrectedClassification":
            logging.debug(f"Headers: {request.headers}")
            logging.debug(f"Form: {request.form}")

            cookie = request.headers.get('Cookie', '')
            message_type = request.form.get('type', '')
            classification = request.form.get('classification', '')
            filename = request.form.get('filename', '')
            class_correct = request.form.get('is_classification_correct', '')
            mixed_results =request.form.get('mixed_results', '')
            logging.debug(f"Type {message_type}")
            # Nachricht senden
            message = {
                "type": message_type,
                "is_classification_correct": class_correct,
                "classification": classification,
                "filename": filename,
                "cookie": cookie,
                "mixed_results": mixed_results
            }
            logging.debug(f"Message CorrectedClassification: {message}")
            # RabbitMQ Nachricht senden, um das Event zu veröffentlichen
            asyncio.run(send_message(message))

            logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"Type {message_type} uploaded successfully."}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500


@app.route('/Trainingsdata', methods=['POST'])
def publish_trainingsdata():
    """
        übermittelt die Bilder der Kunden zur Validierung um sie zu labeln
    """
    try:
        logging.debug(f"Headers: {request.headers}")
        logging.debug(f"Form: {request.form}")

        event_type = request.form.get("type", "")  # Holt den Event-Typ aus der Form-Daten
        event_ki = request.form.get("ki", "") # angabe ob es sich um Tensorflow oder Yolo handelt
        if event_type != "Trainingdata":
            return jsonify({"error": "Ungültiger Event-Typ"}), 400

        # Dateien abrufen
        files = request.files.getlist("files")  # Prüfen, ob Dateien vorhanden sind
        if not files:
            return jsonify({"error": "Keine Dateien hochgeladen!"}), 400

        saved_files = []
        for file in files:
            file_path = os.path.join("/mnt/shared_training", file.filename)
            file.save(file_path)
            saved_files.append(file_path)

        logging.debug(f"Gespeicherte Dateien: {saved_files}")

        message = {
            "type": event_type,
            "ki": event_ki,
            "files": saved_files,
        }
        logging.debug(f"Message Trainingdata Event: {message}")
        asyncio.run(send_message(message))
        return jsonify({"status": f"Type {event_type} uploaded successfully.", "files": saved_files}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500

@app.route('/LabeledTrainingdata', methods=['POST'])
def publish_labeledtrainingsdata():
    """
        Erhält die gelabelten Bilder zurück
    """
    try:
        logging.debug(f"Headers: {request.headers}")
        logging.debug(f"Form: {request.form}")

        event_type = request.form.get("type", "")  # Holt den Event-Typ aus der Form-Daten
        event_ki = request.form.get("ki", "") # angabe ob es sich um Tensorflow oder Yolo handelt
        event_labels = request.form.get("labels", "")
        if event_type != "LabeledTrainingdata":
            return jsonify({"error": "Ungültiger Event-Typ"}), 400

        # Dateien abrufen
        files = request.files.getlist("files")  # Prüfen, ob Dateien vorhanden sind
        if not files:
            return jsonify({"error": "Keine Dateien hochgeladen!"}), 400

        if event_ki is "yolo":
            saved_files = []
            for file in files:
                file_path = os.path.join("/mnt/labeled_yolo", file.filename)
                file.save(file_path)
                saved_files.append(file_path)
        elif event_ki is "tf":
            saved_files = []
            for file in files:
                file_path = os.path.join("/mnt/labeled_yolo", file.filename)
                file.save(file_path)
                saved_files.append(file_path)

        logging.debug(f"Gespeicherte Dateien: {saved_files}")

        message = {
            "type": event_type,
            "ki": event_ki,
            "labels": event_labels,
            "files": saved_files,
        }
        logging.debug(f"Message LabeledTrainingdata Event: {message}")
        asyncio.run(send_message(message))
        return jsonify({"status": f"Type {event_type} uploaded successfully.", "files": saved_files}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500

@app.route('/ai/tensorflow', methods=['POST'])
@token_required
@role_required('Admin')
def start_ai_tensorflow():
    try:
        logging.debug(f"Headers: {request.headers}")
        logging.debug(f"Form: {request.form}")

        event_type = request.form.get("type", "")  # Holt den Event-Typ aus der Form-Daten
        if event_type != "TrainTF":
            return jsonify({"error": "Ungültiger Event-Typ"}), 400

        # Dateien abrufen
        files = request.files.getlist("files")  # Prüfen, ob Dateien vorhanden sind
        if not files:
            return jsonify({"error": "Keine Dateien hochgeladen!"}), 400

        saved_files = []
        for file in files:
            file_path = os.path.join("/mnt/shared_training", file.filename)
            file.save(file_path)
            saved_files.append(file_path)

        logging.debug(f"Gespeicherte Dateien: {saved_files}")

        message = {
            "type": event_type,
            "files": saved_files,
        }
        logging.debug(f"Message TrainTF Event: {message}")
        asyncio.run(send_message(message))
        return jsonify({"status": f"Type {event_type} uploaded successfully.", "files": saved_files}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500

@app.route('/ai/yolo', methods=['POST'])
@token_required
@role_required('Admin')
def start_ai_yolo():

    try:
        logging.debug(f"Headers: {request.headers}")
        logging.debug(f"Form: {request.form}")

        event_type = request.form.get("type", "")  # Holt den Event-Typ aus der Form-Daten
        if event_type != "TrainYOLO":
            return jsonify({"error": "Ungültiger Event-Typ"}), 400

        # Dateien abrufen
        files = request.files.getlist("files")  # Prüfen, ob Dateien vorhanden sind
        if not files:
            return jsonify({"error": "Keine Dateien hochgeladen!"}), 400

        saved_files = []
        for file in files:
            file_path = os.path.join("/mnt/shared_training", file.filename)
            file.save(file_path)
            saved_files.append(file_path)

        logging.debug(f"Gespeicherte Dateien: {saved_files}")

        message = {
            "type": event_type,
            "files": saved_files,
        }
        logging.debug(f"Message TrainYOLO Event: {message}")
        asyncio.run(send_message(message))
        return jsonify({"status": f"Type {event_type} uploaded successfully.", "files": saved_files}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500


@app.route('/qrcode/scan/result', methods=['GET'])
def qrcode_scan_result():
    try:
        event_type = request.args.get('type')
        produkt = request.args.get('produkt')
        # Holt den Event-Typ aus der Form-Daten
        if event_type != "ReadQrCode":
            return jsonify({"error": "Ungültiger Event-Typ"}), 400

        qrdata = request.form.get("qrdata", "")

        message = {
            "type": event_type,
            "qrdata": produkt,
        }
        logging.debug(f"Message TrainYOLO Event: {message}")
        asyncio.run(send_message(message))
        return jsonify({"status": f"Type {event_type} uploaded successfully."}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500

@app.route('/qrcode/send/result', methods=['POST'])
def qrcode_send_result():
    try:
        logging.debug(f"Headers: {request.headers}")
        logging.debug(f"Form: {request.form}")

        event_type = request.form.get("type", "")  # Holt den Event-Typ aus der Form-Daten
        if event_type != "sendQrCodeResult":
            return jsonify({"error": "Ungültiger Event-Typ"}), 400

        name = request.form.get("name", "")
        description = request.form.get("description", "")
        shelf = request.form.get("shelf", "")
        price_piece = request.form.get("price_piece", "")
        price_kg = request.form.get("price_kg", "")

        message = {
            "type": event_type,
            "name": name,
            "description": description,
            "shelf": shelf,
            "price_piece": price_piece,
            "price_kg": price_kg,
        }
        logging.debug(f"Message TrainYOLO Event: {message}")
        asyncio.run(send_message(message))
        return jsonify({"status": f"Type {event_type} uploaded successfully."}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500
@app.route('/debug/session', methods=['GET'])
def debug_session():
    return jsonify(dict(session))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
