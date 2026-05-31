import logging
from playwright.async_api import async_playwright, Browser, Playwright

logger = logging.getLogger("browser")


class BrowserManager:
    _playwright: Playwright = None
    _browser: Browser = None

    @classmethod
    async def launch(cls):
        cls._playwright = await async_playwright().start()
        cls._browser = await cls._playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
            ],
        )
        logger.info("Browser launched")

    @classmethod
    async def close(cls):
        if cls._browser:
            await cls._browser.close()
            cls._browser = None
        if cls._playwright:
            await cls._playwright.stop()
            cls._playwright = None
        logger.info("Browser closed")

    @classmethod
    def is_running(cls) -> bool:
        return cls._browser is not None and cls._browser.is_connected()

    @classmethod
    async def new_context(cls, viewport: dict, user_agent: str = None):
        options = {"viewport": viewport}
        if user_agent:
            options["user_agent"] = user_agent
        return await cls._browser.new_context(**options)