import aio_pika

from common.utils import load_secrets

secrets = load_secrets()
password = secrets.get('RABBITMQ_PASSWORD')
RABBITMQ_URL = "amqp://guest:{}@rabbitmq:5672".format(password)
print(f"Loaded DATABASE_URI: {RABBITMQ_URL}")

async def send_message(message):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        #exchange = await channel.declare_exchange("events", aio_pika.ExchangeType.TOPIC)
        exchange = await channel.declare_exchange("events", aio_pika.ExchangeType.TOPIC, durable=True)
        routing_key = message["type"]
        await exchange.publish(
            aio_pika.Message(body=str(message).encode()),
            routing_key=routing_key,
        )
