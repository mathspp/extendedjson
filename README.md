# extendedjson

Easily extend JSON to encode and decode arbitrary Python objects.


## Getting started

You can [get `extendedjson` from PyPI](https://pypi.org/project/extendedjson),
which means it's easily installable with `pip`:

```bash
python -m pip install extendedjson
```


## Example usage

Suppose you want to extend the JSON format to handle complex numbers,
which corresponds to the type `complex` in Python.

To do that, you need to:

 1. Determine how a complex number could look like as a JSON dictionary.
 For example, a dictionary with keys `"real"` and `"imag"` is enough to determine what complex number we are talking about.
 2. Subclass `ExtendedEncoder` and implement the method `encode_complex` that accepts a complex number and returns a dictionary with the format you defined.
 3. Subclass `ExtendedDecoder` and implement a method `decode_complex` that accepts a dictionary with the format you described and returns an instance of a `complex` number.

Here is the code:

```py
import extendedjson as xjson


class MyEncoder(xjson.ExtendedEncoder):
    def encode_complex(self, c):
        return {"real": c.real, "imag": c.imag}


class MyDecoder(xjson.ExtendedDecoder):
    def decode_complex(self, dict_):
        return complex(dict_["real"], dict_["imag"])
```

Then, you can use your classes with the standard module `json`,
by specifying the `cls` keyword argument in the functions `json.load`, `json.loads`, `json.dump`, and `json.dumps`:

```py
import json

c = complex(1, 2)
c_json = json.dumps(c, cls=MyEncoder)
c_ = json.loads(c_json, cls=MyDecoder)
print(c_)  # (1+2j)
print(c_ == c)  # True
```

Refer to [this article](https://mathspp.com/blog/custom-json-encoder-and-decoder) to learn more about the internal details of `extendedjson`.


## Changelog

Refer to the [CHANGELOG.md](CHANGELOG.md) file.
