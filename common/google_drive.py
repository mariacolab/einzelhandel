from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io
import torch
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

_drive = google_auth()
def google_uploade_file_to_folder(folderId, file_name, file_path):

    #ORDNER_ID = "1xoA3-4RWkeizafEYUqfovjgD6Q3oSR7q"
    file = _drive.CreateFile({
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

    # Delete the local file after upload
    os.remove(file_path)
    logging.info(f"Local file deleted: {file_path}")

    file_id = f"{file['id']}"
    return file_id

def google_get_all_files_from_user():

    # get all files from user
    file_list = _drive.ListFile({'q': "trashed=false"}).GetList()

    # Print all file names and IDs
    for file in file_list:
        logging.info(f"File: {file['title']} - ID: {file['id']}")

def google_get_all_files_from_folder(folderId):
    #get all files from folder
    file_list = _drive.ListFile({'q': f"'{folderId}' in parents and trashed=false"}).GetList()

    # Dateien ausgeben
    for file in file_list:
        logging.info(f"Datei: {file['title']} - ID: {file['id']}")

def google_move_to_another_folder(fileId, newFolderId):
    #datei in anderen Ordner verschieben
    #NEW_FOLDER_ID = "1BV9kt1H9r9qSUcVAcFjSxFWvOxFfDwYm"
    # Datei abrufen
    file = _drive.CreateFile({'id': fileId})
    file.FetchMetadata()  # Aktuelle Metadaten abrufen

    # Alten Ordner entfernen (falls die Datei schon in einem Ordner war)
    if 'parents' in file:
        previous_parents = ",".join(parent['id'] for parent in file['parents'])
        file['parents'] = [{'id': newFolderId}]  # Neuen Ordner setzen
        file.Upload(param={'removeParents': previous_parents})  # Verschieben

    logging.info(f"Datei verschoben: {file['title']} nach Ordner ID {newFolderId}")

def google_delete_file(fileId):
    #delete file
    file_list = _drive.ListFile({'q': f"'{fileId}' in parents"}).GetList()

    if file_list:
        file = _drive.CreateFile({'id': fileId})
        file.Delete()
        logging.info(f"Datei {file['title']} mit ID {fileId} wurde gelöscht.")
    else:
        logging.info(f"Datei mit ID {fileId} nicht gefunden!")

def google_check_if_file_in_folder(filename, folderId):
    # Datei mit dem Namen im angegebenen Ordner suchen
    query = f"title = '{filename}' and '{folderId}' in parents and trashed=false"
    file_list = _drive.ListFile({'q': query}).GetList()

    if file_list:
        for file in file_list:
            logging.info(f"Datei gefunden: {file['title']} - ID: {file['id']}")
    else:
        logging.info(f"Keine Datei mit dem Namen '{filename}' found in the folder.")

def google_get_file(file_id):
    file = _drive.CreateFile({'id': file_id})
    file.FetchMetadata()  # Fetch the latest metadata
    logging.info(f"File Found: {file['title']}")
    logging.info(f"File Size: {file.get('fileSize', 'Unknown')} bytes")
    logging.info(f"MIME Type: {file['mimeType']}")
    return file

def google_download_file(file_id, save_path):

    try:
        file = _drive.CreateFile({'id': file_id})
        file.FetchMetadata()

        # Extract file name from metadata
        file_name = file['title']
        file_path = os.path.join(save_path, file_name)

        # Download the file
        file.GetContentFile(file_path)
        logging.info(f"File downloaded: {file_name} -> {file_path}")

        return file_path
    except Exception as e:
        logging.error(f"Error downloading file from Google Drive: {e}")
        return None

def google_get_file_in_folder(folder_id, file_name, save_path):

    try:
        # Search for the file in the given folder
        query = f"title = '{file_name}' and '{folder_id}' in parents and trashed = false"
        file_list = _drive.ListFile({'q': query}).GetList()

        if not file_list:
            logging.error(f"File '{file_name}' not found in folder ID: {folder_id}")
            return None

        # Assuming the first match is the correct file
        file_drive = file_list[0]

        # Define the local file path
        file_path = os.path.join(save_path, file_drive['title'])

        # Download the file
        file_drive.GetContentFile(file_path)
        logging.info(f"File downloaded: {file_drive['title']} -> {file_path}")

        return file_path
    except Exception as e:
        logging.error(f"Error fetching file from Google Drive: {e}")
        return None

# Google Drive API Authentication
SERVICE_ACCOUNT_FILE = "secrets/fapra-ki-einzelhandel-6f215d4ad989.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]

def google_drive_service():
    """Authenticate and return Google Drive service instance."""
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)

def google_get_file_stream(folder_id, file_name):
    """
    Get a file from Google Drive via folder ID and file name and return as a stream.
    """
    service = google_drive_service()

    # Search for the file in the folder
    query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if not files:
        logging.error(f"File '{file_name}' not found in folder ID {folder_id}.")
        return None

    file_id = files[0]["id"]
    logging.info(f"Found file: {file_name} (ID: {file_id}) in folder {folder_id}")

    # Create an in-memory stream
    file_stream = io.BytesIO()

    # Request to stream the file
    request = service.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(file_stream, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    file_stream.seek(0)  # Reset the stream position to the beginning
    logging.info(f"File '{file_name}' loaded into memory stream successfully.")

    return file_stream  # Now you can use this stream without saving locally
