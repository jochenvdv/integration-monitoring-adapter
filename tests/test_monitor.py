from datetime import datetime
from time import sleep
from pytz import UTC

from monitoring_adapter.models import Heartbeat, StatusChange
from monitoring_adapter.monitor import Monitor


def now():
    return UTC.localize(datetime.now()).isoformat()


def test_monitor_process_heartbeat_returns_statuschange_on_first_heartbeat():
    monitor = Monitor()

    heartbeat = Heartbeat(source_application='kassa', timestamp=now())
    status_change = monitor.process_heartbeat(heartbeat)
    assert isinstance(status_change, StatusChange)
    assert status_change.application_name == 'kassa'
    assert status_change.online


def test_monitor_process_heartbeat_returns_no_statuschange_on_second_heartbeat_in_time():
    monitor = Monitor()

    heartbeat1 = Heartbeat(source_application='kassa', timestamp=now())
    monitor.process_heartbeat(heartbeat1)

    sleep(monitor.OFFLINE_TRESHOLD_IN_SECONDS / 2)

    heartbeat2 = Heartbeat(source_application='kassa', timestamp=now())
    status_change = monitor.process_heartbeat(heartbeat2)
    assert status_change is None


def test_monitor_evaluate_statuses_returns_no_statuschange_if_heartbeat_not_overdue():
    monitor = Monitor()

    heartbeat = Heartbeat(source_application='kassa', timestamp=now())
    monitor.process_heartbeat(heartbeat)

    status_changes = monitor.evaluate_statuses()
    assert type(status_changes) is list
    assert len(status_changes) == 0


def test_monitor_evaluate_statuses_returns_statuschange_if_heartbeat_overdue():
    monitor = Monitor()

    heartbeat = Heartbeat(source_application='kassa', timestamp=now())
    monitor.process_heartbeat(heartbeat)

    sleep(monitor.OFFLINE_TRESHOLD_IN_SECONDS * 2)

    status_changes = monitor.evaluate_statuses()
    assert type(status_changes) is list
    assert len(status_changes) == 1
    assert isinstance(status_changes[0], StatusChange)
    assert status_changes[0].application_name == 'kassa'
    assert not status_changes[0].online


def test_monitor_evaluate_statuses_returns_statuschange_if_heartbeat_overdue_but_was_already_offline():
    monitor = Monitor()

    heartbeat = Heartbeat(source_application='kassa', timestamp=now())
    monitor.process_heartbeat(heartbeat)

    sleep(monitor.OFFLINE_TRESHOLD_IN_SECONDS * 2)

    monitor.evaluate_statuses()

    status_changes = monitor.evaluate_statuses()
    assert type(status_changes) is list
    assert len(status_changes) == 0


def test_monitor_process_heart_returns_statuschange_if_application_comes_back_online():
    monitor = Monitor()

    heartbeat1 = Heartbeat(source_application='kassa', timestamp=now())
    monitor.process_heartbeat(heartbeat1)

    sleep(monitor.OFFLINE_TRESHOLD_IN_SECONDS * 2)

    monitor.evaluate_statuses()

    heartbeat2 = Heartbeat(source_application='kassa', timestamp=now())
    status_change = monitor.process_heartbeat(heartbeat2)
    assert isinstance(status_change, StatusChange)
    assert status_change.application_name == 'kassa'
    assert status_change.online


def test_monitor_evaluate_statuses_accepts_non_localized_heartbeat():
    monitor = Monitor()

    heartbeat = Heartbeat(source_application='kassa', timestamp=datetime.now().isoformat())
    monitor.process_heartbeat(heartbeat)

    status_changes = monitor.evaluate_statuses()
    assert type(status_changes) is list
    assert len(status_changes) == 0

