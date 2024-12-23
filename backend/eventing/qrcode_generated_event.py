from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import aio_pika
import json
import datetime
import uuid

app = FastAPI()

# RabbitMQ-Konfiguration
RABBITMQ_URL = "amqp://broker.example.com"
QUEUE_NAME = "qrcode_generated"

@app.post("/generate-qrcode")
async def generate_qrcode(image_id: str, qr_code_data: str):
    """
    Endpoint to handle QR code generation and publish QRCodeGenerated event.
    """
    try:
        # Generiere eine eindeutige ID für den QR-Code
        qr_code_id = str(uuid.uuid4())

        # Generiere einen Timestamp
        timestamp = datetime.datetime.utcnow().isoformat()

        # Nachricht zum Versenden vorbereiten
        message_payload = {
            "qrCodeId": qr_code_id,
            "imageId": image_id,
            "qrCodeData": qr_code_data,
            "timestamp": timestamp
        }

        # Veröffentliche das Event in RabbitMQ
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message_payload).encode("utf-8"),
                    content_type="application/json",
                ),
                routing_key=QUEUE_NAME,
            )

        return JSONResponse(content={"status": "success", "message": "QRCodeGenerated event published.", "data": message_payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
