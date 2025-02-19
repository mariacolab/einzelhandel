import os.path

import aio_pika
import asyncio

import cv2

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

                # aufruf der KI
                class_names = ['Apfel', 'Aubergine', 'Avocado', 'Birne',
                               'Granatapfel', 'Kaki', 'Kartoffel', 'Kiwi',
                               'Mandarine', 'Orange', 'Pampelmuse', 'Paprika',
                               'Tomate', 'Zitrone', 'Zucchini', 'Zwiebel']

                image = plt.imread(event_filename)  # Lädt das Bild als NumPy-Array

                result1, yolo_result = detect(image, event_filename)  # großes Modell
                if result1 in class_names:
                    result2 = predict_object_TF(image)  # kleines Modell
                else:
                    result2 = None
                if not result2 or result1 == result2:
                    result = result1
                else:  # verschiedene Ergebnisse
                    mixed_results = True
                    result = result2
                logging.info(f"result from image: {result}")

                if event_role == "Kunde":
                    """
                        - Bild wird in traningsordner verschoben
                        - Klassifizierung weitergegeben
                    """
                    product_data = get_product_with_data(result) or {}
                    logging.info(f"result from product_data: {product_data}")
                    product_data = get_product_with_data(result) or {}
                    logging.info(f"result from product_data: {product_data}")
                    for key, value in product_data.items():
                        logging.info(f"{key}: {value}")
                    produkt = product_data['Produkt']
                    info = product_data['Informationen']
                    regal = product_data['Regal']
                    preis_pro_stueck = product_data['Preis_pro_stueck']
                    preis_pro_kg = product_data['Preis_pro_kg']

                    logging.info(f"Produkt: {produkt}")
                    logging.info(f"Informationen: {info}")
                    logging.info(f"Regal: {regal}")
                    logging.info(f"Preis pro Stück: {preis_pro_stueck} €")
                    logging.info(f"Preis pro kg: {preis_pro_kg} €")

                    # # TODO Bild in Trainingsordner für Kundenbilder kopieren
                    # img_small = cv2.resize(image, dsize=(224, 224), interpolation=cv2.INTER_CUBIC)
                    # copy_file_to_folder(img_small,
                    #                     SharedFolders.TRAININGSSATZ.value,
                    #                     event_filename)
                    # # TODO in unlabeled Data
                    # if result2 is not None:
                    #     img_small = cv2.resize(image, dsize=(128, 128), interpolation=cv2.INTER_CUBIC)
                    #     copy_file_to_folder(img_small,
                    #                         SharedFolders.TRAININGSSATZ.value,
                    #                         event_filename)
                    url = " http://nginx-proxy/eventing-service/publish/MisclassificationReported"
                    headers = {
                        "Cookie": f"{event_cookie}",
                    }
                    files = {
                        "type": (None, "MisclassifiedFiles"),
                        "classification": (None, result),
                        "filename": (None, event_filename),
                        "product": (None, produkt),
                        "info": (None, info),
                        "shelf": (None, regal),
                        "price_piece": (None, str(preis_pro_stueck)),
                        "price_kg": (None, str(preis_pro_kg)),
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
                        "product": (None, None),
                        "info": (None, None),
                        "shelf": (None, None),
                        "price_piece": (None, None),
                        "price_kg": (None, None),
                        "role": (None, event_role)
                    }
                    logging.info(f"files: {files}")
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
                    class_names = ['Apfel', 'Aubergine', 'Avocado', 'Birne',
                                   'Granatapfel', 'Kaki', 'Kartoffel', 'Kiwi',
                                   'Mandarine', 'Orange', 'Pampelmuse', 'Paprika',
                                   'Tomate', 'Zitrone', 'Zucchini', 'Zwiebel']
                    if event_classification in class_names:
                        img_small = cv2.resize(image, dsize=(128, 128), interpolation=cv2.INTER_CUBIC)
                        copy_file_to_folder(img_small,
                                            SharedFolders.TRAININGSSATZ.value,  # TODO Richtiger Ordner für Ralfs Bilder
                                            event_filename)
                    img_small = cv2.resize(image, dsize=(224, 224), interpolation=cv2.INTER_CUBIC)
                    copy_file_to_folder(img_small,
                                        SharedFolders.DATASETS_FFv3_TRAIN_IMAGES.value,
                                        event_filename)
                    # TODO: Label speichern und sonst löschen
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

                    img_small = cv2.resize(image, dsize=(224, 224), interpolation=cv2.INTER_CUBIC)
                    copy_file_to_folder(img_small,
                                        SharedFolders.TRAININGSSATZ.value,
                                        event_filename)
                    # TODO in unlabeled Data
                    if result2 is not None:
                        img_small = cv2.resize(image, dsize=(128, 128), interpolation=cv2.INTER_CUBIC)
                        copy_file_to_folder(img_small,
                                            SharedFolders.TRAININGSSATZ.value,
                                            event_filename)
            if "TrainYOLO" in event_type:
                event_classification = event.get("classification", "")
                event_class_correct = event.get("is_classification_correct ", "")
                event_filename = event.get("filename", "")
                logging.info(f"Event file: {event_classification}")
                logging.info(f"Event path: {event_class_correct}")
                logging.info(f"Event path: {event_filename}")
                logging.info("Fehlerhafte Klassifizierung")
            if "TrainTF" in event_type:
                event_classification = event.get("classification", "")
                event_class_correct = event.get("is_classification_correct ", "")
                event_filename = event.get("filename", "")
                logging.info(f"Event file: {event_classification}")
                logging.info(f"Event path: {event_class_correct}")
                logging.info(f"Event path: {event_filename}")
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

            queue_tf = await channel.declare_queue("process_tf_queue", durable=True)
            await queue_tf.bind(exchange, routing_key="tfFiles")

            queue_yolo = await channel.declare_queue("process_yolo_queue", durable=True)
            await queue_yolo.bind(exchange, routing_key="yoloFiles")

            await queue_corrected.consume(on_message)
            await queue_tf.consume(on_message)
            await queue_yolo.consume(on_message)
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
