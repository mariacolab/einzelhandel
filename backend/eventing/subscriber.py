import aio_pika
import asyncio
from common.utils import load_secrets

secrets = load_secrets()
password = secrets.get('RABBITMQ_PASSWORD')
RABBITMQ_URL = "amqp://guest:{}@rabbitmq:5672".format(password)
print(f"Loaded DATABASE_URI: {RABBITMQ_URL}")

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        print(f"Received message: {message.body.decode()}")

async def main():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("events", durable=True)
        await queue.consume(process_message)

if __name__ == "__main__":
    asyncio.run(main())
