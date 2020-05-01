import asyncio
import logging
from datetime import datetime

import aio_pika

from monitoring_adapter.elasticsearch import PersistenceException
from monitoring_adapter.models import Error, Heartbeat
from monitoring_adapter.monitor import Monitor
from monitoring_adapter import config
from monitoring_adapter.xml import DecodeException, decode_message


LOGGER = logging.getLogger('monitoring-adapter')
LOGGER.setLevel(logging.DEBUG)

logging_handler = logging.StreamHandler()
logging_handler.setLevel(logging.DEBUG)
LOGGER.addHandler(logging_handler)


async def main(event_loop, monitor):
    LOGGER.info('Connecting to RabbitMQ')

    connection = await aio_pika.connect_robust(config.AMQP_URI, loop=event_loop)
    channel = await connection.channel()
    queue = await channel.get_queue(config.QUEUE_NAME)

    LOGGER.info('Succesfully connected to RabbitMQ')

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    try:
                        await process_message(message, monitor)
                    except DecodeException:
                        await handle_decode_exception(message)
                    except PersistenceException:
                        await handle_persistence_exception()
                    except Exception as e:
                        await handle_unexpected_exception(e)
                except PersistenceException:
                    await handle_persistence_exception()


async def process_message(message, monitor):
    utf8 = message.body.decode('utf-8')
    LOGGER.info(f'Message incoming from queue: \'{utf8}\'')

    model = decode_message(utf8)
    LOGGER.info(f'Decoded XML message into {model.__class__.__name__}')

    if not isinstance(model, Heartbeat):
        LOGGER.info(f'Persisting {model.__class__.__name__} to ElasticSearch')
        await model.persist()
    else:
        LOGGER.info(f'Processing Heartbeat with monitor')
        status_change = monitor.process_heartbeat(model)

        if status_change:
            LOGGER.info(f'Persisting StatusChange to ElasticSearch: {status_change.application_name} -> online: {status_change.online}')
            await status_change.persist()


async def handle_decode_exception(message):
    LOGGER.warning('Failed to decode message')
    error = Error(
        f'Failed to decoded message \'{message}\'',
        datetime.now().isoformat(),
        'monitoring',
    )

    LOGGER.info(f'Persisting Error to ElasticSearch')
    await error.persist()


async def handle_persistence_exception():
    # not much we can do if writing error to ElasticSearch fails
    # swallow exception, and let message be acknowledged
    LOGGER.critical('Failed to persist to ElasticSearch')
    pass


async def handle_unexpected_exception(e):
    LOGGER.error('Encountered unexpected exception')
    error = Error(
        f'Unexpected error \'{e.message}\'',
        datetime.now().isoformat(),
        'monitoring',
    )

    LOGGER.info(f'Persisting Error to ElasticSearch')
    await error.persist()


async def periodic_monitor(monitor):
    while True:
        await asyncio.sleep(monitor.OFFLINE_TRESHOLD_IN_SECONDS)

        LOGGER.info(f'Evaluating application statuses')

        for status_change in monitor.evaluate_statuses():
            LOGGER.info(f'Persisting StatusChange to ElasticSearch: {status_change.application_name} -> online: {status_change.online}')

            try:
                await status_change.persist()
            except PersistenceException:
                await handle_persistence_exception()

if __name__ == '__main__':
    LOGGER.info('Monitoring adapter starting up')
    monitor_instance = Monitor()
    loop = asyncio.get_event_loop()

    tasks = asyncio.gather(
        main(loop, monitor_instance),
        periodic_monitor(monitor_instance)
    )

    loop.run_until_complete(tasks)
    loop.close()
