import json
import os
import tempfile

import aio_pika
import asyncio

import requests
from flask import session

from common.DriveFolders import DriveFolders
from common.google_drive import google_uploade_file_to_folder, google_download_file
from common.utils import load_secrets
import logging
from process_uploads import process_files
import redis

# Lade das Redis-Passwort aus der Umgebung
redis_password = os.getenv("REDIS_PASSWORD", None)

redis_client = redis.StrictRedis(
    host='redis',
    port=6379,
    db=0,
    decode_responses=True,
    password=redis_password  # Passwort setzen
)
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


async def on_message(message: aio_pika.IncomingMessage, ):
    async with message.process():
        try:
            event = message.body.decode()
            logging.debug(f"Received event: {event}")

            event_corrected = event.replace("'", '"')
            logging.debug(f"Corrected event JSON: {event_corrected}")

            event = json.loads(event_corrected)
            logging.debug(f"Parsed event: {event}")

            event_type = event.get("type", "")
            event_filename = event.get("filename", "")
            event_fileid = event.get("fileid", "")
            event_model = event.get("model", "")
            event_cookie = event.get("cookie", "")
            logging.info(f"Event type: {event_type}")
            logging.info(f"Event filename: {event_filename}")
            logging.info(f"Event file_id: {event_fileid}")
            logging.info(f"Event model: {event_model}")
            logging.info(f"Event cookie: {event_cookie}")

            if "ProcessFiles" in event_type:
                logging.info("Processing files after ImageUploaded event.")
                process_files(event_filename, event_fileid)

                # Download file from Google Drive
                with tempfile.TemporaryDirectory() as temp_dir:
                    local_file_path = google_download_file(event_fileid, temp_dir)

                    url = " http://nginx-proxy/eventing-service/publish/ImageValidated"

                    headers = {
                        "Cookie": f"{event_cookie}",
                    }

                    logging.debug(f"Request Headers: {headers}")

                    with open(local_file_path, "rb") as file:
                        files = {
                            "type": (None, "ValidatedFiles"),
                            "model": (None, event_model),
                            "fileid": (None, event_fileid),
                            "file": (file.name, file, "application/octet-stream"),
                        }
                        logging.debug(f"Request Headers: {headers}")
                        response = requests.post(url, headers=headers, files=files)
                        logging.info(f"Response: {response}")

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
            queue = await channel.declare_queue("process_files_queue", durable=True)
            await queue.bind(exchange, routing_key="ProcessFiles")  # Beispiel: Lauschen auf "ProcessFiles"

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
