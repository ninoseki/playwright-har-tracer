import pytest
from pytest_httpserver.httpserver import HTTPServer

from playwright_har_tracer import dataclasses
from tests.utils import page_with_har_tracer


async def generate_har(
    httpserver: HTTPServer,
) -> dataclasses.har.Har:
    httpserver.expect_oneshot_request("/foo", method="GET").respond_with_data(
        response_data="", status=200
    )

    async with page_with_har_tracer() as (page, tracer):
        await page.goto(httpserver.url_for("/foo"))

        har = await tracer.flush()
        return har


@pytest.mark.asyncio
async def test_enable_response_received_event_tracing(httpserver: HTTPServer):
    har = await generate_har(httpserver)

    entries = har.log.entries
    assert len(entries) == 1

    entry = entries[0]
    entry.response.comment == httpserver.host
    entry.response._remote_ip_address == httpserver.host
