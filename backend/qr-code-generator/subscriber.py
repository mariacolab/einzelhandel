import json
import aio_pika
import asyncio
from cryptography.fernet import Fernet
import requests

from common.utils import load_secrets
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Load secrets
try:
    secrets = load_secrets()
    password = secrets.get('RABBITMQ_PASSWORD')
    key = secrets.get('ENCRYPTION_KEY')
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

            if "ClassFiles" in event_type:
                logging.info("Processing files after ClassificationCompleted event.")
                # TODO aufruf von Methoden um weiteren Code auszuführen
                """Fälle:
                1. Datensatz ist nicht in der Datenbank vorhanden
                    dann werden die Daten verschlüsselt 
                2. Datensatz ist bereits in der Datenbank vorhanden
                    dann wird der Datensatz
                    

                url = f"http://nginx-proxy/database-management/products/{event_data}"
                headers = {
                    'Content-Type': 'application/json',
                    "Authorization": f"{token}"
                }
                logging.info(f"Data: {headers}")

                # POST-Anfrage senden
                response = requests.get(url, headers=headers)

                if not response.json():
                    url = " http://nginx-proxy/database-management/"
                    headers = {
                        'Content-Type': 'application/json',
                        "Authorization": f"{token}"
                    }
                    logging.info(f"Data: {headers}")
                    #TODO Daten ersetzen mit Rückgabe der KI
                    data = {
                        "name": "Apfel",
                        "description": "rot",
                        "price": "0,99"
                    }
                    logging.info(f"Data: {data}")
                    response = requests.post(url, headers=headers, json=data)
                    # Initialisiere den Fernet-Verschlüsselungsalgorithmus
                    cipher = Fernet(key)

                    # Daten zum Verschlüsseln
                    data_to_encrypt = response.json().encode()

                    # Verschlüsseln der Daten
                    data = cipher.encrypt(data_to_encrypt)
                    logging.debug("Verschlüsselte Daten:", data)
                else:
                    body = response.json()
                    qr_code_id = body.get("qr_code_id")
                    url = f"http://nginx-proxy/database-management/products/{qr_code_id}"
                    headers = {
                        'Content-Type': 'application/json',
                        "Authorization": f"{token}"
                    }
                    logging.info(f"Header: {headers}")
    
                    # POST-Anfrage senden
                    response = requests.get(url, headers=headers)
                    body = response.json()
                    data = body.get("code")"""

                url = " http://nginx-proxy/eventing-service/publish/QRCodeGenerated"
                headers = {
                    'Content-Type': 'application/json',
                    "Authorization": f"{token}"
                }
                logging.info(f"Data: {headers}")
                #TODO change data with return values
                data = {
                    "type": "ProcessQrcode",
                    "data": {
                        "code": "cat"
                    }
                }
                logging.info(f"Data: {data}")

                # POST-Anfrage senden
                response = requests.post(url, headers=headers, json=data)
                logging.info(f"Response: {response.request}")
                logging.info(f"Response: {response.status_code}")

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
            queue = await channel.declare_queue("process_classified_queue", durable=True)
            await queue.bind(exchange, routing_key="ClassFiles")

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

