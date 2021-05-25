import pytest
from pytest_httpserver.httpserver import HTTPServer

from playwright_har_tracer import dataclasses
from tests.utils import page_with_har_tracer


async def generate_har(
    httpserver: HTTPServer,
) -> dataclasses.har.Har:
    httpserver.expect_oneshot_request(
        "/foo?name=value", method="GET"
    ).respond_with_data(response_data="", status=200)

    async with page_with_har_tracer() as (page, tracer):
        await page.goto(httpserver.url_for("/foo?name=value"))

        har = await tracer.flush()
        return har


@pytest.mark.asyncio
async def test_query_params(httpserver: HTTPServer):
    har = await generate_har(httpserver)

    entries = har.log.entries
    assert len(entries) == 1

    first = entries[0]
    assert first.request.query_string == [
        dataclasses.har.QueryParameter(name="name", value="value")
    ]
