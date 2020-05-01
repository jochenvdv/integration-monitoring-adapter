import asyncio
from datetime import datetime

import aio_pika

from elasticsearch import PersistenceException
from models import Error
from monitoring_adapter import (
    config,
    xml,
)
from xml import DecodeException


async def main(event_loop):
    connection = await aio_pika.connect_robust(config.AMQP_URI, loop=event_loop)
    channel = await connection.channel()
    queue = await channel.get_queue(config.QUEUE_NAME)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    try:
                        model = xml.decode_message(message.body)

                        if model:
                            await model.persist()
                    except DecodeException:
                        error = Error(
                            f'Failed to decoded message \'{message}\'',
                            datetime.now().isoformat(),
                            'monitoring',
                        )

                        await error.persist()
                    except PersistenceException:
                        # not much we can do if writing error to ElasticSearch fails
                        # swallow exception, and let message be acknowledged
                        pass
                    except Exception as e:
                        error = Error(
                            f'Unexpected error \'{e.message}\'',
                            datetime.now().isoformat(),
                            'monitoring',
                        )

                        await error.persist()
                except PersistenceException:
                    # not much we can do if writing error to ElasticSearch fails
                    # swallow exception, and let message be acknowledged
                    pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
