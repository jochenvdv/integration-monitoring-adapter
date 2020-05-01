from monitoring_adapter.elasticsearch import (
    persist_error,
    persist_event,
    persist_log,
    persist_status_change)


class Event:
    def __init__(self, event_type, source_application):
        self.event_type = event_type,
        self.source_application = source_application

    async def persist(self):
        await persist_event(self)

    @staticmethod
    def from_xml(data):
        pass


class Error:
    def __init__(self, message, timestamp, source_application):
        self.message = message
        self.timestamp = timestamp
        self.source_application = source_application

    async def persist(self):
        await persist_error(self)

    def to_json(self):
        return {
            'message': self.message,
            'timestamp': self.timestamp,
            'application_name': self.source_application,
        }

    @classmethod
    def from_xml(cls, data):
        source_application = data['error']['application_name']['$']
        timestamp = data['error']['timestamp']['$']
        message = data['error']['message']['$']
        return cls(message, timestamp, source_application)


class LogMessage:
    def __init__(self, message, source_application, timestamp):
        self.message = message
        self.source_application = source_application
        self.timestamp = timestamp

    async def persist(self):
        await persist_log(self)

    def to_json(self):
        return {
            'message': self.message,
            'timestamp': self.timestamp,
            'application_name': self.source_application,
        }

    @classmethod
    def from_xml(cls, data):
        source_application = data['log']['application_name']['$']
        timestamp = data['log']['timestamp']['$']
        message = data['log']['message']['$']

        return cls(message, source_application, timestamp)


class Heartbeat:
    def __init__(self, source_application, timestamp):
        self.timestamp = timestamp
        self.source_application = source_application

    @classmethod
    def from_xml(cls, data):
        source_application = data['heartbeat']['application_name']['$']
        timestamp = data['heartbeat']['timestamp']['$']

        return cls(source_application, timestamp)


class StatusChange:
    def __init__(self, application_name, online):
        self.application_name = application_name
        self.online = online

    async def persist(self):
        await persist_status_change(self)

    def to_json(self):
        return {
            'application_name': self.source_application,
            'online': self.online,
        }
