import json
import asyncio
import aio_pika
import logging
from flask import Flask, request
from flask_socketio import SocketIO

# Logging einrichten
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# RabbitMQ Verbindung
RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672"

async def rabbitmq_listener():
    """ Lauscht auf RabbitMQ und sendet Nachrichten per WebSocket an Angular """
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()

        # Queue abonnieren
        queue = await channel.declare_queue("angular_queue", durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    event = message.body.decode()
                    logging.info(f"Received event: {event}")
                    socketio.emit("new_message", json.loads(event))  # Sendet Nachricht an Angular
    except Exception as e:
        logging.error(f"RabbitMQ error: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    """ Empfängt Webhook-Events von externen Services und leitet sie an Angular weiter """
    try:
        data = request.json
        logging.info(f"Webhook received: {data}")
        socketio.emit("new_message", data)  # Sendet Nachricht an Angular
        return {"message": "Webhook received"}, 200
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return {"error": str(e)}, 500

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(rabbitmq_listener())  # RabbitMQ Listener starten
    socketio.run(app, host="0.0.0.0", port=5008)
