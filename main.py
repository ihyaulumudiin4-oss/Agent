import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agent.api.routes import router
from agent.config import HOST, LOGS_DIR, PORT, SCREENSHOTS_DIR
from agent.core.browser import BrowserManager

# ── Logging ──────────────────────────────────────────
log_file = LOGS_DIR / "agent.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding="utf-8"),
    ],
)
logger = logging.getLogger("main")


# ── Lifespan ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Screenshot Agent V2 starting...")
    await BrowserManager.launch()
    logger.info("✅ Browser ready")
    yield
    logger.info("🛑 Shutting down...")
    await BrowserManager.close()
    logger.info("✅ Browser closed")


# ── App ──────────────────────────────────────────────
app = FastAPI(
    title="Screenshot Agent V2",
    description="AI Agent untuk screenshot website secara otomatis",
    version="2.0.0",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Files ──────────────────────────────────────
app.mount(
    "/screenshots",
    StaticFiles(directory=str(SCREENSHOTS_DIR)),
    name="screenshots",
)

# ── Routes ────────────────────────────────────────────
app.include_router(router, prefix="/api")


# ── Health ────────────────────────────────────────────
@app.get("/", tags=["health"])
async def root():
    return {
        "status": "ready",
        "agent": "Screenshot Agent V2",
        "version": "2.0.0",
    }


@app.get("/health", tags=["health"])
async def health():
    return {
        "status": "ok",
        "browser": BrowserManager.is_running(),
        "screenshots_dir": str(SCREENSHOTS_DIR),
    }


# ── Entry Point ───────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info",
    )