import base64
import json
import aio_pika
import asyncio
from cryptography.fernet import Fernet
import requests

from common.product_data import get_product_with_data

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

            event_corrected = event.replace("'", '"')
            logging.debug(f"Corrected event JSON: {event_corrected}")

            event = json.loads(event_corrected)
            logging.debug(f"Parsed event: {event}")

            event_type = event.get("type", "")
            event_cookie = event.get("cookie", "")

            logging.info(f"Event type: {event_type}")
            logging.info(f"Event cookie: {event_cookie}")


            if "ClassFiles" in event_type:
                logging.info("Processing files after ClassificationCompleted event.")
                event_result = event.get("result", "")
                logging.info(f"Event Data: {event_result}")
                # TODO aufruf von Methoden um weiteren Code auszuführen
                """Fälle:
                1. Datensatz ist nicht in der Datenbank vorhanden
                    dann werden die Daten verschlüsselt 
                2. Datensatz ist bereits in der Datenbank vorhanden
                    dann wird der Datensatz """

                # prüft ob der Datensatz in der Datenbank vorhanden ist
                url = f"http://nginx-proxy/database-management/products/{event_result}"
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

                # Fall 1 er ist nicht vorhanden
                if body == expected_json:

                    # json_data = load_json("class.json")
                    # logging.info(f"json_data: {json_data}")
                    # item = get_item_by_class_name(json_data, event_result)
                    # logging.info(f"item: {item}")
                    # data = {
                    #     "Produkt": item["class_name"],
                    #     "Informationen": item.get("info"),
                    #     "Regal": item.get("regal"),
                    #     "Preis_pro_stueck": item["preis"].get("pro_stueck"),
                    #     "Preis_pro_kg": item["preis"].get("pro_kg")
                    # }
                    # logging.info(f"item_data: {data}")
                    data = get_product_with_data(event_result)

                    data_to_encrypt = json.dumps(data)

                    # Datensatz wird verschlüsselt
                    cipher = Fernet(key)

                    # Daten zum Verschlüsseln
                    #data_to_encrypt = data.encode()

                    # Verschlüsseln der Daten
                    encrypted_data = cipher.encrypt(data_to_encrypt.encode())
                    logging.debug(f"Verschlüsselte Daten: {encrypted_data}")
                    qr_data = base64.b64encode(encrypted_data).decode("utf-8")
                    logging.debug(f"Verschlüsselte Daten: {qr_data}")
                    message_data = qr_data

                    # qr-code generieren
                    url = " http://nginx-proxy/database-management/qrcodes"
                    headers = {
                        'Content-Type': 'application/json',
                        "Cookie": f"{event_cookie}",
                    }
                    logging.info(f"Data: {headers}")
                    data = {
                        "data": f"{qr_data}",
                    }

                    logging.info(f"Data Post Product: {data}")
                    response = requests.post(url, headers=headers, json=data)
                    # Initialisiere den Fernet-Verschlüsselungsalgorithmus

                    qr_body = response.json()
                    logging.info(f"qr_body: {qr_body}")

                    url = " http://nginx-proxy/database-management/products"
                    headers = {
                        'Content-Type': 'application/json',
                        "Cookie": f"{event_cookie}",
                    }
                    logging.info(f"Data: {headers}")
                    # TODO Daten ersetzen mit Rückgabe der KI
                    data = {
                        "name": f"{event_result}",
                        "description": item.get("info"),
                        "shelf": item.get("regal"),
                        "price_piece": item["preis"].get("pro_stueck"),
                        "price_kg": item["preis"].get("pro_kg"),
                        "qr_code_id": qr_body.get("id")
                    }
                    logging.info(f"Data Post Product: {data}")
                    response = requests.post(url, headers=headers, json=data)
                    # Initialisiere den Fernet-Verschlüsselungsalgorithmus

                else:
                    # Fall 2 er ist vorhanden
                    body = response.json()
                    # id des QR-Codes aus dem Body gelesen
                    qr_code_id = body.get("qr_code_id")
                    # QR-Code wird aus der Datenbank geholt
                    url = f"http://nginx-proxy/database-management/qrcodes/{qr_code_id}"
                    headers = {
                        "Cookie": f"{event_cookie}",
                    }
                    logging.info(f"Header get Product: {headers}")

                    # POST-Anfrage senden
                    response = requests.get(url, headers=headers)
                    body = response.json()
                    message_data = body.get("data")
                    logging.info(f"body GET qrcodes: {body}")
                    logging.info(f"code from body GET Product: {message_data}")

                # Event QR-Code generated wird mit den entsprechenden Daten abgesetzt
                url = " http://nginx-proxy/eventing-service/publish/QRCodeGenerated"
                headers = {
                    "Cookie": f"{event_cookie}",
                }
                logging.info(f"Data: {headers}")
                # TODO change data with return values
                files = {
                    "type": (None, "ProcessQrcode"),
                    "image_blob": (None, message_data),
                }
                logging.info(f"Files QRCodeGenerated: {files}")

                # POST-Anfrage senden
                response = requests.post(url, headers=headers, files=files)
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
            queue_classified = await channel.declare_queue("process_classified_queue", durable=True)
            await queue_classified.bind(exchange, routing_key="ClassFiles")

            await queue_classified.consume(on_message)
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
