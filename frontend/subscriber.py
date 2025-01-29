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

            event_raw = message.body.decode()
            logging.debug(f"Raw event received: {event_raw}")

            event_corrected = event_raw.replace("'", '"')
            logging.debug(f"Corrected event JSON: {event_corrected}")

            event = json.loads(event_corrected)
            logging.debug(f"Parsed event: {event}")

            event_type = event.get("type", "")
            event_data = event.get("data", "")
            kind = event.get("kind", "")
            logging.info(f"Event type: {event_type}")
            logging.info(f"Event Data: {event_data}")
            logging.info(f"Event kind: {kind}")

            token = event.get("token", "")

            if not token:
                logging.warning("Token not found in event payload")
                return

            logging.info(f"Extracted token: {token}")
            logging.info(f"if: {event}")
            if "EncodedFiles" == event_type:
                logging.info("Processing files after EncodedFiles event.")

                """prüfen ob QR Code oder verschlüsselte Daten gesendet werden
                im ersten Fall muss der QR-Code angezeigt werden
                im zweiten Fall muss aus den Daten ein QR-Code erzeugt werden
                und in die Datenbank geschrieben werden! """

                base64_decoded_qrcode = base64.b64decode(event_data)

                logging.info("message bytes")
                # Rückgabe des Blob QR-Codes aus Backend als Image an Frontend geben
                # Blob in ein Bild laden
                image_stream = io.BytesIO(base64_decoded_qrcode)
                image = Image.open(image_stream)

                # Bild anzeigen
                image.show()
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
            queue = await channel.declare_queue("process_encoded_queue", durable=True)
            await queue.bind(exchange, routing_key="EncodedFiles")  # Beispiel: Lauschen auf "ProcessFiles"

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
