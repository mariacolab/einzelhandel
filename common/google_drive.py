import logging
import os
import shutil
import time

# Setup logging
logging.basicConfig(level=logging.DEBUG)


def google_save_file_in_folder(folder, file):
    """
    Benennt eine Datei im gemounteten Verzeichnis um.

    :param folder: Pfad des gemounteten Verzeichnisses (z.B. "/mnt/gdrive/UPLOAD")
    :param file: Datei, die in das gemountete Verzeichnis gespeichert werden soll
    """
    if os.path.exists(folder):
        save_path = os.path.join(folder, file.filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Sicherstellen, dass das Verzeichnis existiert
        file.save(save_path)
        logging.debug(f"File {file.filename} saved to {save_path}")


def google_rename_file(old_filename, new_filename, folder):
    """
    Benennt eine Datei im gemounteten Verzeichnis um.

    :param old_filename: Name der Datei, die Umbenannt werden soll
    :param new_filename: Neuer Name der Datei
    :param folder: Pfad des gemounteten Verzeichnisses (z.B. "/mnt/gdrive/UPLOAD")
    """
    new_path = os.path.join(folder, new_filename)
    old_path = os.path.join(folder, old_filename)
    try:
        logging.info(f"Versuche Datei zu kopieren: {old_path} -> {new_path}")
        shutil.copy2(old_path, new_path)  # Kopiere mit Metadaten
        logging.info(f"Kopiert. Jetzt wird die Originaldatei gelöscht: {old_path}")
        shutil.move(old_path, new_path)  # Statt rename, nutze move
        logging.info(f"Datei erfolgreich umbenannt: {old_path} -> {new_path}")
        return new_path
    except Exception as e:
        logging.error(f"Fehler beim Umbenennen: {e}")
        return None

def wait_for_file(folder, filename, timeout=60, interval=2):
    """
    Überprüft, ob eine Datei im gemounteten Verzeichnis existiert und wartet darauf.

    :param folder: Pfad des gemounteten Verzeichnisses (z.B. "/mnt/gdrive/UPLOAD")
    :param filename: Name der Datei, die überprüft werden soll
    :param timeout: Maximale Wartezeit in Sekunden (Standard: 60)
    :param interval: Zeit zwischen den Prüfungen in Sekunden (Standard: 2)
    :return: True, wenn die Datei gefunden wurde, sonst False
    """
    file_path = os.path.join(folder, filename)
    start_time = time.time()

    while time.time() - start_time < timeout:
        if os.path.exists(file_path):
            print(f" Datei gefunden: {file_path}")
            return True
        print(f"Warten auf Datei: {filename} im Verzeichnis {folder}...")
        time.sleep(interval)

    print(f"Timeout! Datei {filename} wurde nicht innerhalb von {timeout} Sekunden gefunden.")
    return False


def google_copy_file_to_folder(old_folder, new_folder, filename):
    """
    Kopiert eine Datei im gemounteten Verzeichnis in ein anderes Verzeichnis.

    :param old_folder: Pfad des gemounteten Verzeichnisses (z.B. "/mnt/gdrive/UPLOAD")
    :param new_folder: Pfad des gemounteten Verzeichnisses in dass die Datei verschoben werden soll
    :param filename: Datei, die in das gemountete Verzeichnis gespeichert werden soll
    """
    os.makedirs(new_folder, exist_ok=True)

    quelle_datei = os.path.join(old_folder, filename)
    logging.info(f"Datei old {quelle_datei}")
    ziel_datei = os.path.join(new_folder, filename)
    logging.info(f"Datei old {ziel_datei}")

    # Prüft, ob Datei existiert
    if os.path.exists(quelle_datei):
        shutil.copy2(quelle_datei, ziel_datei)
        logging.info(f"Datei {filename} wurde in das Verzeichnis {new_folder} kopiert.")


def google_get_file(filepath):
    """
    Lädt die Datei in ein Image.

    :param filepath: Datei mit Pfad im gemounteten Verzeichnisses (z.B. "/mnt/gdrive/UPLOAD")
    """
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            return file
    else:
        logging.info(f"Datei {filepath} existiert nicht!")

def google_del_file(filepath):
    """
    Löscht die Datei im gemounteten Verzeichnis.

    :param filepath: Datei mit Pfad im gemounteten Verzeichnisses (z.B. "/mnt/gdrive/UPLOAD")
    """
    if os.path.exists(filepath):
        # Datei löschen
        os.remove(filepath)
        logging.info(f"Datei {filepath} wurde gelöscht.")