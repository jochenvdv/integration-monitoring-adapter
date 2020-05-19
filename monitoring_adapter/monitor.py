from datetime import timedelta, datetime
from pytz import UTC, timezone
import dateutil.parser

from monitoring_adapter.models import StatusChange


TZ = timezone('Europe/Brussels')


class Monitor:
    OFFLINE_TRESHOLD_IN_SECONDS = 1.5

    def __init__(self):
        self._status = {}

    def process_heartbeat(self, heartbeat):
        application = heartbeat.source_application
        status_change = None
        parsed_timestamp = dateutil.parser.isoparse(heartbeat.timestamp)

        if application not in self._status:
            self._status[application] = ApplicationStatus(last_heartbeat=parsed_timestamp, online=True)
            status_change = StatusChange(application, online=True, timestamp=datetime.utcnow().isoformat())
        else:
            if not self._status[application].online:
                status_change = StatusChange(application, online=True, timestamp=datetime.utcnow().isoformat())
                self._status[application].online = True

            self._status[application].last_heartbeat = parsed_timestamp

        return status_change

    def evaluate_statuses(self):
        status_changes = []
        now = datetime.utcnow()
        oldest_allowed_heartbeat = now - timedelta(seconds=self.OFFLINE_TRESHOLD_IN_SECONDS)

        for application, status in self._status.items():
            last_heartbeat = status.last_heartbeat

            if last_heartbeat.tzinfo is None or last_heartbeat.tzinfo.utcoffset(last_heartbeat) is None:
                overdue = last_heartbeat < oldest_allowed_heartbeat
            else:
                overdue = last_heartbeat < UTC.localize(oldest_allowed_heartbeat)

            if status.online and overdue:
                status_changes.append(
                    StatusChange(application, online=False, timestamp=UTC.localize(datetime.utcnow()).isoformat())
                )
                status.online = False

        return status_changes


class ApplicationStatus:
    def __init__(self, last_heartbeat, online):
        self.last_heartbeat = last_heartbeat
        self.online = online
