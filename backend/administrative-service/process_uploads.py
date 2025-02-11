import logging
import os
import tempfile
import uuid
from pathlib import Path

from common.DriveFolders import DriveFolders
from common.google_drive import google_uploade_file_to_folder, google_download_file, google_rename_file

# Pfad zu shared_uploads
# UPLOADS_DIR = "/shared/uploads"

MAGIC_BYTES = {
    b'\xFF\xD8\xFF': 'JPEG image',
    b'\x89PNG\r\n\x1A\n': 'PNG image',
}

logging.basicConfig(level=logging.DEBUG)


def validate_file_magic(fileid):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            local_file_path = google_download_file(fileid, temp_dir)
            logging.info("validate_file_magic")
            with open(local_file_path, 'rb') as file:
                # Read the first few bytes of the file
                file_header = file.read(8)  # Read enough bytes for all known signatures

                # Compare with known magic bytes
                for magic, file_type in MAGIC_BYTES.items():
                    if file_header.startswith(magic):
                        return f"File type: {file_type}"

            return "Unknown file type"
    except Exception as e:
        return f"Error: {e}"

def rename_file(filename, fileid):
    """
    Benennt eine Datei in einen generischen Namen um.
    """
    logging.info("rename_file")
    extension = Path(filename).suffix
    new_name = f"{uuid.uuid4()}{extension}"
    logging.info(f"Dateiendung: {extension}")
    logging.info(f"Datei: {new_name}")
    google_rename_file(fileid, new_name)


def process_files(filename, fileid):
    """
    Sucht Dateien im Uploads-Ordner, überprüft den Typ und benennt sie um.
    """
    logging.info("methode process_files")
    file_type = validate_file_magic(fileid)
    # Überprüfe Magic Bytes
    if not file_type:
        logging.warning(f"Ungültiger Dateityp: {filename}. Datei wird übersprungen.")

    # Benenne die Datei in einen generischen Namen um
    rename_file(filename, fileid)



if __name__ == "__main__":
    process_files()
