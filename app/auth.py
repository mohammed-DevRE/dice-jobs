import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

LOGIN = {"dice": "https://www.dice.com/dashboard/login", "linkedin": "https://www.linkedin.com/login"}


async def main(source):
    if source not in LOGIN:
        raise SystemExit("Use: python -m app.auth dice|linkedin")
    target = Path(f"/data/auth/{source}.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(LOGIN[source])
        input("Complete login in the browser, then press Enter here: ")
        await context.storage_state(path=str(target))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else ""))

