import asyncio

from loguru import logger
from playwright.async_api import async_playwright

from playwright_har_tracer import HarTracer


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        tracer = HarTracer(context=context, browser_name=p.chromium.name)

        page = await context.new_page()
        client = await context.new_cdp_session(page)
        # enable Network.responseReceived event tracking
        # https://chromedevtools.github.io/devtools-protocol/tot/Network/#event-responseReceived
        await tracer.enable_response_received_event_tracing(client)

        await page.goto("http://whatsmyuseragent.org/")

        har = await tracer.flush()

        await context.close()
        await browser.close()

    # Network.responseReceived events are used to enrich HAR
    # (Network.Response's remoteIPAddress is set as a comment)
    for entry in har.log.entries:
        logger.info(entry.request.url)
        logger.info(entry.response.comment)


asyncio.run(main())
