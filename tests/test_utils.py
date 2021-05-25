from datetime import datetime, timezone

import pytest

from playwright_har_tracer import dataclasses
from playwright_har_tracer.utils import (
    datetime_to_millis,
    millis_to_roundish_millis,
    parse_cookie,
    query_to_query_params,
)


@pytest.mark.parametrize("input,expected", [(0.0, 0), (0.1, 0), (1.1, 1), (1.9, 1)])
def test_millis_to_roundish_millis(input: float, expected: int):
    assert millis_to_roundish_millis(input) == expected


def test_datetime_to_millis():
    dt = datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
    assert datetime_to_millis(dt) == 0.0


def test_query_to_query_params():
    query_params = query_to_query_params("name=value")
    assert query_params == [dataclasses.har.QueryParameter(name="name", value="value")]


def test_parse_cookie_with_max_age():
    cookie = parse_cookie("id=a3fWa; Max-Age=2592000")
    assert cookie.name == "id"
    assert cookie.value == "a3fWa"
    assert cookie.expires > datetime.now()


def test_parse_cookie_with_expires():
    cookie = parse_cookie("id=a3fWa; Expires=Wed, 21 Oct 1970 07:28:00 GMT")
    assert cookie.expires < datetime.now(tz=timezone.utc)


def test_parse_cookie_with_http_only():
    cookie = parse_cookie("id=a3fWa; HttpOnly")
    assert cookie.http_only is True


def test_parse_cookie_with_same_site():
    cookie = parse_cookie("id=a3fWa; SameSite=Lax")
    assert cookie.same_site == "Lax"


def test_parse_cookie_with_domain():
    cookie = parse_cookie("id=a3fWa; Domain=example.com")
    assert cookie.domain == "example.com"


def test_parse_cookie_with_secure():
    cookie = parse_cookie("id=a3fWa; Secure")
    assert cookie.secure is True


def test_parse_cookie_with_path():
    cookie = parse_cookie("id=a3fWa; Path=/foo")
    assert cookie.path == "/foo"
