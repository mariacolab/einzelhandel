from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import aio_pika
import json
import datetime
import uuid

app = FastAPI()

# RabbitMQ-Konfiguration
RABBITMQ_URL = "amqp://broker.example.com"
QUEUE_NAME = "image_uploaded"

@app.post("/upload-image")
async def upload_image(image: UploadFile, timestamp: str = Form(...)):
    """
    Endpoint to handle image upload and publish ImageUploaded event.
    """
    try:
        # Generiere eine eindeutige ID für das Bild
        image_id = str(uuid.uuid4())

        # Lade das Bild im Speicher
        image_data = await image.read()

        # Bereite die Metadaten vor
        metadata = {
            "imageId": image_id,
            "timestamp": timestamp or datetime.datetime.utcnow().isoformat(),
        }

        # Nachricht zum Versenden vorbereiten
        message_payload = {
            "metadata": metadata,
            "image": image_data.decode("latin1")  # Kodierung zum Senden im Textformat
        }

        # Veröffentliche das Event in RabbitMQ
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message_payload).encode("utf-8"),
                    content_type="multipart/form-data",
                ),
                routing_key=QUEUE_NAME,
            )

        return JSONResponse(content={"status": "success", "imageId": image_id})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
