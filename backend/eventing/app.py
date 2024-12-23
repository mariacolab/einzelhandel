import asyncio
from aio_pika import connect_robust, IncomingMessage
import json

RABBITMQ_URL = "amqp://rabbitmq:5672"
QUEUES = ["image_uploaded", "image_validated", "classification_completed", "qrcode_generated"]

async def process_event(queue_name: str, message: IncomingMessage):
    async with message.process():
        event_data = json.loads(message.body.decode())
        print(f"Received event from {queue_name}: {json.dumps(event_data, indent=2)}")

async def main():
    connection = await connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        for queue in QUEUES:
            queue_obj = await channel.declare_queue(queue, durable=True)
            await queue_obj.consume(lambda msg: process_event(queue, msg))

if __name__ == "__main__":
    asyncio.run(main())
