import base64
import json

import requests
from PIL import Image
import io
import aio_pika
import asyncio
from common.utils import load_secrets
import logging
import qrcode

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
            logging.info(f"if: {event}")
            if "ProcessQrcode" == event_type:
                event_data = event.get("image_blob", "")
                logging.info(f"Event Data: {event_data}")
                logging.info("Processing files after ProcessQrcode event.")

                base64_decoded_qrcode = base64.b64decode(event_data)
                # Rückgabe des Blob QR-Codes aus Backend als Image an Frontend geben
                # Blob in ein Bild laden
                image_stream = io.BytesIO(base64_decoded_qrcode)
                image = Image.open(image_stream)

                # Bild anzeigen
                image.show()
            elif "MisclassifiedFiles" == event_type:
                event_classification = event.get("classification", "")
                logging.info(f"Event Data: {event_classification}")
                event_filename = event.get("filename", "")
                logging.info(f"Event Filename: {event_filename}")
                event_path = event.get("path", "")
                logging.info(f"Event Path: {event_path}")
                # TODO Load the Image into a Viwer and submit if the classification is corect
                logging.info("Processing files after MisclassifiedFiles event.")

                url = " http://nginx-proxy/eventing-service/publish/CorrectedClassification"
                headers = {
                    "Authorization": f"{token}"
                }
                files = {
                    "type": (None, "CorrectedFiles"),
                    "classification": (None, event_classification),
                    "is_classification_correct": (None, True),
                    "filename": event_filename,
                    "path": event_path
                }
                response = requests.post(url, headers=headers, files=files)
                logging.info(f"Response: {response}")
            else:
                logging.debug("if fehlgeschalgen")
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
            await queue_mis.bind(exchange, routing_key="MisclassifiedFiles")  # Beispiel: Lauschen auf "ProcessFiles"

            queue_qrcode = await channel.declare_queue("process_qrcode_queue", durable=True)
            await queue_qrcode.bind(exchange, routing_key="ProcessQrcode")

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
