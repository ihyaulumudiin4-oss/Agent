from pydantic import BaseModel, Field, field_validator
from typing import Literal


# ── Request ───────────────────────────────────────────────
class ScreenshotRequest(BaseModel):
    url:       str                                          = Field(..., example="https://github.com")
    mode:      Literal["desktop", "mobile", "tablet", "full_page"] = "desktop"
    format:    Literal["PNG", "JPEG", "WEBP"]              = "PNG"
    delay:     int                                          = Field(default=2, ge=0, le=10)
    full_page: bool                                         = False

    @field_validator("url")
    @classmethod
    def url_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("URL tidak boleh kosong")
        return v.strip()


# ── Response ──────────────────────────────────────────────
class ScreenshotResponse(BaseModel):
    status:       str
    file_id:      str
    image_url:    str
    filename:     str
    mode:         str
    format:       str
    width:        int
    height:       int
    file_size_kb: float


# ── History ───────────────────────────────────────────────
class HistoryItem(BaseModel):
    file_id:      str
    filename:     str
    image_url:    str
    file_size_kb: float


# ── Error ─────────────────────────────────────────────────
class ErrorResponse(BaseModel):
    status:  str = "error"
    message: str