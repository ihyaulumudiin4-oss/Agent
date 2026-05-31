import asyncio
import logging
import uuid

from agent.config import (
    BROWSER_TIMEOUT,
    JPEG_QUALITY,
    SCREENSHOTS_DIR,
    VIEWPORT_MODES,
    WEBP_QUALITY,
)
from agent.core.browser import BrowserManager

logger = logging.getLogger("screenshot")

USER_AGENTS = {
    "mobile": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "tablet": (
        "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ),
}


async def take_screenshot(
    url: str,
    mode: str = "desktop",
    fmt: str = "PNG",
    delay: int = 2,
    full_page: bool = False,
) -> dict:
    """
    Ambil screenshot website.

    Returns:
        {
            file_id    : str,
            file_path  : Path,
            filename   : str,
            mode       : str,
            format     : str,
            width      : int,
            height     : int,
        }
    """
    viewport   = VIEWPORT_MODES.get(mode, VIEWPORT_MODES["desktop"])
    user_agent = USER_AGENTS.get(mode)
    is_full    = full_page or mode == "full_page"

    file_id  = str(uuid.uuid4())
    ext      = "jpg" if fmt.upper() == "JPEG" else fmt.lower()
    filename = f"{file_id}.{ext}"
    file_path = SCREENSHOTS_DIR / filename

    context = await BrowserManager.new_context(viewport, user_agent)

    try:
        page = await context.new_page()
        page.set_default_timeout(BROWSER_TIMEOUT)

        logger.info(f"[{file_id}] Navigating → {url}")
        await page.goto(url, wait_until="networkidle")

        if delay > 0:
            logger.info(f"[{file_id}] Waiting {delay}s...")
            await asyncio.sleep(delay)

        # ── Screenshot options ────────────────────────
        opts = {
            "path":      str(file_path),
            "full_page": is_full,
            "type":      fmt.lower(),
        }
        if fmt.upper() == "JPEG":
            opts["quality"] = JPEG_QUALITY
        elif fmt.upper() == "WEBP":
            opts["quality"] = WEBP_QUALITY

        await page.screenshot(**opts)

        # ── Actual dimensions ─────────────────────────
        size = await page.evaluate("""() => ({
            width:  document.body.scrollWidth,
            height: document.body.scrollHeight,
        })""")

        logger.info(f"[{file_id}] Saved → {filename} ({size['width']}×{size['height']})")

        return {
            "file_id":   file_id,
            "file_path": file_path,
            "filename":  filename,
            "mode":      mode,
            "format":    fmt.upper(),
            "width":     size["width"],
            "height":    size["height"],
        }

    except Exception as e:
        logger.error(f"[{file_id}] Failed: {e}")
        # Hapus file gagal jika terbuat
        if file_path.exists():
            file_path.unlink()
        raise

    finally:
        await context.close()