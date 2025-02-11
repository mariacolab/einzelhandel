import mimetypes
import tempfile

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io
import os
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
# Google Drive API Authentication
SERVICE_ACCOUNT_FILE = "secrets/fapra-ki-einzelhandel-555f5e4a0722.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]

def google_auth():

    # Projekt-Root-Verzeichnis holen
    project_root = os.path.dirname(os.path.abspath(__file__))
    logging.info(f"project_root: {project_root}")
    # JSON-Datei im Projekt suchen
    file_path = os.path.join(project_root, SERVICE_ACCOUNT_FILE)
    logging.info(f"file_path: {file_path}")

    # Authentifizieren mit Service Account
    scope = SCOPES
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

def google_drive_service():
    # Projekt-Root-Verzeichnis holen
    project_root = os.path.dirname(os.path.abspath(__file__))
    logging.info(f"project_root: {project_root}")
    # JSON-Datei im Projekt suchen
    file_path = os.path.join(project_root, SERVICE_ACCOUNT_FILE)
    logging.info(f"file_path: {file_path}")

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        file_path,
        scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)

def google_get_file_stream(folder_id, file_name=None, file_id=None):
    """
    Streamt eine Datei aus Google Drive entweder anhand des Dateinamens oder der Datei-ID.
    Falls der Dateiname nicht existiert, versucht es die Datei-ID zu verwenden und umgekehrt.

    :param folder_id: ID des Google Drive-Ordners, in dem die Datei liegt.
    :param file_name: (Optional) Name der Datei.
    :param file_id: (Optional) ID der Datei.
    :return: BytesIO-Stream der Datei oder None, falls die Datei nicht gefunden wird.
    """
    service = google_drive_service()

    # Falls eine Datei-ID angegeben ist, versuche sie direkt zu laden
    if file_id:
        try:
            request = service.files().get_media(fileId=file_id)
            file_stream = io.BytesIO()
            downloader = MediaIoBaseDownload(file_stream, request)

            done = False
            while not done:
                _, done = downloader.next_chunk()

            file_stream.seek(0)  # Zurück zum Anfang setzen
            logging.info(f"File with ID '{file_id}' loaded into memory stream successfully.")
            return file_stream
        except Exception as e:
            logging.error(f"Error loading file with ID '{file_id}': {e}")

    # Falls die Datei-ID nicht vorhanden ist oder fehlschlägt, suche nach dem Dateinamen
    if file_name:
        query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get("files", [])

        if files:
            file_id = files[0]["id"]
            logging.info(f"Found file: {file_name} (ID: {file_id}) in folder {folder_id}")

            # Datei mit der gefundenen ID streamen
            try:
                request = service.files().get_media(fileId=file_id)
                file_stream = io.BytesIO()
                downloader = MediaIoBaseDownload(file_stream, request)

                done = False
                while not done:
                    _, done = downloader.next_chunk()

                file_stream.seek(0)  # Zurück zum Anfang setzen
                logging.info(f"File '{file_name}' loaded into memory stream successfully.")
                return file_stream
            except Exception as e:
                logging.error(f"Error loading file '{file_name}' with ID '{file_id}': {e}")

        logging.error(f"File '{file_name}' not found in folder ID {folder_id}.")

    logging.error("No valid file_name or file_id provided or file not found.")
    return None  # Falls keine Datei gefunden wurde

def google_rename_file(file_id, new_name):
    try:
        # Fetch file metadata
        file = _drive.CreateFile({'id': file_id})
        file.FetchMetadata()

        logging.info(f"Current file name: {file['title']}, ID: {file_id}")

        # Rename the file
        file['title'] = new_name
        file.Upload()

        logging.info(f"File renamed successfully to {new_name}")
    except Exception as e:
        logging.error(f"Error renaming file: {e}")

def google_upload_file_to_drive(folder_id, file):
    """
    Uploads a file received from a POST request to Google Drive.

    :param file: The file object from request.files['file']
    :param folder_id: The Google Drive folder ID where the file should be uploaded.
    :return: Google Drive file ID
    """
    try:
        logging.info(f"Uploading file: {file.filename} to Google Drive Folder: {folder_id}")

        # Reset file pointer before reading
        file.seek(0)

        # Save to a temporary file with explicit binary mode
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(file.read())  # Save binary content
            temp_file_path = temp_file.name

        # Check if file was written correctly
        if os.path.getsize(temp_file_path) == 0:
            logging.error("Temporary file is empty. Possible file read issue.")
            return None

        logging.info(f"Temp file created at: {temp_file_path}, Size: {os.path.getsize(temp_file_path)} bytes")

        # Create file on Google Drive
        drive_file = _drive.CreateFile({
            'title': file.filename,
            'mimeType': file.mimetype,
            'parents': [{'id': folder_id}]
        })
        drive_file.SetContentFile(temp_file_path)
        drive_file.Upload()

        # Remove temp file
        os.remove(temp_file_path)

        logging.info(f"File uploaded successfully: {drive_file['title']}, ID: {drive_file['id']}")
        return drive_file['id']


    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return None

def google_stream_file_to_new_file(source_file_id, new_file_name, folder_id=None):
    service = google_drive_service()

    # 1️⃣ Datei aus Google Drive in ein io.BytesIO-Objekt streamen
    file_stream = io.BytesIO()
    request = service.files().get_media(fileId=source_file_id)
    downloader = MediaIoBaseDownload(file_stream, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    file_stream.seek(0)  # Stream auf Anfang setzen

    # 2️⃣ Datei direkt aus dem Stream in Google Drive hochladen
    file_metadata = {
        'name': new_file_name,
        'parents': [folder_id] if folder_id else []
    }

    media = MediaIoBaseUpload(file_stream, mimetype="application/octet-stream", resumable=True)
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f"File uploaded successfully: {uploaded_file.get('id')}")
    return uploaded_file.get("id")

#def get_mime_type(filename):
#    mime_type, _ = mimetypes.guess_type(filename)
#    return mime_type if mime_type else "application/octet-stream"