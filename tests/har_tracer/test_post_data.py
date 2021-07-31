import pytest
from pytest_httpserver.httpserver import HTTPServer

from playwright_har_tracer import dataclasses
from tests.utils import page_with_har_tracer


async def generate_har(httpserver: HTTPServer) -> dataclasses.har.Har:
    httpserver.expect_oneshot_request("/foo", method="GET").respond_with_data(
        response_data="", status=200
    )
    httpserver.expect_oneshot_request("/post", method="POST").respond_with_json(
        response_json={},
        status=200,
    )

    async with page_with_har_tracer() as (page, tracer):
        await page.goto(httpserver.url_for("/foo"))
        await page.evaluate("""fetch('./post', { method: 'POST', body: 'Hello' })""")

        har = await tracer.flush()
        return har


@pytest.mark.asyncio
async def test_post_data(httpserver: HTTPServer):
    har = await generate_har(httpserver)

    entries = har.log.entries
    assert len(entries) == 2

    entry = entries[1]

    # assert body size
    assert entry.request.body_size > 0

    # assert post data
    post_data = entry.request.post_data
    assert post_data is not None
    assert post_data.mime_type == "text/plain;charset=UTF-8"
    assert post_data.params == []
    assert post_data.text == "Hello"

    assert entry.request.body_size > 0


async def generate_har_with_post_params(httpserver: HTTPServer) -> dataclasses.har.Har:
    httpserver.expect_oneshot_request("/foo", method="GET").respond_with_data(
        response_data="", status=200
    )
    httpserver.expect_oneshot_request("/post", method="POST").respond_with_json(
        response_json={},
        status=200,
    )

    async with page_with_har_tracer() as (page, tracer):
        await page.goto(httpserver.url_for("/foo"))

        await page.set_content(
            "<form method='POST' action='/post'><input type='text' name='foo' value='bar'><input type='number' name='baz' value='123'><input type='submit'></form>"
        )
        await page.click("input[type=submit]")

        har = await tracer.flush()
        return har


@pytest.mark.asyncio
async def test_post_data_with_params(httpserver: HTTPServer):
    har = await generate_har_with_post_params(httpserver)

    entries = har.log.entries
    entry = entries[1]

    # assert body size
    assert entry.request.body_size > 0

    # assert post data
    post_data = entry.request.post_data
    assert post_data is not None
    assert post_data.mime_type == "application/x-www-form-urlencoded"
    assert post_data.params == [
        dataclasses.har.Param(name="foo", value="bar"),
        dataclasses.har.Param(name="baz", value="123"),
    ]
    assert post_data.text == "foo=bar&baz=123"
