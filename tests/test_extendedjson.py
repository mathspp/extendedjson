import json

import pytest

from extendedjson import ExtendedDecoder, ExtendedEncoder, __version__

# Some complex numbers to parametrize tests.
COMPLEX_NUMBERS = [0j, 1 + 2j, -3 + 6j, -3.14 + 42.73j]


class T:
    """Basic class that is not JSON-serialisable by default."""

    pass


class TEncoder(ExtendedEncoder):
    """Simple encoder for T."""

    def encode_T(self, t):
        return {}


class TDecoder(ExtendedDecoder):
    """Simple decoder for T."""

    def decode_T(self, dict_):
        return T()


class ComplexEncoder(ExtendedEncoder):
    """Simple encoder to test the encoding mechanism."""

    def encode_complex(self, c):
        return {"real": c.real, "imag": c.imag}


class ComplexDecoder(ExtendedDecoder):
    """Simple decoder to test the decoding mechanism."""

    def decode_complex(self, dict_):
        return complex(dict_["real"], dict_["imag"])


def test_version():
    assert __version__ == "0.1.1"


@pytest.mark.parametrize("c", COMPLEX_NUMBERS)
def test_complex_round_tripping(c):
    """Make sure that encoding and decoding produces the original data."""
    assert c == json.loads(json.dumps(c, cls=ComplexEncoder), cls=ComplexDecoder)


@pytest.mark.parametrize("obj", [range(10), slice(None, 1), lambda: None])
def test_wrong_type(obj):
    """Make sure that encoding something that's not encodable raises TypeError.

    It's the json documentation that says that a TypeError must be raised when
    trying to encode an object that is not serialisable.
    """

    with pytest.raises(TypeError):
        json.dumps(obj, cls=ComplexEncoder)


def test_unknown_encoded_type():
    """No custom decoding happens when trying to decode an unknown type."""

    json_string = json.dumps(T(), cls=TEncoder)
    assert json.loads(json_string) == json.loads(json_string, cls=ComplexDecoder)


def test_standard_dictionary():
    """Ensure standard dictionaries aren't decoded by mistake."""

    assert {} == json.loads("{}", cls=TDecoder)
    dict_ = {"real": 1, "imag": 2}
    assert dict_ == json.loads(json.dumps(dict_), cls=ComplexDecoder)
