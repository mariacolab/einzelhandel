from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import aio_pika
import json
import datetime

app = FastAPI()

# RabbitMQ-Konfiguration
RABBITMQ_URL = "amqp://broker.example.com"
EXCHANGE_NAME = ""
QUEUE_NAME = "image_validated"

@app.post("/validate-image")
async def validate_image(image_id: str, is_valid: bool):
    """
    Endpoint to handle image validation and publish ImageValidated event.
    """
    try:
        # Generiere einen Timestamp
        timestamp = datetime.datetime.utcnow().isoformat()

        # Nachricht zum Versenden vorbereiten
        message_payload = {
            "imageId": image_id,
            "isValid": is_valid,
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

        return JSONResponse(content={"status": "success", "message": "ImageValidated event published.", "data": message_payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
