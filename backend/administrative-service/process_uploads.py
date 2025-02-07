import os
import uuid
import logging
import tempfile

from common.DriveFolders import DriveFolders
from common.google_drive import google_uploade_file_to_folder

# Pfad zu shared_uploads
UPLOADS_DIR = "/shared/uploads"

MAGIC_BYTES = {
    b'\xFF\xD8\xFF': 'JPEG image',
    b'\x89PNG\r\n\x1A\n': 'PNG image',
}

logging.basicConfig(level=logging.DEBUG)


def validate_file_magic(file_path):
    try:
        with open(file_path, 'rb') as file:
            # Read the first few bytes of the file
            file_header = file.read(8)  # Read enough bytes for all known signatures

            # Compare with known magic bytes
            for magic, file_type in MAGIC_BYTES.items():
                if file_header.startswith(magic):
                    return f"File type: {file_type}"

        return "Unknown file type"
    except Exception as e:
        return f"Error: {e}"


def rename_file(file_path, uploads_dir):
    """
    Benennt eine Datei in einen generischen Namen um.
    """
    file, extension = file_path.split(".", 1)
    new_name = f"{uuid.uuid4()}.{extension}"
    logging.info(f"Dateiendung: {extension}")
    logging.info(f"Datei: {new_name}")
    new_path = os.path.join(uploads_dir, new_name)
    os.rename(file_path, new_path)
    logging.info(f"Datei umbenannt: {file_path} -> {new_path}")
    return new_path


def process_files(filename, filepath):
    """
    Sucht Dateien im Uploads-Ordner, überprüft den Typ und benennt sie um.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, filename)
        os.rename(filepath, temp_file_path)

        # file_path = os.path.join(UPLOADS_DIR, filename)

        # if not os.path.exists(file_path):
        #    logging.error(f"Datei existiert nicht: {file_path}")
        #    return None

        # logging.info(f"Verarbeite Datei: {file_path}")

        file_type = validate_file_magic(temp_file_path)
        # Überprüfe Magic Bytes
        if not file_type:
            logging.warning(f"Ungültiger Dateityp: {temp_file_path}. Datei wird übersprungen.")
            return None

            # Benenne die Datei in einen generischen Namen um
        file = rename_file(temp_file_path, temp_file_path)
        logging.info(f"Datei umbenannt: {file}")
        directory, file_name = os.path.split(file)
        logging.info(f"Verzeichnispfad: {directory}")
        logging.info(f"Dateiname: {file_name}")
        fileid = google_uploade_file_to_folder(DriveFolders.UPLOAD, file_name, directory)

        return fileid, file_name


if __name__ == "__main__":
    process_files()
