import logging
import os
import shutil

# Setup logging
logging.basicConfig(level=logging.DEBUG)


def google_save_file_in_folder(folder, file):
    if os.path.exists(folder):
        save_path = f"{folder}{file.filename}"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Sicherstellen, dass das Verzeichnis existiert
        file.save(save_path)
        logging.debug(f"File {file.filename} saved to {save_path}")


def google_rename_file(old_filename, new_filename, folder):
    new_path = os.path.join(folder, new_filename)
    os.rename(folder, new_path)
    logging.info(f"Datei umbenannt: {folder}{old_filename} -> {new_path}")
    return new_path


def google_copy_file_to_folder(old_folder, new_folder, filename):
    # prüft, ob dass das Zielverzeichnis existiert
    os.makedirs(new_folder, exist_ok=True)

    quelle_datei = os.path.join(old_folder, filename)
    ziel_datei = os.path.join(new_folder, filename)

    # Prüft, ob Datei existiert
    if os.path.exists(quelle_datei):
        shutil.copy2(quelle_datei, ziel_datei)
        logging.info(f"Datei {filename} wurde in das Verzeichnis {new_folder} kopiert.")


def google_get_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            return file
    else:
        logging.info(f"Datei {filepath} existiert nicht!")

def google_del_file(filepath):
    if os.path.exists(filepath):
        # Datei löschen
        os.remove(filepath)
        logging.info(f"Datei {filepath} wurde gelöscht.")