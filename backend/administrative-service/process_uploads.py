import logging
import os
import tempfile
import uuid
from pathlib import Path

from common.DriveFolders import DriveFolders
from common.google_drive import google_rename_file

MAGIC_BYTES = {
    b'\xFF\xD8\xFF': 'JPEG image',
    b'\x89PNG\r\n\x1A\n': 'PNG image',
}

logging.basicConfig(level=logging.DEBUG)


def validate_file_magic(file_path):
    try:
        logging.info("validate_file_magic")
        with open(file_path, 'rb') as file:
            # liest die ersten Bytes der Datei
            file_header = file.read(8)

            # vergleicht sie mit bekannten magic bytes
            for magic, file_type in MAGIC_BYTES.items():
                if file_header.startswith(magic):
                    return f"File type: {file_type}"
    except Exception as e:
        return f"Error: {e}"


def rename_file(filename):
    """
    Benennt eine Datei in einen generischen Namen um.
    """
    logging.info("rename_file")
    extension = Path(filename).suffix
    new_name = f"{uuid.uuid4()}{extension}"
    logging.info(f"Dateiendung: {extension}")
    logging.info(f"Datei: {new_name}")
    new_path = google_rename_file(filename, new_name, DriveFolders.UPLOAD.value)
    return new_path


def process_files(filename):
    """
    Sucht Dateien im Uploads-Ordner, überprüft den Typ und benennt sie um.
    """
    if not os.path.exists(DriveFolders.UPLOAD.value):
        logging.error(f"Uploads-Verzeichnis existiert nicht: {DriveFolders.UPLOAD.value}")
        return

    file_path = os.path.join(DriveFolders.UPLOAD.value, filename)


    logging.info(f"Verarbeite Datei: {file_path}")

    # Überprüfe Magic Bytes
    if not validate_file_magic(file_path):
        logging.warning(f"Ungültiger Dateityp: {file_path}. Datei wird übersprungen.")

        # Benenne die Datei in einen generischen Namen um
    file = rename_file(filename)
    logging.info(f"Datei umbenannt: {file}")
    return file


if __name__ == "__main__":
    filename=""
    process_files(filename)
