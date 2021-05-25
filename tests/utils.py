from contextlib import asynccontextmanager
from typing import AsyncGenerator, Tuple

from playwright.async_api import Page, async_playwright

from playwright_har_tracer import HarTracer


@asynccontextmanager
async def page_with_har_tracer() -> AsyncGenerator[Tuple[Page, HarTracer], None]:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_name = p.chromium.name

        context = await browser.new_context()
        tracer = HarTracer(context=context, browser_name=browser_name)

        page = await context.new_page()

        try:
            yield page, tracer
        finally:
            await context.close()
            await browser.close()
