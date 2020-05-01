from monitoring_adapter.models import LogMessage, Error, Heartbeat
from monitoring_adapter.xml import decode_message


def test_log_decode():
    message = b'<log><application_name>kassa</application_name><timestamp>2020-04-30T16:42:57+00:00</timestamp><message>test</message></log>'
    log = decode_message(message)
    assert isinstance(log, LogMessage)
    assert log.source_application == 'kassa'
    assert log.timestamp == '2020-04-30T16:42:57+00:00'
    assert log.message == 'test'


def test_error_decode():
    message = b'<error><application_name>kassa</application_name><timestamp>2020-04-30T16:42:57+00:00</timestamp><message>test</message></error>'
    error = decode_message(message)
    assert isinstance(error, Error)
    assert error.source_application == 'kassa'
    assert error.timestamp == '2020-04-30T16:42:57+00:00'
    assert error.message == 'test'


def test_heartbeat_decode():
    message = b'<heartbeat><application_name>kassa</application_name><timestamp>2020-04-30T16:42:57+00:00</timestamp></heartbeat>'
    heartbeat = decode_message(message)
    assert isinstance(heartbeat, Heartbeat)
    assert heartbeat.source_application == 'kassa'
    assert heartbeat.timestamp == '2020-04-30T16:42:57+00:00'
