import asyncio
from aio_pika import connect_robust, IncomingMessage
import json

RABBITMQ_URL = "amqp://broker.example.com"

async def process_image(message: IncomingMessage):
    async with message.process():
        event_data = json.loads(message.body.decode())
        metadata = event_data["metadata"]
        image = event_data["image"]  # Binary encoded
        print(f"Processing image {metadata['imageId']} uploaded at {metadata['timestamp']}")

async def process_validated_image(message: IncomingMessage):
    async with message.process():
        event_data = json.loads(message.body.decode())
        image_id = event_data["imageId"]
        is_valid = event_data["isValid"]
        timestamp = event_data["timestamp"]
        print(f"Image {image_id} validation status: {'Valid' if is_valid else 'Invalid'} at {timestamp}")


async def main(queue_name: str):
    connection = await connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, durable=True)

        await queue.consume(process_image)

if __name__ == "__main__":
    asyncio.run(main())
