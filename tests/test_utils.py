from datetime import datetime, timezone
from typing import Optional

import pytest

from playwright_har_tracer import dataclasses
from playwright_har_tracer.utils import (
    calculate_request_headers_size,
    calculate_response_headers_size,
    datetime_to_millis,
    millis_to_roundish_millis,
    normalize_http_version,
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


@pytest.mark.parametrize(
    "input,expected", [(None, "HTTP/1.1"), ("http/1.1", "HTTP/1.1")]
)
def test_normalize_http_version(input: Optional[str], expected: str):
    assert normalize_http_version(input) == expected


def test_calculate_request_headers_size():
    size = calculate_request_headers_size(
        "GET",
        "/",
        "HTTP/1.1",
        {
            "Host": "example.com",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/93.0.4576.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
        },
    )
    assert size == 407


def test_calculate_response_headers_size():
    size = calculate_response_headers_size(
        "HTTP/1.1",
        200,
        "OK",
        {
            "Content-Encoding": "gzip",
            "Accept-Ranges": "bytes",
            "Age": "410497",
            "Cache-Control": "max-age=604800",
            "Content-Type": "text/html; charset=UTF-8",
            "Date": "Sat, 31 Jul 2021 10:03:11 GMT",
            "Etag": '"3147526947+ident"',
            "Expires": "Sat, 07 Aug 2021 10:03:11 GMT",
            "Last-Modified": "Thu, 17 Oct 2019 07:18:26 GMT",
            "Server": "ECS (sec/9794)",
            "Vary": "Accept-Encoding",
            "X-Cache": "HIT",
            "Content-Length": "648",
        },
    )
    assert size == 380
