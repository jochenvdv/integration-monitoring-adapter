from monitoring_adapter import config


async def process_event(channel):
    queue = channel.declare_queue(config.EVENTS_QUEUE_NAME, internal=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print(message.body)

                if queue.name in message.body.decode():
                    break
