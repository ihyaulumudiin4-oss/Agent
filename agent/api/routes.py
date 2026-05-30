import logging
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from agent.api.schemas import (
    ErrorResponse,
    HistoryItem,
    ScreenshotRequest,
    ScreenshotResponse,
)
from agent.config import SCREENSHOTS_DIR
from agent.core.screenshot import take_screenshot
from agent.core.validator import normalize_url, validate_url

logger = logging.getLogger("routes")
router = APIRouter()


# ── POST /screenshot ──────────────────────────────────────
@router.post(
    "/screenshot",
    response_model=ScreenshotResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["screenshot"],
)
async def create_screenshot(req: ScreenshotRequest):
    # Validasi URL
    is_valid, error = validate_url(req.url)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    url = normalize_url(req.url)

    try:
        result = await take_screenshot(
            url=url,
            mode=req.mode,
            fmt=req.format,
            delay=req.delay,
            full_page=req.full_page,
        )
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal screenshot: {str(e)}")

    file_path = result["file_path"]
    file_size_kb = round(file_path.stat().st_size / 1024, 2)

    return ScreenshotResponse(
        status="success",
        file_id=result["file_id"],
        image_url=f"/screenshots/{result['filename']}",
        filename=result["filename"],
        mode=result["mode"],
        format=result["format"],
        width=result["width"],
        height=result["height"],
        file_size_kb=file_size_kb,
    )


# ── GET /history ──────────────────────────────────────────
@router.get(
    "/history",
    response_model=list[HistoryItem],
    tags=["screenshot"],
)
async def get_history():
    files = sorted(
        SCREENSHOTS_DIR.glob("*.*"),
        key=os.path.getmtime,
        reverse=True,
    )
    return [
        HistoryItem(
            file_id=f.stem,
            filename=f.name,
            image_url=f"/screenshots/{f.name}",
            file_size_kb=round(f.stat().st_size / 1024, 2),
        )
        for f in files
    ]


# ── GET /screenshot/{file_id} ─────────────────────────────
@router.get(
    "/screenshot/{file_id}",
    tags=["screenshot"],
)
async def get_screenshot(file_id: str):
    matches = list(SCREENSHOTS_DIR.glob(f"{file_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="File tidak ditemukan")
    return FileResponse(str(matches[0]))


# ── DELETE /screenshot/{file_id} ──────────────────────────
@router.delete(
    "/screenshot/{file_id}",
    tags=["screenshot"],
)
async def delete_screenshot(file_id: str):
    matches = list(SCREENSHOTS_DIR.glob(f"{file_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="File tidak ditemukan")
    for f in matches:
        f.unlink()
    logger.info(f"Deleted: {file_id}")
    return {"status": "deleted", "file_id": file_id}