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

        await page.goto("http://whatsmyuseragent.org/")

        har = await tracer.flush()

        await context.close()
        await browser.close()

    logger.info(har)


asyncio.run(main())
