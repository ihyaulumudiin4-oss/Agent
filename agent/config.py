from pathlib import Path

# ── Base Paths ──────────────────────────────────────────────
BASE_DIR        = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
LOGS_DIR        = BASE_DIR / "logs"

# Auto-create directories
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ── Server ──────────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 8000

# ── Browser ─────────────────────────────────────────────────
BROWSER_HEADLESS = True
BROWSER_TIMEOUT  = 30_000   # ms — page load timeout
DEFAULT_DELAY    = 2        # seconds — wait after load

# ── Screenshot Modes ────────────────────────────────────────
VIEWPORT_MODES = {
    "desktop":   {"width": 1920, "height": 1080},
    "mobile":    {"width": 390,  "height": 844},
    "tablet":    {"width": 768,  "height": 1024},
    "full_page": {"width": 1920, "height": 1080},
}

# ── Image ────────────────────────────────────────────────────
SUPPORTED_FORMATS = ["PNG", "JPEG", "WEBP"]
DEFAULT_FORMAT    = "PNG"
JPEG_QUALITY      = 85      # 1–100
WEBP_QUALITY      = 85

# ── File Retention ───────────────────────────────────────────
MAX_SCREENSHOTS   = 100     # max files kept in /screenshots
FILE_EXPIRE_HOURS = 24      # auto-delete after N hours