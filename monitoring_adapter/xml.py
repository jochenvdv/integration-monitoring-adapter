import xmlschema

XML_SCHEMA = ''

xs = xmlschema.XMLSchema(XML_SCHEMA, converter=xmlschema.ParkerConverter)


def decode_message(message):
    decoded = xs.to_dict(message)


class DecodeException(Exception):
    pass
