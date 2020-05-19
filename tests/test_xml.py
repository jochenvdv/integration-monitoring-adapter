from monitoring_adapter.models import LogMessage, Error, Heartbeat, Event
from monitoring_adapter.xml import decode_message


def test_log_decode():
    message = '<log><application_name>kassa</application_name><timestamp>2020-04-30T16:42:57+00:00</timestamp><message>test</message></log>'
    log = decode_message(message)
    assert isinstance(log, LogMessage)
    assert log.source_application == 'kassa'
    assert log.timestamp == '2020-04-30T16:42:57+00:00'
    assert log.message == 'test'


def test_error_decode():
    message = '<error><application_name>kassa</application_name><timestamp>2020-04-30T16:42:57+00:00</timestamp><message>test</message></error>'
    error = decode_message(message)
    assert isinstance(error, Error)
    assert error.source_application == 'kassa'
    assert error.timestamp == '2020-04-30T16:42:57+00:00'
    assert error.message == 'test'


def test_heartbeat_decode():
    message = '<heartbeat><application_name>kassa</application_name><timestamp>2020-04-30T16:42:57+00:00</timestamp></heartbeat>'
    heartbeat = decode_message(message)
    assert isinstance(heartbeat, Heartbeat)
    assert heartbeat.source_application == 'kassa'
    #assert heartbeat.timestamp == '2020-04-30T16:42:57+00:00'


def test_event_adduser_decode():
    message = '<add_user><application_name>kassa</application_name><name>test</name><uuid>test</uuid><email>test</email><street>test</street><municipal>test</municipal><postalCode>test</postalCode><vat>test</vat></add_user>'
    event = decode_message(message)
    assert isinstance(event, Event)
    assert event.event_type == 'add_user'
    assert event.source_application == 'kassa'


def test_event_patchuser_decode():
    message = '<patch_user><application_name>kassa</application_name><name>test</name><uuid>test</uuid><email>test</email><street>test</street><municipal>test</municipal><postalCode>test</postalCode><vat>test</vat></patch_user>'
    event = decode_message(message)
    assert isinstance(event, Event)
    assert event.event_type == 'patch_user'
    assert event.source_application == 'kassa'


def test_event_addinvoice_decode():
    message = '<add_invoice><application_name>kassa</application_name><uuid>test</uuid><paid>test</paid><invoice_date>test</invoice_date><order_line><name>test</name><quantity>test</quantity><price>test</price><discount>test</discount></order_line></add_invoice>'
    event = decode_message(message)
    assert isinstance(event, Event)
    assert event.event_type == 'add_invoice'
    assert event.source_application == 'kassa'


def test_event_updateinvoice_decode():
    message = '<update_invoice><application_name>kassa</application_name><invoice_id>test</invoice_id><name>test</name><description>test</description><quantity>test</quantity><price>test</price><paid>test</paid></update_invoice>'
    event = decode_message(message)
    assert isinstance(event, Event)
    assert event.event_type == 'update_invoice'
    assert event.source_application == 'kassa'
