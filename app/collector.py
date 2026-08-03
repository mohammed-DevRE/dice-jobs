import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from playwright.async_api import async_playwright

from .db import add_job, log_run

SOURCES = {
    "dice": (Path("config/dice_urls.txt"), ("dice.com/job-detail", "dice.com/jobs/detail")),
    "linkedin": (Path("config/linkedin_urls.txt"), ("linkedin.com/jobs/view",)),
}


def normalize_url(url):
    parts = urlsplit(url)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", ""))


def configured_urls(path):
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.startswith("#")]


async def collect_source(source):
    path, patterns = SOURCES[source]
    urls = configured_urls(path)
    if not urls:
        log_run(source, "skipped", "No search URLs configured")
        return
    auth = Path(f"/data/auth/{source}.json")
    if not auth.exists():
        log_run(source, "blocked", "Authenticated browser state is missing")
        return
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=os.getenv("HEADLESS", "true").lower() == "true")
            context = await browser.new_context(storage_state=str(auth))
            page = await context.new_page()
            for search_url in urls:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                body = (await page.locator("body").inner_text()).lower()
                if any(term in body for term in ("captcha", "security verification", "verify you are human", "sign in to continue")):
                    log_run(source, "blocked", "Login or security verification required")
                    await browser.close()
                    return
                for anchor in await page.locator("a[href]").all():
                    href = await anchor.get_attribute("href") or ""
                    if not any(pattern in href for pattern in patterns):
                        continue
                    title = (await anchor.inner_text()).strip() or "Untitled job"
                    add_job(source, title, "", normalize_url(href))
            await browser.close()
        log_run(source, "success")
    except Exception as exc:
        log_run(source, "error", f"{type(exc).__name__}: {exc}")


async def collect_all():
    for source in SOURCES:
        await collect_source(source)

