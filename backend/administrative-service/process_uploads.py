import os
import uuid
import filetype
import logging

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


def process_files():
    """
    Sucht Dateien im Uploads-Ordner, überprüft den Typ und benennt sie um.
    """
    if not os.path.exists(UPLOADS_DIR):
        logging.error(f"Uploads-Verzeichnis existiert nicht: {UPLOADS_DIR}")
        return

    for filename in os.listdir(UPLOADS_DIR):
        file_path = os.path.join(UPLOADS_DIR, filename)

        if not os.path.isfile(file_path):
            continue  # Überspringe, falls es kein regulärer Dateityp ist

        logging.info(f"Verarbeite Datei: {file_path}")

        # Überprüfe Magic Bytes
        if not validate_file_magic(file_path):
            logging.warning(f"Ungültiger Dateityp: {file_path}. Datei wird übersprungen.")
            continue

        # Benenne die Datei in einen generischen Namen um
        file = rename_file(file_path, UPLOADS_DIR)
        logging.info(f"Datei umbenannt: {file}")
        return file


if __name__ == "__main__":
    process_files()
