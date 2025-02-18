import os
import time
import logging

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from common.SharedFolders import SharedFolders
from common.middleware import get_user_role_from_token

# Überwachtes Verzeichnis
WATCH_FOLDER = SharedFolders.TRAININGSSATZ.value
FILE_THRESHOLD = 2  # Anzahl der Dateien, nach der die Aktion ausgeführt wird

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


class FolderWatcher(FileSystemEventHandler):
    def __init__(self):
        self.file_count = len(os.listdir(WATCH_FOLDER))  # Start mit bestehenden Dateien

    def process(self, event):
        if event.is_directory:
            return  # Überspringe Verzeichnisse

        # Aktuelle Anzahl der Dateien abrufen
        self.file_count = len(os.listdir(WATCH_FOLDER))
        logging.info(f"Dateien im Ordner: {self.file_count}")

        # Falls die Anzahl der Dateien den Schwellenwert erreicht
        if self.file_count >= FILE_THRESHOLD:
            logging.info(f"Schwellenwert {FILE_THRESHOLD} erreicht! Starte Verarbeitung...")
            self.trigger_action()

    def trigger_action(self):
        logging.info("Aktion wird ausgeführt! Beispiel: Verarbeitung der Dateien")
        send_files()
        time.sleep(5)  # Verzögerung nach der Aktion

    def on_created(self, event):
        self.process(event)

    def on_deleted(self, event):
        self.process(event)

    def on_modify(self, event):
        self.process(event)

def send_files():
    files = {}

    # Alle Dateien aus dem Verzeichnis sammeln
    for filename in os.listdir(WATCH_FOLDER):
        file_path = os.path.join(WATCH_FOLDER, filename)

        if os.path.isfile(file_path):  # prüfen, ob es eine Datei ist
            files[filename] = open(file_path, "rb")  # Datei öffnen

    if not files:
        logging.warning("Keine Dateien zum Senden gefunden!")
        return

    logging.info(f"Sende {len(files)} Dateien")

    try:
        cookie = get_user_role_from_token()
        url = " http://nginx-proxy/eventing-service/publish/Trainingsdata"
        headers = {
            "Cookie": f"{cookie}",
        }

        response = requests.post(url, headers=headers, files=files)
        logging.info(f"Response: {response}")

    except Exception as e:
        logging.error(f"Fehler beim Senden der Dateien: {e}")

    finally:
        # Alle geöffneten Dateien schließen
        for f in files.values():
            f.close()


if __name__ == "__main__":
    observer = Observer()
    event_handler = FolderWatcher()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)

    logging.info(f"Überwachung gestartet für: {WATCH_FOLDER}")

    try:
        observer.start()
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Überwachung beendet")

    observer.join()
