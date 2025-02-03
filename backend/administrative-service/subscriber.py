import json
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import aio_pika
import asyncio
from oauth2client.service_account import ServiceAccountCredentials
import requests

from common.utils import load_secrets
import logging
from process_uploads import process_files

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Load secrets
try:
    secrets = load_secrets()
    password = secrets.get('RABBITMQ_PASSWORD')
    logging.debug(f"Loaded password: {password}")
    RABBITMQ_URL = "amqp://guest:{}@rabbitmq:5672".format(password)
    logging.debug(f"Loaded RABBITMQ_URL: {RABBITMQ_URL}")
except Exception as e:
    logging.error(f"Error loading secrets: {e}")
    raise


async def on_message(message: aio_pika.IncomingMessage, ):
    async with message.process():
        try:
            event = message.body.decode()
            logging.debug(f"Received event: {event}")

            event_corrected = event.replace("'", '"')
            logging.debug(f"Corrected event JSON: {event_corrected}")

            event = json.loads(event_corrected)
            logging.debug(f"Parsed event: {event}")

            event_type = event.get("type", "")
            event_filename = event.get("filename", "")
            event_path = event.get("path", "")
            event_model= event.get("model", "")
            logging.info(f"Event type: {event_type}")
            logging.info(f"Event filename: {event_filename}")
            logging.info(f"Event path: {event_path}")

            token = event.get("token", "")
            if not token:
                logging.warning("Token not found in event payload")
                return

            logging.info(f"Extracted token: {token}")

            #
            if "ProcessFiles" in event_type:
                logging.info("Processing files after ImageUploaded event.")
                processed_file = process_files(event_filename)
                logging.info(f"{processed_file}")

                directory, file_name = os.path.split(processed_file)

                logging.info(f"Verzeichnispfad: {directory}")
                logging.info(f"Dateiname: {file_name}")

                gauth = GoogleAuth()
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

                ORDNER_ID = "1xoA3-4RWkeizafEYUqfovjgD6Q3oSR7q"

                file = drive.CreateFile({
                    'title': f"{file_name}",
                    'mimeType': 'image/jpeg',
                    'parents': [{'id': ORDNER_ID}]
                })
                file.SetContentFile(f"{processed_file}")  # Lokale Datei setzen
                file.Upload()
                logging.debug(f"Bild hochgeladen: {file['title']}, ID: {file['id']}")
                # löschen der Datei im shared Verzeichnis
                logging.info(f"Bild hochgeladen in Ordner: https://drive.google.com/drive/folders/{ORDNER_ID}")
                # Google Drive API-Berechtigungen setzen
                file.InsertPermission({
                    'type': 'user',          # Berechtigung für ein bestimmtes Konto
                    'value': 'fapra73@gmail.com',  # Ersetze mit deiner Google-Mail-Adresse
                    'role': 'writer'         # Alternativ 'reader' für nur-Lese-Zugriff
                })

                FILE_ID = f"{file['id']}"

                logging.info(f"Datei geteilt mit: fapra73@gmail.com")

                # get all files from user
                file_list = drive.ListFile({'q': "trashed=false"}).GetList()

                # Print all file names and IDs
                for file in file_list:
                    logging.info(f"File: {file['title']} - ID: {file['id']}")

                #get all files from folder
                file_list = drive.ListFile({'q': f"'{ORDNER_ID}' in parents and trashed=false"}).GetList()

                # Dateien ausgeben
                for file in file_list:
                    logging.info(f"Datei: {file['title']} - ID: {file['id']}")

                #datei in anderen Ordner verschieben
                NEW_FOLDER_ID = "1BV9kt1H9r9qSUcVAcFjSxFWvOxFfDwYm"

                # Datei abrufen
                file = drive.CreateFile({'id': FILE_ID})
                file.FetchMetadata()  # Aktuelle Metadaten abrufen

                # Alten Ordner entfernen (falls die Datei schon in einem Ordner war)
                if 'parents' in file:
                    previous_parents = ",".join(parent['id'] for parent in file['parents'])
                    file['parents'] = [{'id': NEW_FOLDER_ID}]  # Neuen Ordner setzen
                    file.Upload(param={'removeParents': previous_parents})  # Verschieben

                logging.info(f"Datei verschoben: {file['title']} nach Ordner ID {NEW_FOLDER_ID}")

                #delete file
                file_list = drive.ListFile({'q': f"'{FILE_ID}' in parents"}).GetList()

                if file_list:
                    file = drive.CreateFile({'id': FILE_ID})
                    file.Delete()
                    logging.info(f"Datei {file['title']} mit ID {FILE_ID} wurde gelöscht.")
                else:
                    logging.info(f"Datei mit ID {FILE_ID} nicht gefunden!")

                # Datei mit dem Namen im angegebenen Ordner suchen
                query = f"title = '{file['title']}' and '{NEW_FOLDER_ID}' in parents and trashed=false"
                file_list = drive.ListFile({'q': query}).GetList()

                if file_list:
                    for file in file_list:
                        logging.info(f"Lösche Datei: {file['title']} - ID: {file['id']}")
                        file.Delete()
                    logging.info("Datei(en) erfolgreich gelöscht.")
                else:
                    logging.info(f"Keine Datei mit dem Namen '{file['title']}' im Ordner gefunden.")

                url = " http://nginx-proxy/eventing-service/publish/ImageValidated"
                headers = {
                    "Authorization": f"{token}"
                }
                files = {
                    "type": (None, "ValidatedFiles"),
                    "model": event_model,
                    "file": (f"{file_name}", open(f"{processed_file}", "rb")),
                }


                response = requests.post(url, headers=headers, files=files)
                logging.info(f"Response: {response}")

        except Exception as e:
            logging.error(f"Error processing message: {e}")


async def main():
    try:
        logging.info("Starting RabbitMQ subscriber.")
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            logging.info("Connected to RabbitMQ.")
            channel = await connection.channel()
            exchange = await channel.declare_exchange("events", aio_pika.ExchangeType.TOPIC, durable=True)
            queue = await channel.declare_queue("process_files_queue", durable=True)
            await queue.bind(exchange, routing_key="ProcessFiles")  # Beispiel: Lauschen auf "ProcessFiles"

            await queue.consume(on_message)
            logging.info("Waiting for messages. To exit press CTRL+C.")
            await asyncio.Future()  # Blockiert, um Nachrichten zu empfangen
    except Exception as e:
        logging.error(f"Error in RabbitMQ connection or setup: {e}")
        await asyncio.sleep(5)  # Delay before retrying
        await main()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
