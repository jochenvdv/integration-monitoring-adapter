from datetime import timedelta, datetime

import dateutil.parser

from monitoring_adapter.models import StatusChange


class Monitor:
    OFFLINE_TRESHOLD_IN_SECONDS = 1

    def __init__(self):
        self._status = {}

    def process_heartbeat(self, heartbeat):
        application = heartbeat.source_application
        status_change = None
        parsed_timestamp = dateutil.parser.isoparse(heartbeat.timestamp)

        if application not in self._status:
            self._status[application] = ApplicationStatus(last_heartbeat=parsed_timestamp, online=True)
            status_change = StatusChange(application, online=True, timestamp=datetime.now().isoformat())
        else:
            if not self._status[application].online:
                status_change = StatusChange(application, online=True, timestamp=datetime.now().isoformat())
                self._status[application].online = True

            self._status[application].last_heartbeat = parsed_timestamp

        return status_change

    def evaluate_statuses(self):
        status_changes = []
        now = datetime.now()
        oldest_allowed_heartbeat = now - timedelta(seconds=self.OFFLINE_TRESHOLD_IN_SECONDS)

        for application, status in self._status.items():
            if status.online and status.last_heartbeat < oldest_allowed_heartbeat:
                status_changes.append(StatusChange(application, online=False, timestamp=datetime.now().isoformat()))
                status.online = False

        return status_changes


class ApplicationStatus:
    def __init__(self, last_heartbeat, online):
        self.last_heartbeat = last_heartbeat
        self.online = online
