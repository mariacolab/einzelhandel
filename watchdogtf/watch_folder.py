import logging
import os
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Setup logging
logging.basicConfig(level=logging.INFO)

WATCHED_DIR = "/watched_data"
FILE_THRESHOLD = int(os.getenv("FILE_THRESHOLD", 50))
TARGET_URL = os.getenv("TARGET_URL", "http://nginx/eventing-service/Trainingsdata")
WATCHDOG_SERVER = "nginx"  # WebSocket Server-Adresse
WATCHDOG_PORT = 5011

# Verbindung zu WebSocket
socket = SocketIO(WATCHDOG_SERVER, WATCHDOG_PORT)
watchdog_active = False  # Zustand des Watchdogs

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        """Wird aufgerufen, wenn eine neue Datei erstellt wird"""
        if event.is_directory:
            return

        logging.debug(f"Neue Datei erkannt: {event.src_path}")
        time.sleep(3)  # Sicherstellen, dass Datei vollständig geschrieben wurde

        total_files = self.count_files()
        logging.debug(f"Aktuelle Anzahl Dateien nach Neu-Erstellung: {total_files}")
        logging.debug(f"Aktuelle Anzahl FILE_THRESHOLD: {FILE_THRESHOLD}")

        if total_files >= FILE_THRESHOLD:
            logging.info(f"Schwellenwert erreicht ({FILE_THRESHOLD} Dateien). Starte Upload.")
            self.send_files()

    def count_files(self):
        """Zählt die Anzahl der Dateien im Verzeichnis"""
        file_count = sum(len(files) for _, _, files in os.walk(WATCHED_DIR))
        logging.debug(f"Aktuelle Anzahl Dateien: {file_count}")
        return file_count

    def send_files(self):
        """Sendet die Dateien per POST-Request"""
         if not watchdog_active:
            logging.info("Watchdog inaktiv. Keine Daten werden gesendet.")
            return

        files = []
        data = {'type': 'Trainingdata',
                'ki': 'Yolo'}  # Zusätzliche Form-Daten

        # Alle Dateien aus dem Verzeichnis sammeln
        for filename in os.listdir(WATCHED_DIR):
            file_path = os.path.join(WATCHED_DIR, filename)

            if os.path.isfile(file_path):  # Nur Dateien (keine Verzeichnisse)
                files.append(("files", (filename, open(file_path, "rb"), "application/octet-stream")))

        if not files:
            logging.warning("Keine Dateien gefunden, Upload abgebrochen!")
            return

        logging.info(f"Sende {len(files)} Dateien an {TARGET_URL} mit Form-Daten: {data}")

        try:
            response = requests.post(TARGET_URL, files=files, data=data)
            logging.info(f"Server-Antwort: {response.status_code} - {response.text}")

            if response.status_code == 200:
                logging.info("Upload erfolgreich, lösche Dateien...")
                for file_entry in files:
                    file_path = os.path.join(WATCHED_DIR, file_entry[1][0])
                    try:
                        os.remove(file_path)  # Datei nach erfolgreichem Upload löschen
                        logging.info(f"Datei gelöscht: {file_path}")
                    except Exception as e:
                        logging.error(f"Fehler beim Löschen von {file_path}: {e}")
            else:
                logging.error(f"Fehler beim Upload: {response.text}")

        except Exception as e:
            logging.error(f"Upload fehlgeschlagen: {e}")

        finally:
            # Alle geöffneten Dateien schließen
            for file_entry in files:
                file_entry[1][1].close()


def initial_check(handler):
    """Überprüft bereits vorhandene Dateien beim Start"""
    file_count = handler.count_files()
    logging.info(f"Initialer Datei-Check: {file_count} Dateien vorhanden")
    logging.debug(f"Aktuelle Anzahl FILE_THRESHOLD: {FILE_THRESHOLD}")

    if file_count >= FILE_THRESHOLD:
        logging.info("Schwellenwert bereits erreicht, starte Upload.")
        handler.send_files()

def listen_for_ws_messages():
    """ Lauscht auf WebSocket-Nachrichten, um den Watchdog zu aktivieren oder zu deaktivieren """
    global watchdog_active

    def on_start_watchdog():
        global watchdog_active
        watchdog_active = True
        logging.info("Watchdog aktiviert.")

    def on_stop_watchdog():
        global watchdog_active
        watchdog_active = False
        logging.info("Watchdog deaktiviert.")

    socket.on("start_watchdog", on_start_watchdog)
    socket.on("stop_watchdog", on_stop_watchdog)
    socket.wait()

if __name__ == "__main__":
    logging.info(f"Starte Datei-Überwachung in {WATCHED_DIR}")

    # Initialen Check durchführen
    handler = FileHandler()
    initial_check(handler)

    # Watchdog starten
    observer = Observer()
    observer.schedule(handler, path=WATCHED_DIR, recursive=True)
    observer.start()

    # Starte WebSocket-Listener im Hintergrund
    import threading
    threading.Thread(target=listen_for_ws_messages, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
