import asyncio
import aio_pika


from monitoring_adapter import (
    config,
    xml,
    # common
)


async def main(event_loop):
    connection = await aio_pika.connect_robust(config.AMQP_URI, loop=event_loop)
    channel = await connection.channel()
    queue = await channel.declare_queue(config.QUEUE_NAME, internal=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                model = xml.decode_message(message.body)

                if model:
                    await model.persist


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
