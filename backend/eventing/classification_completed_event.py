from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import aio_pika
import json
import datetime

app = FastAPI()

# RabbitMQ-Konfiguration
RABBITMQ_URL = "amqp://broker.example.com"
QUEUE_NAME = "classification_completed"

@app.post("/classification-completed")
async def classification_completed(image_id: str, classifications: list):
    """
    Endpoint to handle classification results and publish ClassificationCompleted event.
    """
    try:
        # Generiere einen Timestamp
        timestamp = datetime.datetime.utcnow().isoformat()

        # Nachricht zum Versenden vorbereiten
        message_payload = {
            "imageId": image_id,
            "classifications": classifications,
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

        return JSONResponse(content={"status": "success", "message": "ClassificationCompleted event published.", "data": message_payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
