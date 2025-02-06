from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import os
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def google_auth():

    # Projekt-Root-Verzeichnis holen
    project_root = os.path.dirname(os.path.abspath(__file__))
    logging.info(f"project_root: {project_root}")
    # JSON-Datei im Projekt suchen
    file_path = os.path.join(project_root, "secrets/fapra-ki-einzelhandel-6f215d4ad989.json")
    logging.info(f"file_path: {file_path}")

    # Authentifizieren mit Service Account
    scope = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(file_path, scope)

    # GoogleAuth mit den Service-Credentials
    gauth = GoogleAuth()
    gauth.credentials = credentials
    drive = GoogleDrive(gauth)
    return drive

def google_uploade_file_to_folder(folderId, file_name, file_path):

    #ORDNER_ID = "1xoA3-4RWkeizafEYUqfovjgD6Q3oSR7q"
    drive = google_auth()
    file = drive.CreateFile({
        'title': f"{file_name}",
        'mimeType': 'image/jpeg',
        'parents': [{'id': folderId}]
    })
    file.SetContentFile(f"{file_path}")  # Lokale Datei setzen
    file.Upload()
    logging.debug(f"Bild hochgeladen: {file['title']}, ID: {file['id']}")
    # löschen der Datei im shared Verzeichnis
    logging.info(f"Bild hochgeladen in Ordner: https://drive.google.com/drive/folders/{folderId}")
    # Google Drive API-Berechtigungen setzen
    file.InsertPermission({
        'type': 'user',          # Berechtigung für ein bestimmtes Konto
        'value': 'fapra73@gmail.com',  # Ersetze mit deiner Google-Mail-Adresse
        'role': 'writer'         # Alternativ 'reader' für nur-Lese-Zugriff
    })
    logging.info(f"Datei geteilt mit: fapra73@gmail.com")

    file_id = f"{file['id']}"
    return file_id

def google_get_all_files_from_user():
    drive = google_auth()
    # get all files from user
    file_list = drive.ListFile({'q': "trashed=false"}).GetList()

    # Print all file names and IDs
    for file in file_list:
        logging.info(f"File: {file['title']} - ID: {file['id']}")

def google_get_all_files_from_folder(folderId):
    #get all files from folder
    drive = google_auth()
    file_list = drive.ListFile({'q': f"'{folderId}' in parents and trashed=false"}).GetList()

    # Dateien ausgeben
    for file in file_list:
        logging.info(f"Datei: {file['title']} - ID: {file['id']}")

def google_move_to_another_folder(fileId, newFolderId):
    #datei in anderen Ordner verschieben
    #NEW_FOLDER_ID = "1BV9kt1H9r9qSUcVAcFjSxFWvOxFfDwYm"
    drive = google_auth()
    # Datei abrufen
    file = drive.CreateFile({'id': fileId})
    file.FetchMetadata()  # Aktuelle Metadaten abrufen

    # Alten Ordner entfernen (falls die Datei schon in einem Ordner war)
    if 'parents' in file:
        previous_parents = ",".join(parent['id'] for parent in file['parents'])
        file['parents'] = [{'id': newFolderId}]  # Neuen Ordner setzen
        file.Upload(param={'removeParents': previous_parents})  # Verschieben

    logging.info(f"Datei verschoben: {file['title']} nach Ordner ID {newFolderId}")

def google_delete_file(fileId):
    drive = google_auth()
    #delete file
    file_list = drive.ListFile({'q': f"'{fileId}' in parents"}).GetList()

    if file_list:
        file = drive.CreateFile({'id': fileId})
        file.Delete()
        logging.info(f"Datei {file['title']} mit ID {fileId} wurde gelöscht.")
    else:
        logging.info(f"Datei mit ID {fileId} nicht gefunden!")

def google_check_if_file_in_folder(filename, folderId):
    # Datei mit dem Namen im angegebenen Ordner suchen
    drive = google_auth()
    query = f"title = '{filename}' and '{folderId}' in parents and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()

    if file_list:
        for file in file_list:
            logging.info(f"Datei gefunden: {file['title']} - ID: {file['id']}")
    else:
        logging.info(f"Keine Datei mit dem Namen '{filename}' found in the folder.")
