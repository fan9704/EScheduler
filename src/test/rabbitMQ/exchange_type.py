import asyncio
import aio_pika

async def consume(exchange_name, exchange_type_str: str, queue_name, routing_key=""):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    exchange_type = getattr(aio_pika.ExchangeType, exchange_type_str.upper(), aio_pika.ExchangeType.DIRECT)
    exchange = await channel.declare_exchange(
        exchange_name,
        exchange_type,
        durable=True
    )

    queue = await channel.declare_queue(queue_name, durable=True)
    await queue.bind(exchange, routing_key=routing_key)

    print(f"Listening on queue '{queue_name}' bound to exchange '{exchange_name}'")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print(f"Received from {queue_name}: {message.body.decode()}")

if __name__ == "__main__":
    asyncio.run(consume("my_direct_exchange", "direct", "direct_queue", "task"))
    # asyncio.run(consume("my_fanout_exchange", "fanout", "fanout_queue"))
    # asyncio.run(consume("my_topic_exchange", "topic", "topic_queue", "order.created"))
