from datetime import datetime

from monitoring_adapter.models import Event, LogMessage, Error, StatusChange


def test_event():
    event = Event(event_type='add_user', source_application='kassa')
    assert event.to_json() == {
        'event_type': 'add_user',
        'application_name': 'kassa',
    }


def test_log():
    timestamp = datetime.now().isoformat()
    log = LogMessage(message='test', source_application='kassa', timestamp=timestamp)
    assert log.to_json() == {
        'message': 'test',
        'application_name': 'kassa',
        'timestamp': timestamp,
    }


def test_error():
    timestamp = datetime.now().isoformat()
    error = Error(message='test', source_application='kassa', timestamp=timestamp)
    assert error.to_json() == {
        'message': 'test',
        'application_name': 'kassa',
        'timestamp': timestamp,
    }


def test_statuschange():
    timestamp = datetime.now().isoformat()
    statuschange = StatusChange(online=True, application_name='kassa', timestamp=timestamp)
    assert statuschange.to_json() == {
        'online': True,
        'application_name': 'kassa',
        'timestamp': timestamp,
    }
