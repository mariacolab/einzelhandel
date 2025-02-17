import os.path

import aio_pika
import asyncio
from common.SharedFolders import SharedFolders
import requests
import json
import logging
import matplotlib.pyplot as plt
from common.product_data import get_product_with_data
from common.shared_drive import copy_file_to_folder
from detectYOLO11 import detect
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
            event_cookie = event.get("cookie", "")
            event_role = event.get("role", "")

            logging.info(f"Event type: {event_type}")
            logging.info(f"Event cookie: {event_cookie}")
            logging.info(f"Event role: {event_role}")

            if "ValidatedFiles" in event_type:
                logging.info("Processing files after ImageUploaded event.")
                event_filename = event.get("file", "")
                logging.info(f"Event filename: {event_filename}")

                #aufruf der KI
                class_names = ['Apfel', 'Aubergine', 'Avocado', 'Birne',
                               'Granatapfel', 'Kaki', 'Kartoffel', 'Kiwi',
                               'Mandarine', 'Orange', 'Pampelmuse', 'Paprika',
                               'Tomate', 'Zitrone', 'Zucchini', 'Zwiebel']

                image = plt.imread(event_filename)  # Lädt das Bild als NumPy-Array

                result = detect(image, event_filename)
                if result in class_names:
                    result = predict_object_TF(image)

                logging.info(f"result from image: {result}")

                if event_role == "Kunde":
                    """
                        - Bild wird in traningsordner verschoben
                        - Klassifizierung weitergegeben
                    """
                    product_data = get_product_with_data(result)
                    #TODO Bild in Trainingsordner für Kundenbilder kopieren
                    copy_file_to_folder(SharedFolders.UPLOAD.value,
                                               SharedFolders.TRAININGSSATZ.value,
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
                    copy_file_to_folder(SharedFolders.UPLOAD.value,
                                               SharedFolders.TRAININGSSATZ.value,
                                               event_filename)
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
