import json

import pytest

from extendedjson import ExtendedDecoder, ExtendedEncoder, __version__


class ComplexEncoder(ExtendedEncoder):
    def encode_complex(self, c):
        return {"real": c.real, "imag": c.imag}


class ComplexDecoder(ExtendedDecoder):
    def decode_complex(self, dict_):
        return complex(dict_["real"], dict_["imag"])


def test_version():
    assert __version__ == "0.1.1"


@pytest.mark.parametrize("c", [0j, 1 + 2j, -3 + 6j, -3.14 + 42.73j])
def test_complex_round_tripping(c):
    assert c == json.loads(json.dumps(c, cls=ComplexEncoder), cls=ComplexDecoder)
