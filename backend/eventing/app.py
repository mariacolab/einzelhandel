"""
    von Maria Schuster
    Events werden mit den Messages gemappt
"""
import eventlet
eventlet.monkey_patch()
import logging
import os
import shutil
import json
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
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)  # Lade zentrale Config
CORS(app, resources={r"/*": {"origins": ["http://localhost:4200", "http://192.168.2.58:4200", "https://localhost:4200", "https://192.168.2.58:4200"]}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

Tf_SOURCE = "/mnt/shared_training/ki/kleinesModell"
Labeled_Tf = "/mnt/labeled_tf"
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

@app.route('/ImageUploaded', methods=['POST'])
@cross_origin(origins=["http://localhost:4200", "http://192.168.2.58:4200", "https://localhost:4200", "https://192.168.2.58:4200"], supports_credentials=True)
@token_required
@role_required('Admin', 'Mitarbeiter', 'Kunde')
@limiter.limit("30 per minute", key_func=lambda: f"Mitarbeiter:{get_remote_address()}" if request.user.get(
    'role') == 'Mitarbeiter' else None, override_defaults=True)
@limiter.limit("10 per minute",
               key_func=lambda: f"Kunde:{get_remote_address()}" if request.user.get('role') == 'Kunde' else None,
               override_defaults=True)
def publish_imageupload():
    """
        ausführen des Bild hochgeladen Events
    """
    try:
        logging.debug(f"Headers: {request.headers}")
        logging.debug(f"Form: {request.form}")
        event_type = request.form.get("type", "")
        #hochladen des Fotos
        if event_type != "ImageUploaded":
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
            #logging.debug(f"Event {event} published successfully")
            return jsonify({"status": f"File {file.filename} uploaded successfully."}), 200
    except Exception as e:
            logging.debug(f"Error in publish_event: {e}")
            return jsonify({"message": "Internal server error", "details": str(e)}), 500


#Events die alle Rollen ausführen können
@app.route('/publish/<event>', methods=['POST'])
@cross_origin(origins=["http://localhost:4200", "http://192.168.2.58:4200", "https://localhost:4200", "https://192.168.2.58:4200"], supports_credentials=True)
@token_required
@role_required('Admin', 'Mitarbeiter', 'Kunde')
def publish_event(event):
    """
        mapping von Eventtypen zu den Messages
        :param event: Bezeichnung des erhaltenen Events
    """
    try:
        logging.debug(f"Processing event: {event}")

        # Event-Typen
        if event not in ["ImageValidated", "ClassificationCompleted",
                         "QRCodeGenerated", "CorrectedClassification", "ClassificationReported"]:
            logging.debug("Event not recognized")
            return jsonify({"error": "Event not recognized"}), 400
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

            host = request.form.get('host', '')
            protocol = request.form.get('protocol', '')
            cookie = request.headers.get('Cookie', '')
            message_type = request.form.get('type', '')
            result = request.form.get('result', '')
            logging.debug(f"result {result}")
            logging.debug(f"Type {message_type}")
            # Nachricht senden
            message = {
                "type": message_type,
                "result": result,
                "cookie": cookie,
                "protocol": protocol,
                "host": host
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

            # Bestimmt automatisch das Protokoll (http/https) und die Herkunft (Host)
            protocol = "https" if request.is_secure else "http"
            host = request.host  # Holt den aktuellen Host (z. B. localhost:5000 oder 192.168.2.58:5000)
            logging.debug(f"host: {host}")
            logging.debug(f"protocol: {protocol}")

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
                "mixed_results": mixed_results,
                "host": host,
                "protocol": protocol,
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
@cross_origin(origins=["http://localhost:4200", "http://192.168.2.58:4200", "https://localhost:4200", "https://192.168.2.58:4200"], supports_credentials=True)
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

# @socketio.on('LabeledTrainingdata')
# def handle_labeled_trainingdata(data):
#     """
#     Erwartet ein JSON mit:
#       - ki: "tf"
#       - fileNames: Liste der Dateinamen
#       - labels: Parallele Liste der Dropdown-Werte
#     """
#     logging.info(f"LabeledTrainingdata socketio")
#     ki = data.get("ki", "").lower()
#     file_names = data.get("fileNames", [])
#     labels = data.get("labels", [])
#     logging.info(f"LabeledTrainingdata ki: {ki}")
#     logging.info(f"LabeledTrainingdata file_names: {file_names}")
#     logging.info(f"LabeledTrainingdata labels: {labels}")
#     if not file_names or not labels or len(file_names) != len(labels):
#         emit("LabeledTrainingdataAck", {"error": "Ungültige Daten"})
#         return
#
#     # Bestimme Quell- und Zielordner anhand des KI-Typs
#     if ki == "tf":
#         source_folder = Tf_SOURCE
#         target_folder = Labeled_Tf
#     else:
#         emit("LabeledTrainingdataAck", {"error": "Unbekannter KI-Typ"})
#         return
#
#     saved_files = []
#     for filename in file_names:
#         src_path = os.path.join(source_folder, filename)
#         dest_path = os.path.join(target_folder, filename)
#         try:
#             os.rename(src_path, dest_path)
#             saved_files.append({"file": dest_path})
#             logging.info(f"Verschoben: {src_path} -> {dest_path}")
#         except Exception as e:
#             logging.error(f"Fehler beim Verschieben der Datei {filename}: {e}")
#
#     message = {
#                 "type": "LabeledTrainingdata",
#                 "ki": ki,
#                 "labels": labels,
#                 "files": file_names,
#             }
#     logging.debug(f"Message LabeledTrainingdata Event: {message}")
#     asyncio.run(send_message(message))
#
#     emit("LabeledTrainingdataAck", {"files": saved_files})

@app.route('/LabeledTrainingdata', methods=['POST'])
@cross_origin(origins=["http://localhost:4200", "http://192.168.2.58:4200", "https://localhost:4200", "https://192.168.2.58:4200"], supports_credentials=True)
@token_required
@role_required('Admin', 'Mitarbeiter')
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
        event_filenames = request.form.get("files", "")

        if event_type != "LabeledTrainingdata":
            return jsonify({"error": "Ungültiger Event-Typ"}), 400

        try:
            event_labels = json.loads(event_labels)
        except json.JSONDecodeError as e:
            logging.error(f"Fehler beim Parsen von labels: {e}")
            return jsonify({"error": "Labels-Format fehlerhaft"}), 400

        event_filenames = event_filenames.strip('"').split(",")

        saved_files = []
        if event_ki == "tf":
            for name in event_filenames:
                source_path = os.path.join(Tf_SOURCE, name.strip())
                dest_path = os.path.join(Labeled_Tf, name.strip())
                try:
                    shutil.move(source_path, dest_path)
                    saved_files.append(dest_path)
                    logging.info(f"Datei verschoben: {source_path} → {dest_path}")
                except Exception as e:
                    logging.error(f"Fehler beim Verschieben von {name}: {e}")

        logging.debug(f"Gespeicherte Dateien: {saved_files}")

        message = {
            "type": event_type,
            "ki": event_ki,
            "labels": event_labels,
            "files": event_filenames,
        }

        message_json = json.dumps(message)
        logging.debug(f"Message LabeledTrainingdata Event: {message}")
        asyncio.run(send_message(message))
        return jsonify({"status": f"Type {event_type} uploaded successfully.", "files": saved_files}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500

@app.route('/ai/tensorflow', methods=['POST'])
@cross_origin(origins=["http://localhost:4200", "http://192.168.2.58:4200", "https://localhost:4200", "https://192.168.2.58:4200"], supports_credentials=True)
@token_required
@role_required('Admin')
def start_ai_tensorflow():
    """
        starten des Nachtrainings von Tensorflow
    """
    try:
        logging.debug(f"Headers: {request.headers}")
        #logging.debug(f"Form: {request.form}")

        event_type = request.form.get("type", "")  # Holt den Event-Typ aus der Form-Daten
        if event_type != "TrainTF":
            return jsonify({"error": "Ungültiger Event-Typ"}), 400

        message = {
            "type": event_type,
            #"files": saved_files,
        }
        logging.debug(f"Message TrainTF Event: {message}")
        asyncio.run(send_message(message))
        return jsonify({"status": f"Type {event_type} uploaded successfully."}), 200#, "files": saved_files}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500

@app.route('/ai/yolo', methods=['POST'])
@cross_origin(origins=["http://localhost:4200", "http://192.168.2.58:4200", "https://localhost:4200", "https://192.168.2.58:4200"], supports_credentials=True)
@token_required
@role_required('Admin')
def start_ai_yolo():
    """
        starten des Nachtrainings von Tensorflow
    """
    try:
        logging.debug(f"Headers: {request.headers}")
        #logging.debug(f"Form: {request.form}")

        event_type = request.form.get("type", "")  # Holt den Event-Typ aus der Form-Daten
        if event_type != "TrainYOLO":
            return jsonify({"error": "Ungültiger Event-Typ"}), 400

        message = {
            "type": event_type,
            #"files": saved_files,
        }
        logging.debug(f"Message TrainYOLO Event: {message}")
        asyncio.run(send_message(message))
        return jsonify({"status": f"Type {event_type} uploaded successfully."}), 200#, "files": saved_files}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500


""" @app.route('/qrcode/scan/result', methods=['POST'])
@cross_origin(origins=["http://localhost:4200", "http://192.168.2.58:4200", "https://localhost:4200", "https://192.168.2.58:4200"], supports_credentials=True)
def qrcode_scan_result():
    try:
        logging.debug(f"Headers: {request.headers}")
        logging.debug(f"Form: {request.form}")

        event_type = request.form.get('type')

        # Holt den Event-Typ aus der Form-Daten
        if event_type != "ReadQrCode":
            return jsonify({"error": "Ungültiger Event-Typ"}), 400

        qrdata = request.form.get("qrdata", "")

        message = {
            "type": event_type,
            "qrdata": qrdata,
        }
        logging.debug(f"Message qr-code Event: {message}")
        asyncio.run(send_message(message))
        return jsonify({"status": f"Type {event_type} uploaded successfully."}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500 """

@app.route('/qrcode/scan/result', methods=['GET'])
@cross_origin(origins=["http://localhost:4200", "http://192.168.2.58:4200", "https://localhost:4200", "https://192.168.2.58:4200"], supports_credentials=True)
def qrcode_scan_result():
    """
        scan QR Codes
    """
    try:
        logging.debug(f"Headers: {request.headers}")
        logging.debug(f"Args: {request.args}")

        # Holt den Event-Typ aus den URL-Parametern
        event_type = request.args.get('type')

        if event_type != "ReadQrCode":
            return jsonify({"error": "Ungültiger Event-Typ"}), 400

        qrdata = request.args.get("qrdata", "")

        message = {
            "type": event_type,
            "qrdata": qrdata,
        }
        logging.debug(f"Message qr-code Event: {message}")
        asyncio.run(send_message(message))
        return jsonify({"status": f"Type {event_type} uploaded successfully."}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500

@app.route('/qrcode/send/result', methods=['POST'])
def qrcode_send_result():
    """
        senden der Daten die der QR-Code zurückgibt
    """
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
