import xmlschema

from monitoring_adapter.models import (
    LogMessage,
    Error,
    Heartbeat,
    Event
)

LOG_DECODER = xmlschema.XMLSchema('monitoring_adapter/resources/log.xsd', converter=xmlschema.BadgerFishConverter)
ERROR_DECODER = xmlschema.XMLSchema('monitoring_adapter/resources/error.xsd', converter=xmlschema.BadgerFishConverter)
HEARTBEAT_DECODER = xmlschema.XMLSchema('monitoring_adapter/resources/heartbeat.xsd', converter=xmlschema.BadgerFishConverter)

EVENT_DECODERS = {
    'add_user': xmlschema.XMLSchema('monitoring_adapter/resources/addUser.xsd', converter=xmlschema.BadgerFishConverter),
    'patch_user': xmlschema.XMLSchema('monitoring_adapter/resources/patchUser.xsd', converter=xmlschema.BadgerFishConverter),
    'add_invoice': xmlschema.XMLSchema('monitoring_adapter/resources/addInvoice.xsd', converter=xmlschema.BadgerFishConverter),
    'update_invoice': xmlschema.XMLSchema('monitoring_adapter/resources/updateInvoice.xsd', converter=xmlschema.BadgerFishConverter),
}


def get_event_decoder(message):
    for event_type, decoder in EVENT_DECODERS.items():
        if decoder.is_valid(message):
            return event_type, decoder

    return None


def decode_message(message):
    if LOG_DECODER.is_valid(message):
        decoded = LOG_DECODER.to_dict(message)
        model = LogMessage.from_xml(decoded)
    elif ERROR_DECODER.is_valid(message):
        decoded = ERROR_DECODER.to_dict(message)
        model = Error.from_xml(decoded)
    elif HEARTBEAT_DECODER.is_valid(message):
        decoded = HEARTBEAT_DECODER.to_dict(message)
        model = Heartbeat.from_xml(decoded)
    else:
        event_decoder = get_event_decoder(message)

        if event_decoder:
            decoded = event_decoder[1].to_dict(message)
            model = Event.from_xml(decoded, event_decoder[0])
        else:
            raise DecodeException

    return model


class DecodeException(Exception):
    pass
