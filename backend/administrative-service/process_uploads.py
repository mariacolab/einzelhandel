import logging
import os
import uuid
from pathlib import Path

from common.SharedFolders import SharedFolders

UPLOADS_DIR = "/shared/uploads"

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
        return f"Error validate_file_magic: {e}"


def rename_file(filename, file_path):
    """
    Benennt eine Datei in einen generischen Namen um.
    """
    logging.info("rename_file")
    extension = Path(filename).suffix
    new_name = f"{uuid.uuid4()}.{extension}"
    logging.info(f"Dateiendung: {extension}")
    logging.info(f"Datei: {new_name}")
    new_path = os.path.join(file_path, new_name)
    os.rename(file_path, new_path)
    logging.info(f"Datei umbenannt: {file_path} -> {new_path}")
    return new_path


def process_files(filename):
    """
    Sucht Dateien im Uploads-Ordner, überprüft den Typ und benennt sie um.
    """
    if not os.path.exists(SharedFolders.UPLOAD.value):
        logging.error(f"Uploads-Verzeichnis existiert nicht: {SharedFolders.UPLOAD.value}")
        return

    file_path = os.path.join(SharedFolders.UPLOAD.value, filename)

    logging.info(f"Verarbeite Datei: {file_path}")

    # Überprüfe Magic Bytes
    if not validate_file_magic(file_path):
        logging.warning(f"Ungültiger Dateityp: {file_path}. Datei wird übersprungen.")

        # Benenne die Datei in einen generischen Namen um
    file = rename_file(filename, SharedFolders.UPLOAD.value)
    logging.info(f"Datei umbenannt: {file}")
    return file


if __name__ == "__main__":
    filename = ""
    process_files(filename)
