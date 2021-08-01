import base64
from datetime import datetime, timezone
from typing import Dict, List

import pytest
from pytest_httpserver.httpserver import HTTPServer

from playwright_har_tracer import __version__, dataclasses
from tests.utils import page_with_har_tracer


def headers_to_dict(headers: List[dataclasses.har.Header]) -> Dict[str, str]:
    d = {}
    for header in headers:
        d[header.name] = header.value

    return d


async def generate_har(
    httpserver: HTTPServer,
    response_data: str,
    status: int,
    headers: Dict[str, str],
) -> dataclasses.har.Har:

    httpserver.expect_oneshot_request("/foo", method="GET").respond_with_data(
        response_data=response_data, status=status, headers=headers
    )

    async with page_with_har_tracer() as (page, tracer):
        await page.goto(httpserver.url_for("/foo"))

        har = await tracer.flush()
        return har


@pytest.mark.asyncio
async def test_har_tracer(httpserver: HTTPServer, test_html: str):
    status = 200
    headers = {"content-type": "text/html"}
    har = await generate_har(
        httpserver, response_data=test_html, status=status, headers=headers
    )

    # assert log
    assert har.log.version == "1.2"

    # assert creator
    assert har.log.creator.version == __version__
    assert har.log.creator.name == "playwright-har-tracer"

    # assert browser
    assert har.log.browser.name == "chromium"

    # assert pages
    assert len(har.log.pages) == 1

    # assert page
    page = har.log.pages[0]
    assert page.id == "page_0"
    assert page.title == "Document"
    assert page.started_date_time < datetime.now(timezone.utc)
    assert page.page_timings.on_content_load is not None
    assert float(page.page_timings.on_content_load) > 0.0
    assert page.page_timings.on_load is not None
    assert float(page.page_timings.on_load) > 0.0

    # assert entries
    entries = har.log.entries
    assert len(entries) == 1

    entry = entries[0]
    # assert request
    assert entry.request.method == "GET"
    assert entry.request.url == httpserver.url_for("/foo")
    assert entry.request.http_version == "HTTP/1.1"
    headers = headers_to_dict(entry.request.headers)
    assert "user-agent" in headers
    assert entry.request.body_size == 0

    # assert response
    assert entry.response.status == status
    assert entry.response.status_text == "OK"
    assert entry.response.http_version == "HTTP/1.1"
    assert len(entry.response.headers) > 0
    headers = headers_to_dict(entry.response.headers)
    assert headers.get("content-type") == "text/html"

    # assert content
    assert entry.response.content.encoding == "base64"
    assert entry.response.content.mime_type == "text/html"
    assert entry.response.content.text is not None
    assert base64.b64decode(entry.response.content.text).decode() == test_html

    # assert server IP address and port
    assert entry.server_ip_address == "127.0.0.1"
    assert entry._server_port == httpserver.port

    # assert security details
    assert entry._security_details is None
