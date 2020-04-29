import aiohttp

from monitoring_adapter.config import ELASTICSEARCH_URI


async def persist_event(event):
    return await persist_document('events', event.to_json())


async def persist_error(error):
    return await persist_document('errors', error.to_json())


async def persist_log(log):
    return await persist_document('logs', log.to_json())


async def persist_document(index, document):
    async with aiohttp.request(method='POST', url=f'{ELASTICSEARCH_URI}/{index}/_doc', json=document) as response:
        if response.status != 200:
            raise PersistenceException


class PersistenceException(Exception):
    pass
