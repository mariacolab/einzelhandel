"""
   von Maria Schuster
   Überwachung der TRAININGSSATZ/kleinesModell
"""
import eventlet
eventlet.monkey_patch()
import logging
import os
import time
import base64
from flask import Flask
from flask_socketio import SocketIO
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flask_cors import CORS

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)

# Konfiguration
WATCHED_DIR = "/watched_data"
FILE_THRESHOLD = int(os.getenv("FILE_THRESHOLD", 3))
# KI_TYPE: "yolo" oder "tf" – wird als Umgebungsvariable gesetzt (z.B. in docker-compose)
KI_TYPE = os.getenv("KI_TYPE", "tf")
watchdog_active = True

# Flask-App und SocketIO initialisieren
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": ["http://localhost:4200", "http://192.168.2.58:4200", "https://localhost:4200", "https://192.168.2.58:4200"]}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
#socketio = SocketIO(app, cors_allowed_origins="*", transports=["websocket"], async_mode="eventlet")



class FileHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()

    def on_created(self, event):
        """Wird aufgerufen, wenn eine neue Datei erstellt wird."""
        if event.is_directory:
            return

        logging.debug(f"Neue Datei erkannt: {event.src_path}")
        time.sleep(3)  # Sicherstellen, dass die Datei vollständig geschrieben wurde

        total_files = self.count_files()
        logging.debug(f"Aktuelle Anzahl Dateien: {total_files}")

        if total_files >= FILE_THRESHOLD:
            logging.info(f"Schwellenwert ({FILE_THRESHOLD} Dateien) erreicht. Sende Trainingsdata-Event.")
            self.send_files()

    def count_files(self):
        """Zählt alle Dateien im WATCHED_DIR."""
        return sum(len(files) for _, _, files in os.walk(WATCHED_DIR))

    def send_files(self):
        """Sendet per SocketIO ein Trainingsdata-Event an das Frontend."""
        if not watchdog_active:
            logging.info("Watchdog inaktiv. Keine Daten werden gesendet.")
            return

        file_list = []
        encoded_files = {}

        for filename in os.listdir(WATCHED_DIR):
            file_path = os.path.join(WATCHED_DIR, filename)
            if os.path.isfile(file_path):
                if(filename != ".gitignore"):
                    file_list.append(filename)

                    with open(file_path, "rb") as file:
                        encoded_content = base64.b64encode(file.read()).decode('utf-8')
                        encoded_files[filename] = encoded_content

        if not file_list:
            logging.warning("Keine Dateien gefunden, Event wird nicht gesendet!")
            return

        payload = {
            "type": "Trainingdata",
            "ki": KI_TYPE,
            "files": file_list,
            "data": encoded_files
        }
        logging.info(f"Emitting Trainingsdata Event: {payload}")
        socketio.emit("Trainingdata", payload)


@socketio.on("connect")
def handle_connect():
    global watchdog_active
    watchdog_active = True
    logging.info("WebSocket-Client tf verbunden!")
    logging.info("Frontend hat sich per SocketIO verbunden.")
    total_files = sum(len(files) for _, _, files in os.walk(WATCHED_DIR))
    logging.info(f"Aktuelle Anzahl Dateien: {total_files}")
    if total_files >= FILE_THRESHOLD:
        logging.info(f"Schwellenwert erreicht ({FILE_THRESHOLD} Dateien). Sende Trainingsdata-Event.")
        event_handler.send_files()  # Verwende die globale Instanz

@socketio.on("disconnect")
def handle_disconnect():
    global watchdog_active
    watchdog_active = False
    logging.info("WebSocket-Client tf getrennt.")

if __name__ == "__main__":
    # Watchdog starten
    observer = Observer()
    event_handler = FileHandler()
    observer.schedule(event_handler, WATCHED_DIR, recursive=True)
    observer.start()
    logging.info(f"Starte Dateiüberwachung in {WATCHED_DIR} für TF")
    try:
        print(f"Starte Watchdog auf Port {5015 if KI_TYPE == 'tf' else 5016}...")
        socketio.run(app, host="0.0.0.0", port=(5015 if KI_TYPE == "tf" else 5016), debug=True)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
