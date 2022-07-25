import io
import json

import pytest

import extendedjson as xjson
from extendedjson import ExtendedDecoder, ExtendedEncoder, __version__

# Some complex numbers to parametrize tests.
COMPLEX_NUMBERS = [0j, 1 + 2j, -3 + 6j, -3.14 + 42.73j]


class T:
    """Basic class that is not JSON-serialisable by default."""

    def __eq__(self, other):
        return isinstance(other, T)


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
    assert __version__ == "0.1.2"


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


@pytest.mark.parametrize("c", COMPLEX_NUMBERS)
def test_dump_default(c):
    """Ensure xjson.dump matches json.dump by default."""

    assert xjson.dump.__defaults__[0] == json.JSONEncoder
    with pytest.raises(TypeError):
        xjson.dump(c, io.StringIO())


@pytest.mark.parametrize("c", COMPLEX_NUMBERS)
def test_dumps_default(c):
    """Ensure xjson.dumps matches json.dumps by default."""

    assert xjson.dump.__defaults__[0] == json.JSONEncoder
    with pytest.raises(TypeError):
        xjson.dumps(c)


@pytest.mark.parametrize("c", COMPLEX_NUMBERS)
def test_load_default(c):
    """Ensure xjson.load matches json.load by default."""

    assert xjson.load.__defaults__[0] == json.JSONDecoder

    fp = io.StringIO()
    json.dump(c, fp, cls=ComplexEncoder)
    fp.seek(0)
    assert xjson.load(fp) == json.loads(json.dumps(c, cls=ComplexEncoder))


@pytest.mark.parametrize("c", COMPLEX_NUMBERS)
def test_loads_default(c):
    """Ensure xjson.loads matches json.loads by default."""

    assert xjson.loads.__defaults__[0] == json.JSONDecoder

    json_string = json.dumps(c, cls=ComplexEncoder)
    assert xjson.loads(json_string) == json.loads(json_string)


def test_register_encoder():
    """Test registering encoders."""

    c = 3 + 4j
    xjson.register_encoder(ComplexEncoder)
    assert c == json.loads(xjson.dumps(c), cls=ComplexDecoder)

    xjson.register_encoder(TEncoder)
    with pytest.raises(TypeError):
        xjson.dumps(c)
    assert T() == json.loads(xjson.dumps(T()), cls=TDecoder)

    xjson.register_encoder(json.JSONEncoder)
    with pytest.raises(TypeError):
        xjson.dumps(c)
    with pytest.raises(TypeError):
        xjson.dumps(T())


def test_register_decoder():
    """Test registering decoders."""

    c = 3 + 4j
    xjson.register_decoder(ComplexDecoder)
    c_json = json.dumps(c, cls=ComplexEncoder)
    assert c == xjson.loads(c_json)

    xjson.register_decoder(TDecoder)
    assert json.loads(c_json) == xjson.loads(c_json)
    T_json = json.dumps(T(), cls=TEncoder)
    assert T() == xjson.loads(json.dumps(T(), cls=TEncoder))

    xjson.register_decoder(json.JSONDecoder)
    assert json.loads(c_json) == xjson.loads(c_json)
    assert json.loads(T_json) == xjson.loads(T_json)
