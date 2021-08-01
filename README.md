# playwright-har-tracer

[![PyPI version](https://badge.fury.io/py/playwright-har-tracer.svg)](https://badge.fury.io/py/playwright-har-tracer)
[![Python CI](https://github.com/ninoseki/playwright-har-tracer/actions/workflows/test.yml/badge.svg)](https://github.com/ninoseki/playwright-har-tracer/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/ninoseki/playwright-har-tracer/badge.svg?branch=main)](https://coveralls.io/github/ninoseki/playwright-har-tracer?branch=main)

A Python implementation version of Playwright's HAR tracer.
It is equivalent to playwright `v0.13.x`’s HAR tracer implementation.

## Motivation

Playwright's HAR tracer is implemented to generate HAR as a file. I need to get HAR as a Python object rather than a file.

- `playwright-har-tracer`'s HarTracer generates HAR as a dataclass object.

## ⚠️ Limitations

- Tested with Python 3.8+
- Tested with Chromium only
- Supports the async API only

## Installation

```bash
pip install playwright-har-tracer
```

## Usage

```python
import asyncio
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

    print(har.to_json())


asyncio.run(main())
```
