"""
This module defines the main mechanism to extend the JSON format.
"""

__version__ = "0.1.1"

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
