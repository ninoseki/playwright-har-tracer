import json
import pathlib

import dateutil.parser

from playwright_har_tracer.dataclasses.har import Har


def datetime_decoder(data: dict) -> dict:
    for field, value in data.items():
        if field in ["startedDateTime", "expires"]:
            data[field] = dateutil.parser.parse(value)
    return data


path = pathlib.Path(__file__).parent / "./fixtures/test.har"
with open(path) as f:
    fixture = json.loads(f.read(), object_hook=datetime_decoder)


def test_har_from_dict():
    har = Har.from_dict(fixture)
    assert har


def test_har_to_dict():
    har = Har.from_dict(fixture)
    assert isinstance(har.to_dict(), dict)


def test_har_to_json():
    har = Har.from_dict(fixture)
    json_str = har.to_json()
    assert isinstance(json_str, str)

    # also it should be converted as a dataclass
    har = Har.from_dict(json.loads(json_str, object_hook=datetime_decoder))
    assert isinstance(har, Har)
