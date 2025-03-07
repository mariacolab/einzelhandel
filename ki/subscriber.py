"""
   von Maria Schuster
   Konsument der RabbitMQ Events die in der Ki verarbeitet werden
   ruft die Yolo und Tensorflow auf, die Erstellung des QR Codes,
   die Rückgabe der Produktdaten an den Kunden und ruft das Nachlernen der Ki's auf
"""
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
from common.shared_drive import copy_file_to_folder, del_file
from detectYOLO11 import detect, pfad_zerlegen, retrain
from common.utils import load_secrets
from rh_TF_Update import update_model_TF, move_Data_TF
from rh_TF_Predict import predict_object_TF

# Setup logging
logging.basicConfig(level=logging.INFO)

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
            event = json.loads(event_corrected)
            event_type = event.get("type", "")
            event_cookie = event.get("cookie", "")
            event_role = event.get("role", "")

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
                        - Klassifizierung weitergegeben an Kunden
                    """
#Abschnitt von Sonja Schwabe - Anfang
                    # Bilder für kleines Modell ungelabelt ablegen
                    if result2 is not None:
                        pfad, name, endung = pfad_zerlegen(event_filename)
                        img_small = image.resize((128, 128))
                        img_small.save(f"{SharedFolders.TRAININGSSATZ.value}/kleinesModell/{name}{endung}")
#Abschnitt von Sonja Schwabe - Ende

                    # prüft ob der Datensatz in der Datenbank vorhanden ist
                    url = f"http://nginx-proxy/database-management/products/{result}"
                    headers = {
                        'Content-Type': 'application/json',
                        "Cookie": f"{event_cookie}",
                    }
                    logging.info(f"Header get Product: {headers}")

                    # POST-Anfrage senden
                    response = requests.get(url, headers=headers)
                    body = response.json()
                    logging.info(f"Product response: {body}")
                    expected_json = {"error": "Product not found"}

                    if body == expected_json:
                        url = " http://nginx-proxy/eventing-service/publish/ClassificationReported"
                        headers = {
                            "Cookie": f"{event_cookie}",
                        }
                        files = {
                            "type": (None, "ClassifiedFiles"),
                            "classification": (None, result),
                            "filename": (None, event_filename),
                            "product": (None, "Das Produkt ist leider nicht im Supermarkt vorhanden."),
                            "info": (None, None),
                            "shelf": (None, None),
                            "price_piece": (None, None),
                            "price_kg": (None, None),
                            "role": (None, event_role),
                            "mixed_results": (None, mixed_results)
                        }

                        response = requests.post(url, headers=headers, files=files)
                        logging.info(f"Response: {response}")
                    else:
                        produkt = body.get("name")
                        info = body.get("description")
                        regal = body.get("shelf")
                        preis_pro_stueck = body.get("price_piece")
                        preis_pro_kg = body.get("price_kg")

                        url = " http://nginx-proxy/eventing-service/publish/ClassificationReported"
                        headers = {
                            "Cookie": f"{event_cookie}",
                        }
                        files = {
                            "type": (None, "ClassifiedFiles"),
                            "classification": (None, result),
                            "filename": (None, event_filename),
                             "product": (None, produkt),
                            "info": (None, info),
                            "shelf": (None, regal),
                            "price_piece": (None, str(preis_pro_stueck)),
                            "price_kg": (None, str(preis_pro_kg)),
                            "role": (None, event_role),
                            "mixed_results": (None, mixed_results)

                        }
                        response = requests.post(url, headers=headers, files=files)
                        logging.info(f"Response: {response}")
                else:

                    """
                        - prüfen ob Klassifizierung korrekt ist
                        - falls ja Klassifizierung weitergegeben
                        - falls nein labeln für das Nachtraining
                    """

                    # einlesen der Produktdaten aus einem JSON um sie als Rückgabewert mit zu senden
                    product_data = get_product_with_data(result) or {}

                    produkt = product_data['Produkt']
                    info = product_data['Informationen']
                    regal = product_data['Regal']
                    preis_pro_stueck = product_data['Preis_pro_stueck']
                    preis_pro_kg = product_data['Preis_pro_kg']

                    url = " http://nginx-proxy/eventing-service/publish/ClassificationReported"
                    headers = {
                        "Cookie": f"{event_cookie}",
                    }
                    files = {
                        "type": (None, "ClassifiedFiles"),
                        "classification": (None, result),
                        "filename": (None, event_filename),
                        "product": (None, produkt),
                        "info": (None, info),
                        "shelf": (None, regal),
                        "price_piece": (None, str(preis_pro_stueck)),
                        "price_kg": (None, str(preis_pro_kg)),
                        "role": (None, event_role),
                        "mixed_results": (None, mixed_results)
                    }
                    logging.info(f"files: {files}")
                    response = requests.post(url, headers=headers, files=files)
                    logging.info(f"Response: {response}")

                    """ url = " http://nginx-proxy/eventing-service/publish/ClassificationCompleted"
                    headers = {
                        "Cookie": f"{event_cookie}",
                    }
                    files = {
                        "type": (None, "ClassFiles"),
                        "result": (None, result),
                    }
                    response = requests.post(url, headers=headers, files=files)
                    logging.info(f"Response: {response}") """

            if "CorrectedFiles" in event_type:
                event_classification = event.get("classification", "")
                event_class_correct = event.get("is_classification_correct", "")
                event_filename = event.get("filename", "")
                mixed_results = event.get("mixed_results","")
                event_host = event.get("host", "")
                event_protocol = event.get("protocol", "")
                logging.info(f"Event event_classification: {event_classification}")
                logging.info(f"Event class_correct: {event_filename}")
                logging.info(f"Event class_correct: {event_class_correct}")
                logging.info(f"Event event_protocol: {event_protocol}")
                logging.info(f"Event event_host: {event_host}")

#Abschnitt von Sonja Schwabe - Anfang
                class_names = ['Apfel', 'Aubergine', 'Avocado', 'Birne',
                               'Granatapfel', 'Kaki', 'Kartoffel', 'Kiwi',
                               'Mandarine', 'Orange', 'Pampelmuse', 'Paprika',
                               'Tomate', 'Zitrone', 'Zucchini', 'Zwiebel']
                if(SharedFolders.UPLOAD.value in event_filename):
                    image = Image.open(event_filename)
                else:
                    image = Image.open(f"{SharedFolders.UPLOAD.value}/{event_filename}")  # Lädt das Bild als NumPy-Array

                pfad, name, endung = pfad_zerlegen(event_filename)
                if event_class_correct == "True" or event_class_correct == "true": #Bild wurde korrekt klassifiziert
                    logging.info("event_class_correct == true")
                    if event_classification in class_names: #passend für kleines Modell
                        logging.info("kleines Modell")
                        img_small = image.resize((128, 128))
                        logging.info("kleines Modell small")
                        img_small.save(f"{SharedFolders.DATA_OBST_GEMUESE_NEU_1_TRAIN.value}/{event_classification}/{name}{endung}")
                        logging.info("kleines Modellsmall saved")
                    if mixed_results == "False":
                        logging.info("Yolo Modell")
                        img_small = image.resize((224, 224))
                        img_small.save(f"{SharedFolders.DATASETS_FFv3_TRAIN_IMAGES.value}/{name}{endung}")
                        logging.info("Yolo resize saved")
                        if os.path.exists(f"{SharedFolders.TRAININGSSATZ.value}/{name}.txt"):
                            copy_file_to_folder(f"{SharedFolders.TRAININGSSATZ.value}/{name}.txt",
                                        SharedFolders.DATASETS_FFv3_TRAIN_LABELS.value,
                                        f"{name}.txt")
                            os.remove(f"{SharedFolders.TRAININGSSATZ.value}/{name}.txt")
                            if os.path.exists(f"{SharedFolders.TRAININGSSATZ.value}/{name}{endung}"):
                                os.remove(f"{SharedFolders.TRAININGSSATZ.value}/{name}{endung}")
#Abschnitt von Sonja Schwabe - Ende
                    logging.info("create qrcode")
                    url = " http://nginx-proxy/eventing-service/publish/ClassificationCompleted"
                    headers = {
                        "Cookie": f"{event_cookie}",
                    }
                    files = {
                        "type": (None, "ClassFiles"),
                        "result": (None, event_classification),
                        "protocol": (None, event_protocol),
                        "host": (None, event_host)
                    }
                    logging.info(f"files ClassificationCompleted: {files}")
                    response = requests.post(url, headers=headers, files=files)
                    logging.info(f"Response: {response}")

                    url = " http://nginx-proxy/eventing-service/publish/ClassificationCompleted"
                    headers = {
                        "Cookie": f"{event_cookie}",
                    }
                    files = {
                        "type": (None, "ClassFiles"),
                        "result": (None, event_classification),
                        "protocol": (None, event_protocol),
                        "host": (None, event_host)
                    }
                    logging.info(f"files ClassificationCompleted: {files}")
                    response = requests.post(url, headers=headers, files=files)
                    logging.info(f"Response: {response}")

                else:
                    logging.info(f"Event file: {event_classification}")

#Abschnitt von Sonja Schwabe - Anfang

                    if event_classification in class_names:
                        img_small = image.resize((128, 128))
                        img_small.save(f"{SharedFolders.TRAININGSSATZ.value}/kleinesModell/{name}{endung}")  # TODO richtiger Ordner für unlabeled Data

#Abschnitt von Sonja Schwabe - Ende
                    logging.info("Fehlerhafte Klassifizierung")
                    """ #Datei wird aus Sharefolders.Uploade gelöscht
                    if(SharedFolders.UPLOAD.value in event_filename):
                        del_file(event_filename)
                    else:
                        del_file(f"{SharedFolders.UPLOAD.value}/{event_filename}") """
            if "LabeledTrainingdata" in event_type:
                logging.info("LabeledTrainingdata")
# Abschnitt von Ralf Hager - Beginn
#    Ein Vorbereitungsschritt für das Nachlernen des Modells wird angestossen
#    Es wird dabei eine Liste von Files vom Front-End durchgereicht,
#    beim 'kleinen' Modell noch zusätzlich die Labels, damit die Dateien
#    in die richtigen Verzeichnisse verschoben werden können.
                event_filepath = f'../mnt/'
                event_ki = event.get("ki", "")
                event_labels = event.get("labels","")
                event_files = event.get("files","")
                if "yolo" in event_ki:
                    file_path = f'{event_filepath}/labeled_yolo'
                    # ToDo Aufruf Nachlernen YOLO
                if "tf" in event_ki:
                    file_path = f'../mnt/labeled_tf'
                    logging.info(f"LabeledTrainingdata tf: {file_path}, {event_labels}, {event_files}")
                    move_Data_TF(file_path,event_labels, event_files)
                    for file in event_files:
                        del_file(f'../mnt/labeled_tf/{file}')
# Abschnitt von Ralf Hager - Ende
            if "TrainYOLO" in event_type:
                retrain()
            if "TrainTF" in event_type:
                update_model_TF()

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
            await queue_tf.bind(exchange, routing_key="TrainTF")

            queue_label = await channel.declare_queue("process_labeleddata_queue", durable=True)
            await queue_label.bind(exchange, routing_key="LabeledTrainingdata")

            queue_yolo = await channel.declare_queue("process_yolo_queue", durable=True)
            await queue_yolo.bind(exchange, routing_key="TrainYolo")

            await queue_label.consume(on_message)
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
