import asyncio
from datetime import datetime

import aio_pika

from monitoring_adapter.elasticsearch import PersistenceException
from monitoring_adapter.models import Error, Heartbeat
from monitoring_adapter.monitor import Monitor
from monitoring_adapter import config
from monitoring_adapter.xml import DecodeException, decode_message


async def main(event_loop, monitor):
    connection = await aio_pika.connect_robust(config.AMQP_URI, loop=event_loop)
    channel = await connection.channel()
    queue = await channel.get_queue(config.QUEUE_NAME)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    try:
                        model = decode_message(message.body)

                        if not isinstance(model, Heartbeat):
                            await model.persist()
                        else:
                            status_change = monitor.process_heartbeat(model)

                            if status_change:
                                await status_change.persist()
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


async def periodic_monitor(monitor):
    while True:
        await asyncio.sleep(monitor.OFFLINE_TRESHOLD_IN_SECONDS)

        for status_change in monitor.evaluate_statuses():
            await status_change.persist()


if __name__ == '__main__':
    monitor = Monitor()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(main(loop, monitor), periodic_monitor(monitor)))
    loop.close()
