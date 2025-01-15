import json

import aio_pika
import asyncio
from common.utils import load_secrets
import logging

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

            logging.info(f"Event type: {event_type}")
            logging.info(f"Event filename: {event_data}")

            token = event.get("token", "")

            if not token:
                logging.warning("Token not found in event payload")
                return

            logging.info(f"Extracted token: {token}")

            if "ProcessQrcode" in event:
                logging.info("Processing files after QRCodeGenerated event.")
                # TODO aufruf von Methoden um weiteren Code auszuführen
                """prüfen ob QR Code oder verschlüsselte Daten gesendet werden
                im ersten Fall muss der QR-Code angezeigt werden
                im zweiten Fall muss aus den Daten ein QR-Code erzeugt werden
                und in die Datenbank geschrieben werden!"""

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
            queue = await channel.declare_queue("process_qrcode_queue", durable=True)
            await queue.bind(exchange, routing_key="ProcessQrcode")  # Beispiel: Lauschen auf "ProcessFiles"

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

