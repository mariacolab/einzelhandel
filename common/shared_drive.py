import logging
import os
import shutil
import time

# Setup logging
logging.basicConfig(level=logging.DEBUG)


def save_file_in_folder(folder, file):
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

def rename_file(old_filename, new_filename, folder):
    """
    Benennt eine Datei im gemounteten Verzeichnis um.

    :param old_filename: Name der Datei, die Umbenannt werden soll
    :param new_filename: Neuer Name der Datei
    :param folder: Pfad des gemounteten Verzeichnisses (z.B. "/mnt/gdrive/UPLOAD")
    """
    new_path = os.path.join(folder, new_filename)
    old_path = os.path.join(folder, old_filename)
    try:
        logging.info(f"Prüfe, ob Datei existiert: {old_path}")
        if not os.path.exists(old_path) or os.path.getsize(old_path) == 0:
            logging.error(f"Fehler: Datei nicht gefunden oder leer: {old_path}")
            return None

        logging.info(f"Versuche Datei umzubenennen: {old_path} -> {new_path}")
        shutil.move(old_path, new_path)
        logging.info(f"Datei erfolgreich umbenannt: {old_path} -> {new_path}")

        return new_path
    except Exception as e:
        logging.error(f"Fehler beim Umbenennen: {e}")
        return new_path


def copy_file_to_folder(source_file, new_folder, filename):
    """
    Kopiert eine Datei im gemounteten Verzeichnis in ein anderes Verzeichnis.

    :param source_file: zu speicherndes Bild
    :param new_folder: Pfad des gemounteten Verzeichnisses in dass die Datei verschoben werden soll
    :param filename: Datei, die in das gemountete Verzeichnis gespeichert werden soll
    """
    os.makedirs(new_folder, exist_ok=True)
    shutil.copy2(source_file, new_folder)


def get_file(filepath):
    """
    Lädt die Datei in ein Image.

    :param filepath: Datei mit Pfad im gemounteten Verzeichnisses (z.B. "/mnt/gdrive/UPLOAD")
    """
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            return file
    else:
        logging.info(f"Datei {filepath} existiert nicht!")

def del_file(filepath):
    """
    Löscht die Datei im gemounteten Verzeichnis.

    :param filepath: Datei mit Pfad im gemounteten Verzeichnisses (z.B. "/mnt/gdrive/UPLOAD")
    """
    if os.path.exists(filepath):
        # Datei löschen
        os.remove(filepath)
        logging.info(f"Datei {filepath} wurde gelöscht.")