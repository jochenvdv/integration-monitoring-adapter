import asyncio
import aio_pika

from monitoring_adapter import (
    config,
    # events,
    # errors,
    # heartbeats,
    # xml,
    # common
)


async def main(event_loop):
    connection = await aio_pika.connect_robust(config.AMQP_URI, loop=event_loop)
    channel = await connection.channel()
    queue = await channel.declare_queue(config.QUEUE_NAME, internal=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print(message.body)

                # try:
                #     obj = xml.decode_message(message.body.decode())
                # except xml.DecodeException:
                #     message.reject()
                #
                # try:
                #     if isinstance(obj, events.Event):
                #         await events.process_event(obj)
                #     elif isinstance(obj, heartbeats.Heartbeat):
                #         await heartbeats.process_heartbeat(obj)
                #     elif isinstance(obj, errors.Error):
                #         await errors.process_error(obj)
                # except common.ProcessingFailure:
                #     message.reject()


                # parse message using XSD
                # call correct Python module for processing message (event, error or heartbeat)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
