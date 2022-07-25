"""
This module defines the main mechanism to extend the JSON format.
"""

__version__ = "0.1.3"

import json


class ExtendedEncoder(json.JSONEncoder):
    """JSON encoder defining the mechanism to encode arbitrary Python objects.

    To encode an arbitrary object, you should subclass this encoder and define one
    encode_X method for each type of object you want to be able to encode.
    The method name should start with "encode_" and end with the type name.
    The method accepts the given type of Python object and
    should return a JSON-serialisable dictionary with the appropriate data,
    which typically amounts to the data necessary to rebuild the object later on.
    A related decoder must be implemented if decoding from JSON is required.
    """

    def default(self, o):
        name = type(o).__name__
        try:
            encoder = getattr(self, f"encode_{name}")
        except AttributeError:
            return super().default(o)
        else:
            encoded = encoder(o)
            encoded["__extended_json_type__"] = name
            return encoded


class ExtendedDecoder(json.JSONDecoder):
    """JSON decoder defining the mechanism to decode arbitrary JSON objects.

    To decode an arbitrary object encoded by the related JSON encoder,
    you should subclass this decoder and define one decode_X method for
    each type of object you want to be able to decode.
    The method name should start with "decode_" and end with the type name.
    The method accepts a Python dictionary with string keys and should be able
    to reconstruct the arbitrary object from the data provided in the dictionary.
    """

    def __init__(self, **kwargs):
        kwargs["object_hook"] = self._object_hook
        super().__init__(**kwargs)

    def _object_hook(self, obj):
        """Default object hook that matches the encoder behaviour."""

        try:
            name = obj["__extended_json_type__"]
            decoder = getattr(self, f"decode_{name}")
        except (KeyError, AttributeError):
            return obj
        else:
            return decoder(obj)


def dump(obj, fp, cls=json.JSONEncoder, **kwargs):  # pylint: disable=invalid-name
    """Thin wrapper around `json.dump` with customisable default encoder."""
    return json.dump(obj, fp, cls=cls, **kwargs)


def dumps(obj, cls=json.JSONEncoder, **kwargs):
    """Thin wrapper around `json.dumps` with customisable default encoder."""
    return json.dumps(obj, cls=cls, **kwargs)


def load(fp, cls=json.JSONDecoder, **kwargs):  # pylint: disable=invalid-name
    """Thin wrapper around `json.load` with customisable default decoder."""
    return json.load(fp, cls=cls, **kwargs)


def loads(s, cls=json.JSONDecoder, **kwargs):  # pylint: disable=invalid-name
    """Thin wrapper around `json.loads` with customisable default decoder."""
    return json.loads(s, cls=cls, **kwargs)


def register_encoder(encoder_cls):
    """Decorator to register a new extended JSON encoder.

    This decorator sets the decorated class as the default encoder used by the
    functions `dump` and `dumps` provided in this module.
    The decorated class is not modified and should be a subclass of ExtendedEncoder.
    """
    dump.__defaults__ = (encoder_cls,)
    dumps.__defaults__ = (encoder_cls,)
    return encoder_cls


def register_decoder(decoder_cls):
    """Decorator to register a new extended JSON decoder.

    This decorator sets the decorated class as the default decoder used by the
    functions `load` and `loads` provided in this module.
    The decorated class is not modified and should be a subclass of ExtendedDecoder.
    """
    load.__defaults__ = (decoder_cls,)
    loads.__defaults__ = (decoder_cls,)
    return decoder_cls
