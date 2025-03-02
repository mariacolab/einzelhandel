"""
   von Maria Schuster
   erstellt einen QR-Code oder sendet einen bereits erstellten
"""
import json
import aio_pika
import asyncio
from cryptography.fernet import Fernet
import requests
import qrcode
import base64
from io import BytesIO
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
                event_protocol = event.get("protocol","")
                event_host = event.get("host","")
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

                    data = get_product_with_data(event_result) or {}

                    produkt = data['Produkt']
                    info = data['Informationen']
                    regal = data['Regal']
                    preis_pro_stueck = data['Preis_pro_stueck']
                    preis_pro_kg = data['Preis_pro_kg']

                    logging.info(f"Produkt: {produkt}")
                    logging.info(f"Informationen: {info}")
                    logging.info(f"Regal: {regal}")
                    logging.info(f"Preis pro Stück: {preis_pro_stueck} €")
                    logging.info(f"Preis pro kg: {preis_pro_kg} €")
                    regal = int(regal) if regal else 0
                    preis_pro_stueck = float(preis_pro_stueck) if preis_pro_stueck else 0.00
                    preis_pro_kg = float(preis_pro_kg) if preis_pro_kg else 0.00

                    url = "http://nginx-proxy/database-management/products/no-qr"
                    headers = {
                        'Content-Type': 'application/json',
                        "Cookie": f"{event_cookie}",
                    }
                    logging.info(f"Data: {headers}")
                    # TODO Daten ersetzen mit Rückgabe der KI
                    data = {
                        "name": produkt,
                        "description": info,
                        "shelf": regal,
                        "price_piece": preis_pro_stueck,
                        "price_kg": preis_pro_kg
                    }
                    logging.info(f"Data Post Product: {data}")
                    response = requests.post(url, headers=headers, json=data)
                    logging.info(f"Data Post Product: {response}")
                    # Initialisiere den Fernet-Verschlüsselungsalgorithmus
                    produkt_body = response.json()
                    logging.info(f"produkt_body: {produkt_body}")
                    id = produkt_body.get("id")
                    data_to_encrypt = json.dumps(id)

                    # Datensatz wird verschlüsselt
                    cipher = Fernet(key)

                    # Verschlüsseln der Daten
                    encrypted_data = cipher.encrypt(data_to_encrypt.encode())
                    logging.debug(f"Verschlüsselte Daten: {encrypted_data}")
                    qrcode_url = f"{event_protocol}://{event_host}/qrcode/scan/result?type=ReadQrCode&qrdata={encrypted_data}"
                    logging.info(f"QR-Code URl: {qrcode_url}")
                    # QR-Code Bild generieren (PIL Image)
                    img = qrcode.make(qrcode_url)
                    # Bild in einen BytesIO-Stream speichern
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG")
                    buffer.seek(0)
                    # Bildinhalt als Base64 kodieren
                    img_bytes = buffer.getvalue()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    logging.debug(f"img_base64: {img_base64}")
                    url = " http://nginx-proxy/database-management/qrcodes"
                    headers = {
                        'Content-Type': 'application/json',
                        "Cookie": f"{event_cookie}",
                    }
                    logging.info(f"Data: {headers}")
                    data = {
                        "data": f"{img_base64}",
                    }

                    logging.info(f"Data Post Product: {data}")
                    response = requests.post(url, headers=headers, json=data)

                    qr_body = response.json()
                    logging.info(f"qr_body: {qr_body}")
                    logging.info(f"qr_code_id: {qr_body.get('id')}")
                    url = f"http://nginx-proxy/database-management/products/{id}"
                    headers = {
                        'Content-Type': 'application/json',
                        "Cookie": f"{event_cookie}",
                    }
                    logging.info(f"Data: {headers}")
                    # TODO Daten ersetzen mit Rückgabe der KI
                    data = {
                        "name": produkt,
                        "description": info,
                        "shelf": regal,
                        "price_piece": preis_pro_stueck,
                        "price_kg": preis_pro_kg,
                        "qr_code_id": qr_body.get("id")
                    }
                    logging.info(f"Data Post Product: {data}")
                    response = requests.put(url, headers=headers, json=data)
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

            elif "ReadQrCode" in event_type:
                logging.info("Processing files after ReadQrCode event.")
                event_result = event.get("qrdata", "")
                logging.info(f"Event Data: {event_result}")

                # Datensatz wird verschlüsselt
                cipher = Fernet(key)
                #encrypted_data = base64.b64decode(event_result)
                decrypted_data = cipher.decrypt(event_result).decode()

                url = f"http://nginx-proxy/database-management/products/{decrypted_data}"
                headers = {
                    'Content-Type': 'application/json',
                }
                logging.info(f"Data: {headers}")

                response = requests.get(url, headers=headers)

                product_body = response.json()
                logging.info(f"qr_body: {product_body}")

                produkt = product_body.get("name")
                info = product_body.get("description")
                regal = product_body.get("shelf")
                preis_pro_stueck = product_body.get("price_piece")
                preis_pro_kg = product_body.get("price_kg")

                logging.info(f"Response produkt: {produkt}")
                logging.info(f"Response info: {info}")
                logging.info(f"Response regal: {regal}")
                logging.info(f"Response preis_pro_stueck: {preis_pro_stueck}")
                logging.info(f"Response preis_pro_kg: {preis_pro_kg}")

                url = " http://nginx-proxy/eventing-service/qrcode/send/result"

                files = {
                    "type": (None, "sendQrCodeResult"),
                    "name": (None, produkt),
                    "description": (None, info),
                    "shelf": (None, regal),
                    "price_piece": (None, str(preis_pro_stueck)),
                    "price_kg": (None, str(preis_pro_kg)),
                }
                logging.info(f"Response: {files}")
                response = requests.post(url, files=files)
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
            queue_classified = await channel.declare_queue("process_classified_queue", durable=True)
            await queue_classified.bind(exchange, routing_key="ClassFiles")

            queue_readqr = await channel.declare_queue("process_readqr_queue", durable=True)
            await queue_readqr.bind(exchange, routing_key="ReadQrCode")

            await queue_classified.consume(on_message)
            await queue_readqr.consume(on_message)
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
