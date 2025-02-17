import os

import aio_pika
import asyncio
from common.DriveFolders import DriveFolders
from common.google_drive import google_copy_file_to_folder, wait_for_file
import requests
import json
import logging
from PIL import Image
from common.product_data import get_product_with_data
from detectYOLO11 import detect, pfad_zerlegen, retrain
from common.utils import load_secrets
from rh_TF_Predict import predict_object_TF

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
            event_filepath = event.get("filepath", "")
            event_cookie = event.get("cookie", "")
            event_role = event.get("role", "")

            logging.info(f"Event type: {event_type}")
            logging.info(f"Event filepath: {event_filepath}")
            logging.info(f"Event cookie: {event_cookie}")
            logging.info(f"Event role: {event_role}")

            if "ValidatedFiles" in event_type:
                wait_for_file(DriveFolders.UPLOAD.value, event_filepath, 10, 1)
                logging.info("Processing files after ImageUploaded event.")
                event_filename = event.get("file", "")
                path,file_without_path =  event_filename.rsplit('/',1)
                logging.info(f"Event filename: {event_filename}")
                logging.info(f"Event filename without path is : {file_without_path}")

                #aufruf der KI
                class_names = ['Apfel', 'Aubergine', 'Avocado', 'Birne',
                               'Granatapfel', 'Kaki', 'Kartoffel', 'Kiwi',
                               'Mandarine', 'Orange', 'Pampelmuse', 'Paprika',
                               'Tomate', 'Zitrone', 'Zucchini', 'Zwiebel']
                image = Image.open(f"{DriveFolders.UPLOAD.value}/{file_without_path}")
                result1, yolo_result  = detect(image, event_filename) # großes Modell
                retrain()
                if result1 in class_names:
                    result2 = predict_object_TF(event_filepath, event_filename) #kleines Modell
                else:
                    result2=None
                if not result2 or result1==result2:
                        result = result1
                logging.info(f"result from image: {result}")
                #TODO wenn verschiedene Ergebnisse
                if event_role == "Kunde":
                    """
                        - Bild wird in traningsordner verschoben
                        - Klassifizierung weitergegeben
                    """
                    product_data = get_product_with_data(result)
                    #TODO Bild in Trainingsordner für Kundenbilder kopieren
                    google_copy_file_to_folder(DriveFolders.UPLOAD.value,
                                               DriveFolders.TRAININGSSATZ.value,
                                               event_filename)

                    url = " http://nginx-proxy/eventing-service/publish/MisclassificationReported"
                    headers = {
                        "Cookie": f"{event_cookie}",
                    }
                    files = {
                        "type": (None, "MisclassifiedFiles"),
                        "classification": (None, result),
                        "filename": (None, event_filename),
                        "product_data": (None, product_data),
                        "role": (None, event_role)
                    }
                    response = requests.post(url, headers=headers, files=files)
                    logging.info(f"Response: {response}")
                else:
                    """
                        - prüfen ob Klassifizierung korrekt ist
                        - falls ja Klassifizierung weitergegeben
                        - falls nein Nachtraining
                    """
                    url = " http://nginx-proxy/eventing-service/publish/MisclassificationReported"
                    headers = {
                        "Cookie": f"{event_cookie}",
                    }
                    files = {
                        "type": (None, "MisclassifiedFiles"),
                        "classification": (None, result),
                        "filename": (None, event_filename),
                        "product_data": (None, None),
                        "role": (None, event_role)
                    }
                    response = requests.post(url, headers=headers, files=files)
                    logging.info(f"Response: {response}")

            if "CorrectedFiles" in event_type:
                event_classification = event.get("classification", "")
                event_class_correct = event.get("is_classification_correct ", "")
                event_filename = event.get("filename", "")
                logging.info(f"Event file: {event_classification}")
                logging.info(f"Event path: {event_class_correct}")
                logging.info(f"Event path: {event_filename}")
                if event_class_correct:

                    # (Sonja Schwabe) Für Yolo-Modell Bild und Label in den Trainingsordner legen
                    #TODO bei else noch was tun?
                    if not os.path.exists(f"{DriveFolders.DATASETS_TESTDATEN_IMAGES.value}/{file_without_path}"):
                        to_resize = Image.open(f"{DriveFolders.UPLOAD.value}/{file_without_path}")
                        resized = to_resize.resize((224, 224))
                        resized.save(f"{DriveFolders.DATASETS_TESTDATEN_IMAGES.value}/{file_without_path}")
                    else:
                        logging.info("FEHLER: Bilddatei mit diesem Namen bereits vorhanden")
                    pfad, label_name, endung = pfad_zerlegen(event_filename)
                    if not os.path.exists(f"{DriveFolders.DATASETS_TESTDATEN_LABELS.value}/{label_name}.txt"):
                        yolo_result.save_txt(f"{DriveFolders.DATASETS_TESTDATEN_LABELS.value}/{label_name}.txt")
                    else:
                        logging.info("FEHLER: Labeldatei mit diesem Namen bereits vorhanden")

                    #TODO Falls erkannte Klasse zu Ralfs Modell passt Bild für Nachtraining speichern
                    #google_copy_file_to_folder(DriveFolders.UPLOAD.value,
                    #                           DriveFolders.TRAININGSSATZ.value,
                    #                           event_filename)

                    url = " http://nginx-proxy/eventing-service/publish/ClassificationCompleted"
                    headers = {
                        "Cookie": f"{event_cookie}",
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

                    logging.info("Fehlerhafte Klassifizierung")
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
