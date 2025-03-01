import base64
import json
import os
import requests
from PIL import Image
import io
import aio_pika
import asyncio
from common.SharedFolders import SharedFolders
from common.utils import load_secrets
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
WEBHOOK_URL = "http://webhook-service:5008/webhook"
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
            logging.info(f"Event type: {event_type}")
            logging.info(f"Event type: {event_cookie}")

            logging.info(f"if: {event}")
            if "ProcessQrcode" == event_type:
                event_data = event.get("image_blob", "")
                logging.info(f"Event Data: {event_data}")
                logging.info("Processing files after ProcessQrcode event.")

                response = requests.post(WEBHOOK_URL, json={"type": "QRCodeGenerated", "image": event_data})
                logging.info(f"Webhook response: {response.status_code}, {response.text}")
            elif "ClassifiedFiles" == event_type:
                mixed_results = event.get("mixed_results","")
                event_classification = event.get("classification", "")
                logging.info(f"Event Data: {event_classification}")
                event_filename = event.get("filename", "")
                logging.info(f"Event Filename: {event_filename}")
                event_role = event.get("role", "")
                logging.info(f"Event Role: {event_role}")
                event_product = event.get("product", "")
                logging.info(f"Event Product: {event_product}")
                event_product_info = event.get("info", "")
                logging.info(f"Event Product: {event_product_info}")
                event_product_shelf = event.get("shelf", "")
                logging.info(f"Event Product: {event_product_shelf}")
                event_price_piece = event.get("price_piece", "")
                logging.info(f"Event Product: {event_price_piece}")
                event_price_kg = event.get("price_kg", "")
                logging.info(f"Event Product: {event_price_kg}")
                event_mixed_results = event.get("mixed_results", "")
                logging.info(f"Event mixed_results: {mixed_results}")
                # TODO Load the Image into a Viewer and submit if the classification is correct
                logging.info("Processing files after ClassifiedFiles event.")

                try:
                    with open(event_filename, "rb") as file:
                        file_data = file.read()
                        base64_encoded = base64.b64encode(file_data).decode("utf-8")
                    logging.info("Datei erfolgreich in Base64 umgewandelt")
                except Exception as e:
                    logging.error(f"Error processing file: {e}")
                    logging.info(f"Fehler: Datei konnte nicht verarbeitet werden. {str(e)}")

                filename = os.path.basename(event_filename)
                logging.info(f"filename: {filename}")

                response = requests.post(WEBHOOK_URL, json={"type": "ClassifiedFiles",
                                                            "classification": event_classification,
                                                            "filename": filename,
                                                            "role": event_role,
                                                            "product": event_product,
                                                            "info": event_product_info,
                                                            "shelf": event_product_shelf,
                                                            "price_piece": event_price_piece,
                                                            "price_kg": event_price_kg,
                                                            "file": base64_encoded,
                                                            "mixed_results": mixed_results})
                logging.info(f"Webhook response: {response.status_code}, {response.text}")

                url = " http://nginx-proxy/eventing-service/publish/CorrectedClassification"
                headers = {
                    "Cookie": f"{event_cookie}",
                }
                files = {
                    "type": (None, "CorrectedFiles"),
                    "classification": (None, event_classification),
                    "is_classification_correct": (None, True),
                    "filename": (None,event_filename),
                    "mixed_results": (None, mixed_results)
                }
                response = requests.post(url, headers=headers, files=files)
                logging.info(f"Response: {response}")
            elif "Trainingdata" == event_type:
                event_files = event.get("files", "")
                #logging.info(f"Event Data: {event_data}")
                logging.info("Processing files after Trainingdata event.")
                event_ki = event.get("ki", "")
                base64_encoded = []
                filenames = []

                for file in event_files:
                    try:
                        with open(file, "rb") as file:
                            filenames.append(os.path.basename(f.name))
                            file_data = file.read()
                            base64_encoded.append(base64.b64encode(file_data).decode("utf-8"))
                        logging.info("Datei erfolgreich in Base64 umgewandelt")
                    except Exception as e:
                        logging.error(f"Error processing file: {e}")
                        logging.info(f"Fehler: Datei konnte nicht verarbeitet werden. {str(e)}")
                response = requests.post(WEBHOOK_URL, json={"type": "Trainingdata",
                                                            "ki": event_ki,
                                                            "files": base64_encoded,
                                                            "filenames": filename})
                logging.info(f"Webhook response: {response.status_code}, {response.text}")
            elif "sendQrCodeResult" == event_type:
                logging.info("Processing files after sendQrCodeResult event.")
                event_name = event.get("name", "")
                event_description = event.get("description", "")
                event_shelf = event.get("shelf", "")
                event_price_piece = event.get("price_piece", "")
                event_price_kg = event.get("price_kg", "")
                logging.info(f"Event Name: {event_name}")
                logging.info(f"Event Description: {event_description}")
                logging.info(f"Event Shelf: {event_shelf}")
                logging.info(f"Event Price_piece: {event_price_piece}")
                logging.info(f"Event Price_kg: {event_price_kg}")

                response = requests.post(WEBHOOK_URL, json={"type": "sendQrCodeResult",
                                                            "product": event_name,
                                                            "info": event_description,
                                                            "shelf": event_shelf,
                                                            "price_piece": event_price_piece,
                                                            "price_kg": event_price_kg})
                logging.info(f"Webhook response: {response.status_code}, {response.text}")
            else:
                logging.debug("if fehlgeschlagen")
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
            queue_mis = await channel.declare_queue("process_misclassified_queue", durable=True)
            await queue_mis.bind(exchange, routing_key="ClassifiedFiles")  # Beispiel: Lauschen auf "ProcessFiles"

            queue_qrcode = await channel.declare_queue("process_qrcode_queue", durable=True)
            await queue_qrcode.bind(exchange, routing_key="ProcessQrcode")

            queue_trainingdata = await channel.declare_queue("process_trainingdata_queue", durable=True)
            await queue_trainingdata.bind(exchange, routing_key="Trainingdata")

            queue_sendresult = await channel.declare_queue("process_sendresult_queue", durable=True)
            await queue_sendresult.bind(exchange, routing_key="sendQrCodeResult")

            await queue_sendresult.consume(on_message)
            await queue_trainingdata.consume(on_message)
            await queue_mis.consume(on_message)
            await queue_qrcode.consume(on_message)
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
