import asyncio
import base64
import copy
from datetime import datetime
from typing import Dict, List, Union
from urllib.parse import urlparse

import poetry_version
from playwright.async_api import BrowserContext, CDPSession, Page, Request, Response

from . import dataclasses
from .utils import (
    cookies_for_har,
    datetime_to_millis,
    dict_to_headers,
    millis_to_roundish_millis,
    post_data_for_har,
    query_to_query_params,
    set_remote_ip_address_as_comment,
)

__version__ = poetry_version.extract(source_file=__file__)


HAR_VERSION: str = "1.2"
CREATOR_NAME: str = "playwright-har-tracer"
CREATOR_VERSION: str = __version__


class HarTracer:
    def __init__(
        self,
        context: BrowserContext,
        browser_name: str,
        *,
        omit_content: bool = False,
    ):
        if context.browser is None:
            raise ValueError

        self._omit_content = omit_content

        self._page_entries: Dict[Page, dataclasses.har.Page] = {}
        self._entries: Dict[Request, dataclasses.har.Entry] = {}
        self._last_page: int = 0

        self._loop = asyncio.get_event_loop()
        self._tasks: List[asyncio.Task] = []

        self._on_load_event = asyncio.Event()
        self._on_dom_content_loaded_event = asyncio.Event()

        self._log = dataclasses.har.Log(
            version=HAR_VERSION,
            creator=dataclasses.har.Creator(name=CREATOR_NAME, version=CREATOR_VERSION),
            browser=dataclasses.har.Browser(
                name=browser_name, version=context.browser.version
            ),
            pages=[],
            entries=[],
        )

        self._response_received_events: List[dataclasses.cdp.ResponseReceivedEvent] = []

        def on_request(page: Page, request: Request) -> None:
            page_entry = self._page_entries.get(page)
            if page_entry is None:
                return

            parsed_url = urlparse(request.url)

            har_entry = dataclasses.har.Entry(
                pageref=page_entry.id,
                started_date_time=datetime.now(),
                time=-1,
                request=dataclasses.har.Request(
                    method=request.method,
                    url=request.url,
                    http_version="HTTP/1.1",
                    cookies=[],
                    headers=[],
                    query_string=query_to_query_params(parsed_url.query),
                    post_data=None,
                    headers_size=-1,
                    body_size=-1,
                ),
                response=dataclasses.har.Response(
                    status=-1,
                    status_text="",
                    http_version="HTTP/1.1",
                    cookies=[],
                    headers=[],
                    content=dataclasses.har.Content(
                        size=-1,
                        mime_type=request.headers.get("content-type")
                        or "application/octet-stream",
                    ),
                    headers_size=-1,
                    body_size=-1,
                    redirect_url="",
                ),
                cache=dataclasses.har.Cache(before_request=None, after_request=None),
                timings=dataclasses.har.Timings(send=-1, wait=-1, receive=-1),
            )

            redirected_from_request = request.redirected_from
            if redirected_from_request is not None:
                from_entry = self._entries.get(redirected_from_request)
                if from_entry is not None:
                    from_entry.response.redirect_url = request.url

            self._log.entries.append(har_entry)
            self._entries[request] = har_entry

        def on_response(page: Page, response: Response) -> None:
            page_entry = self._page_entries.get(page)
            if page_entry is None:
                return

            request = response.request
            har_entry = self._entries.get(request)
            if har_entry is None:
                return

            # Rewrite provisional headers with actual
            har_entry.request.headers = dict_to_headers(request.headers)
            har_entry.request.cookies = cookies_for_har(
                request.headers.get("cookie"), ";"
            )
            har_entry.request.post_data = post_data_for_har(request)

            har_entry.response = dataclasses.har.Response(
                status=response.status,
                status_text=response.status_text,
                http_version="HTTP/1.1",
                cookies=cookies_for_har(response.headers.get("set-cookie"), "\n"),
                headers=dict_to_headers(response.headers),
                content=dataclasses.har.Content(
                    size=-1,
                    mime_type=response.headers.get(
                        "content-type", "application/octet-stream"
                    ),
                ),
                headers_size=-1,
                body_size=-1,
                redirect_url="",
            )

            timing = response.request.timing
            start_time = timing.get("startTime", 0.0)
            if datetime_to_millis(page_entry.started_date_time) > start_time:
                page_entry.started_date_time = datetime.fromtimestamp(
                    start_time / 1000.0
                )

            domain_lookup_start: Union[float, int] = timing.get("domainLookupStart", -1)
            domain_lookup_end: Union[float, int] = timing.get("domainLookupEnd", -1)
            dns = (
                millis_to_roundish_millis(domain_lookup_end - domain_lookup_start)
                if domain_lookup_end != -1
                else -1
            )

            connect_start: Union[float, int] = timing.get("connectStart", -1)
            connect_end: Union[float, int] = timing.get("connectEnd", -1)
            connect = (
                millis_to_roundish_millis(connect_end - connect_start)
                if connect_end != -1
                else -1
            )

            secure_connection_start: Union[float, int] = timing.get(
                "secureConnectionStart", -1
            )
            ssl = (
                millis_to_roundish_millis(connect_end - secure_connection_start)
                if connect_end != -1
                else -1
            )

            request_start: Union[float, int] = timing.get("requestStart", -1)
            response_start: Union[float, int] = timing.get("responseStart", -1)
            wait = (
                millis_to_roundish_millis(response_start - request_start)
                if response_start != -1
                else -1
            )

            response_end: Union[float, int] = timing.get("responseEnd", -1)
            receive = (
                millis_to_roundish_millis(response_end - response_start)
                if response_end != -1
                else -1
            )

            har_entry.timings = dataclasses.har.Timings(
                dns=dns,
                connect=connect,
                ssl=ssl,
                send=0,
                wait=wait,
                receive=receive,
            )
            har_entry.time = sum([dns, connect, ssl, wait, receive])

            if self._omit_content is False and response.status == 200:

                async def on_response_task():
                    body = await response.body()
                    har_entry.response.content.text = base64.b64encode(body).decode()
                    har_entry.response.content.encoding = "base64"

                self._tasks.append(self._loop.create_task(on_response_task()))

        def on_page(page: Page) -> None:
            page_entry = dataclasses.har.Page(
                started_date_time=datetime.now(),
                id=f"page_{self._last_page}",
                title="",
                page_timings=dataclasses.har.PageTimings(
                    on_content_load=-1, on_load=-1
                ),
            )
            self._last_page += 1

            self._page_entries[page] = page_entry
            self._log.pages.append(page_entry)

            page.on("request", lambda request: on_request(page, request))
            page.on("response", lambda response: on_response(page, response))

            def on_dom_content_loaded(page: Page) -> None:
                async def on_dom_content_loaded_task():
                    result: Dict[str, Union[str, int]] = await page.main_frame.evaluate(
                        """Promise.resolve({title: document.title, domContentLoaded: performance.timing.domContentLoadedEventStart})"""
                    )

                    title = str(result.get("title", ""))
                    page_entry.title = title

                    dom_content_loaded = int(result.get("domContentLoaded", 0))
                    page_entry.page_timings.on_content_load = dom_content_loaded

                    self._on_dom_content_loaded_event.set()

                self._tasks.append(self._loop.create_task(on_dom_content_loaded_task()))

            async def wait_on_dom_content_loaded_task():
                await self._on_dom_content_loaded_event.wait()

            self._tasks.append(
                self._loop.create_task(wait_on_dom_content_loaded_task())
            )

            def on_load(page: Page) -> None:
                async def on_load_task():
                    result: Dict[str, Union[str, int]] = await page.main_frame.evaluate(
                        """Promise.resolve({title: document.title, loaded: performance.timing.loadEventStart})"""
                    )

                    title = str(result.get("title", ""))
                    page_entry.title = title

                    loaded = int(result.get("loaded", 0))
                    page_entry.page_timings.on_load = loaded

                    self._on_load_event.set()

                self._tasks.append(self._loop.create_task(on_load_task()))

            async def wait_on_load_task():
                await self._on_load_event.wait()

            self._tasks.append(self._loop.create_task(wait_on_load_task()))

            page.on("domcontentloaded", lambda: on_dom_content_loaded(page))
            page.on("load", lambda: on_load(page))

        context.on("page", on_page)

    async def enable_response_received_event_tracing(self, client: CDPSession):
        await client.send("Network.enable")
        client.on(
            "Network.responseReceived",
            lambda data: self._response_received_events.append(
                dataclasses.cdp.ResponseReceivedEvent.from_dict(data)
            ),
        )

    async def flush(self) -> dataclasses.har.Har:
        await asyncio.gather(*self._tasks)

        for page_entry in self._log.pages:
            on_content_load = page_entry.page_timings.on_content_load
            if on_content_load is not None and float(on_content_load) >= 0.0:
                page_entry.page_timings.on_content_load = float(
                    on_content_load
                ) - datetime_to_millis(page_entry.started_date_time)
            else:
                page_entry.page_timings.on_content_load = -1

            on_load = page_entry.page_timings.on_load
            if on_load is not None and float(on_load) >= 0.0:
                page_entry.page_timings.on_load = float(on_load) - datetime_to_millis(
                    page_entry.started_date_time
                )
            else:
                page_entry.page_timings.on_load = -1

        log = copy.deepcopy(self._log)
        har = dataclasses.har.Har(log=log)
        har = set_remote_ip_address_as_comment(har, self._response_received_events)
        return har
