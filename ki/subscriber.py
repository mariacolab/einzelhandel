import json
import mimetypes
import os
import random
import aio_pika
import asyncio
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from my_function_TF import predict_object_TF

import requests
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

from common.middleware import get_user_role_from_token
from common.utils import load_secrets

import logging
from detectYOLO11 import detect

from common.utils import load_secrets

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


async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            event = message.body.decode()
            logging.debug(f"Received event: {event}")

            event_corrected = event.replace("'", '"')
            logging.debug(f"Corrected event JSON: {event_corrected}")

            event = json.loads(event_corrected)
            logging.debug(f"Parsed event: {event}")

            event_type = event.get("type", "")
            logging.info(f"Event type: {event_type}")

            token = event.get("token", "")

            if not token:
                logging.warning("Token not found in event payload")
                return

            logging.info(f"Extracted token: {token}")

            #
            if "ValidatedFiles" in event_type:

                event_filename = event.get("file", "")
                event_path = event.get("path", "")
                event_model = event.get("model", "")
                logging.info(f"Event type: {event_model}")
                logging.info(f"Event file: {event_filename}")
                logging.info(f"Event path: {event_path}")

                logging.info("Processing files after ImageUploaded event.")


                # TODO aufruf von Methoden um weiteren Code auszuführen

                user_role = get_user_role_from_token()

                if event_model == "big":
                  result = detect(f"{event_path}{event_filename}",f"{event_filename}", user_role)
                elif event_model == "small":
                  img_file = f"{event_path}{event_filename}"
                  img = plt.imread(img_file)  # Lädt das Bild als NumPy-Array
                  img = np.resize(img, (128, 128, 3))

                  class_name = predict_object_TF(img)
                  #class_name = predict_object_YOLO(img_file)
                  #logging.info(f"Exampleresult: {class_name}")

                logging.info(f"result from image: {result}")


                # TODO Rolle filtern wenn Kunde dann erhält er bei FaLse eine Fehlermeldung in classification
                is_classification_correct = True

                if is_classification_correct:
                    # löschen der Datei im shared Verzeichnis
                    try:
                        # Überprüfen, ob die Datei existiert
                        if os.path.exists(f"{event_path}{event_filename}"):
                            os.remove(f"{event_path}{event_filename}")
                            logging.debug(f"Datei {event_path}{event_filename} wurde erfolgreich gelöscht.")
                        else:
                            logging.debug(f"Datei {event_path}{event_filename} wurde nicht gefunden.")
                    except Exception as e:
                        logging.error(f"Fehler beim Löschen der Datei: {e}")
                    url = " http://nginx-proxy/eventing-service/publish/ClassificationCompleted"
                    headers = {
                        "Authorization": f"{token}"
                    }
                    files = {
                        "type": (None, "ClassFiles"),
                        "result": (None, result),
                    }
                    response = requests.post(url, headers=headers, files=files)
                    logging.info(f"Response: {response}")
                elif is_classification_correct == False and user_role != "Kunde":
                    url = " http://nginx-proxy/eventing-service/publish/MisclassificationReported"
                    headers = {
                        "Authorization": f"{token}"
                    }
                    files = {
                        "type": (None, "MisclassifiedFiles"),
                        "classification": (None, result),
                        "filename": (f"{event_filename}", open(f"{event_path}{event_filename}", "rb")),
                    }
                    response = requests.post(url, headers=headers, files=files)
                    logging.info(f"Response: {response}")
                else:
                    logging.info("Fehlermeldung für Kunde")
            if "CorrectedFiles" in event_type:
                event_classification = event.get("classification", "")
                event_class_correct = event.get("is_classification_correct ", "")
                event_filename = event.get("filename", "")
                event_path = event.get("path ", "")
                logging.info(f"Event file: {event_classification}")
                logging.info(f"Event path: {event_class_correct}")
                if event_class_correct:
                    # löschen der Datei im shared Verzeichnis
                    try:
                        # Überprüfen, ob die Datei existiert
                        if os.path.exists(f"{event_path}{event_filename}"):
                            os.remove(f"{event_path}{event_filename}")
                            logging.debug(f"Datei {event_path}{event_filename} wurde erfolgreich gelöscht.")
                        else:
                            logging.debug(f"Datei {event_path}{event_filename} wurde nicht gefunden.")
                    except Exception as e:
                        logging.error(f"Fehler beim Löschen der Datei: {e}")

                    url = " http://nginx-proxy/eventing-service/publish/ClassificationCompleted"
                    headers = {
                        "Authorization": f"{token}"
                    }
                    files = {
                        "type": (None, "ClassFiles"),
                        "result": (None, event_classification),
                    }
                    response = requests.post(url, headers=headers, files=files)
                    logging.info(f"Response: {response}")
                else:
                    logging.info(f"Event file: {event_classification}")
                    # TODO Datei in Googledrive ablegen

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

                    ORDNER_ID = "1BV9kt1H9r9qSUcVAcFjSxFWvOxFfDwYm"

                    file = drive.CreateFile({
                        'title': f"{event_filename}",
                        'mimeType': 'image/jpeg',
                        'parents': [{'id': ORDNER_ID}]
                    })
                    file.SetContentFile(f"{event_path}{event_filename}")  # Lokale Datei setzen
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

                    logging.info(f"Datei geteilt mit: fapra73@gmail.com")

                    # löschen der Datei im shared Verzeichnis
                    try:
                        # Überprüfen, ob die Datei existiert
                        if os.path.exists(f"{event_path}{event_filename}"):
                            os.remove(f"{event_path}{event_filename}")
                            logging.debug(f"Datei {event_path}{event_filename} wurde erfolgreich gelöscht.")
                        else:
                            logging.debug(f"Datei {event_path}{event_filename} wurde nicht gefunden.")
                    except Exception as e:
                        logging.error(f"Fehler beim Löschen der Datei: {e}")

                    logging.info("Fehlerhafte Klassifizierung")
        except Exception as e:
            logging.error(f"Error processing message: {e}")


def get_mime_type(filename):
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type if mime_type else "application/octet-stream"


async def main():
    try:
        logging.info("Starting RabbitMQ subscriber.")
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            logging.info("Connected to RabbitMQ.")
            channel = await connection.channel()
            exchange = await channel.declare_exchange("events", aio_pika.ExchangeType.TOPIC, durable=True)
            queue_validated = await channel.declare_queue("image_validated_queue", durable=True)
            await queue_validated.bind(exchange, routing_key="ValidatedFiles")  # Beispiel: Lauschen auf "ProcessFiles"

            queue_corrected = await channel.declare_queue("process_corrected_classified_queue", durable=True)
            await queue_corrected.bind(exchange, routing_key="CorrectedFiles")

            await queue_corrected.consume(on_message)

            await queue_validated.consume(on_message)
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
