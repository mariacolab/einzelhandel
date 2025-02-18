import os.path

import aio_pika
import asyncio

import cv2
from PIL import Image

from common.SharedFolders import SharedFolders
import requests
import json
import logging
from common.product_data import get_product_with_data
from common.shared_drive import copy_file_to_folder
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

                image = Image.open(event_filename)  # Lädt das Bild als NumPy-Array

                result1 = detect(image, event_filename) #großes Modell
                result2=None
                if result1 in class_names:
                    result2 = predict_object_TF(image)  # kleines Modell

                if result2: # kleines Modell kam zum Einsatz
                    result = result2
                    if result1 == result2: #gleiches Resultat
                        mixed_results = "False"
                    else: #verschiedene Resultate
                        mixed_results="True"
                else:
                    mixed_results="False"
                    result = result1
                logging.info(f"result from image: {result}")

                if event_role == "Kunde":
                    """
                        - Bild wird in traningsordner verschoben
                        - Klassifizierung weitergegeben
                    """
                    product_data = get_product_with_data(result)

#Abschnitt von Sonja Schwabe - Anfang

                    # Bilder für kleines Modell ungelabelt ablegen
                    if result2 is not None:
                        pfad, name, endung = pfad_zerlegen(event_filename)
                        img_small = image.resize((128, 128))
                        img_small.save(f"{SharedFolders.TRAININGSSATZ.value}/kleinesModell/{name}{endung}")

#Abschnitt von Sonja Schwabe - Ende

                    url = " http://nginx-proxy/eventing-service/publish/MisclassificationReported"
                    headers = {
                        "Cookie": f"{event_cookie}",
                    }
                    files = {
                        "type": (None, "MisclassifiedFiles"),
                        "classification": (None, result),
                        "filename": (None, event_filename),
                        "product_data": (None, product_data),
                        "role": (None, event_role),
                        "mixed_results": (None, mixed_results)
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
                        "role": (None, event_role),
                        "mixed_results": (None,mixed_results)
                    }
                    response = requests.post(url, headers=headers, files=files)
                    logging.info(f"Response: {response}")

            if "CorrectedFiles" in event_type:
                event_classification = event.get("classification", "")
                event_class_correct = event.get("is_classification_correct ", "")
                event_filename = event.get("filename", "")
                mixed_results = event.get("mixed_results","")
                logging.info(f"Event file: {event_classification}")
                logging.info(f"Event path: {event_class_correct}")
                logging.info(f"Event path: {event_filename}")
#Abschnitt von Sonja Schwabe - Anfang

                class_names = ['Apfel', 'Aubergine', 'Avocado', 'Birne',
                               'Granatapfel', 'Kaki', 'Kartoffel', 'Kiwi',
                               'Mandarine', 'Orange', 'Pampelmuse', 'Paprika',
                               'Tomate', 'Zitrone', 'Zucchini', 'Zwiebel']
                image = Image.open(event_filename)  # Lädt das Bild als NumPy-Array

                pfad, name, endung = pfad_zerlegen(event_filename)
                if event_class_correct: #Bild wurde korrekt klassifiziert
                    if event_classification in class_names: #passend für kleines Modell
                        img_small = image.resize((128, 128))
                        img_small.save(f"{SharedFolders.DATA_OBST_GEMUESE_NEU_1_TRAIN.value}/{event_classification}")
                    if mixed_results == "False":
                        img_small = image.resize((224, 224))
                        img_small.save(f"{SharedFolders.DATASETS_FFv3_TRAIN_IMAGES.value}/{name}{endung}")
                        if os.path.exists(f"{SharedFolders.TRAININGSSATZ.value}/{name}.txt"):
                            copy_file_to_folder(f"{SharedFolders.TRAININGSSATZ.value}/{name}.txt",
                                        SharedFolders.DATASETS_FFv3_TRAIN_LABELS.value,
                                        f"{name}.txt")
                            os.remove(f"{SharedFolders.TRAININGSSATZ.value}/{name}.txt")
                            if os.path.exists(f"{SharedFolders.TRAININGSSATZ.value}/{name}{endung}"):
                                os.remove(f"{SharedFolders.TRAININGSSATZ.value}/{name}{endung}")
#Abschnitt von Sonja Schwabe - Ende
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
#Abschnitt von Sonja Schwabe - Anfang
                    #img_small = cv2.resize(image, dsize=(224, 224), interpolation=cv2.INTER_CUBIC)
                    #copy_file_to_folder(img_small,
                    #                    SharedFolders.TRAININGSSATZ.value,
                    #                    event_filename)

                    if event_classification in class_names:
                        img_small = image.resize((128, 128))
                        img_small.save(f"{SharedFolders.TRAININGSSATZ.value}/kleinesModell/{name}{endung}")  # TODO richtiger Ordner für unlabeled Data
                        #img_small = cv2.resize(image, dsize=(128, 128), interpolation=cv2.INTER_CUBIC)
                        #copy_file_to_folder(img_small,
                        #                    SharedFolders.TRAININGSSATZ.value,
                        #                    event_filename)
#Abschnitt von Sonja Schwabe - Ende
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
