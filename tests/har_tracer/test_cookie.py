from datetime import datetime
from typing import Dict, List

import pytest
from pytest_httpserver.httpserver import HTTPServer

from playwright_har_tracer import dataclasses
from tests.utils import page_with_har_tracer


def cookies_to_dict(cookies: List[dataclasses.har.Cookie]) -> Dict[str, str]:
    d = {}
    for cookie in cookies:
        d[cookie.name] = cookie.value

    return d


async def generate_har(httpserver: HTTPServer, headers) -> dataclasses.har.Har:
    httpserver.expect_oneshot_request("/foo", method="GET").respond_with_data(
        response_data="", headers=headers
    )

    async with page_with_har_tracer() as (page, tracer):
        await page.goto(httpserver.url_for("/foo"))

        har = await tracer.flush()
        return har


@pytest.mark.asyncio
async def test_cookie(httpserver: HTTPServer):
    headers = {
        "content-type": "text/html",
        "set-cookie": "id=a3fWa; Max-Age=1500",
    }
    har = await generate_har(httpserver, headers=headers)

    # assert entries
    entries = har.log.entries

    entry = entries[0]
    cookies = entry.response.cookies
    assert len(cookies) == 1
    cookie = cookies[0]
    assert cookie.value == "a3fWa"
    assert cookie.expires is not None
    assert cookie.expires > datetime.now()


async def generate_har_with_unusual_cookies(
    httpserver: HTTPServer, cookie_value: str
) -> dataclasses.har.Har:
    set_cookie = f"cookie_name={cookie_value}"
    httpserver.expect_oneshot_request("/foo", method="GET").respond_with_data(
        response_data="", headers={"set-cookie": set_cookie}
    )

    async with page_with_har_tracer() as (page, tracer):
        await page.goto(httpserver.url_for("/foo"))
        har = await tracer.flush()
        return har


@pytest.mark.asyncio
@pytest.mark.parametrize("value", ['"value1"', 'val"ue2', "val=ue3", "val,ue4"])
async def test_unusual_cookies(httpserver: HTTPServer, value: str):
    har = await generate_har_with_unusual_cookies(httpserver, value)

    entries = har.log.entries
    entry = entries[0]
    cookies = entry.response.cookies
    assert len(cookies) == 1
    assert cookies[0].value == value
