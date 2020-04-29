import xmlschema
from xmlschema import XMLSchemaParseError

from monitoring_adapter.models import (
    LogMessage,
    Error,
)

#EVENT_DECODER = xmlschema.XMLSchema('monitoring_adapter/resources/event.xsd', converter=xmlschema.BadgerFishConverter)
LOG_DECODER = xmlschema.XMLSchema('monitoring_adapter/resources/log.xsd', converter=xmlschema.BadgerFishConverter)
ERROR_DECODER = xmlschema.XMLSchema('monitoring_adapter/resources/error.xsd', converter=xmlschema.BadgerFishConverter)
#HEARTBEAT_DECODER = xmlschema.XMLSchema('monitoring_adapter/resources/heartbeat.xsd', converter=xmlschema.BadgerFishConverter)


def decode_message(message):
    try:
        if LOG_DECODER.is_valid(message):
            decoded = LOG_DECODER.to_dict(message)
            model = LogMessage.from_xml(decoded)
        elif ERROR_DECODER.is_valid(message):
            decoded = ERROR_DECODER.to_dict(message)
            model = Error.from_xml(decoded)
        else:
            # skip heartbeats & events for now
            model = None
    except XMLSchemaParseError:
        raise DecodeException

    return model


class DecodeException(Exception):
    pass
