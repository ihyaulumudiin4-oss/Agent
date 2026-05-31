import logging
import time
from pathlib import Path

from agent.config import FILE_EXPIRE_HOURS, MAX_SCREENSHOTS, SCREENSHOTS_DIR

logger = logging.getLogger("file_manager")


def cleanup_old_files() -> int:
    """
    Hapus file yang sudah melewati FILE_EXPIRE_HOURS.
    Returns jumlah file yang dihapus.
    """
    now            = time.time()
    expire_seconds = FILE_EXPIRE_HOURS * 3600
    deleted        = 0

    for f in SCREENSHOTS_DIR.glob("*.*"):
        age = now - f.stat().st_mtime
        if age > expire_seconds:
            f.unlink()
            deleted += 1
            logger.info(f"Deleted (expired): {f.name}")

    logger.info(f"Cleanup done — {deleted} file(s) removed")
    return deleted


def enforce_max_files() -> int:
    """
    Hapus file terlama jika jumlah melebihi MAX_SCREENSHOTS.
    Returns jumlah file yang dihapus.
    """
    files  = sorted(
        SCREENSHOTS_DIR.glob("*.*"),
        key=lambda f: f.stat().st_mtime,
    )
    excess  = len(files) - MAX_SCREENSHOTS
    deleted = 0

    if excess > 0:
        for f in files[:excess]:
            f.unlink()
            deleted += 1
            logger.info(f"Deleted (max limit): {f.name}")

    return deleted


def get_storage_info() -> dict:
    """Info penggunaan storage folder screenshots."""
    files      = list(SCREENSHOTS_DIR.glob("*.*"))
    total_size = sum(f.stat().st_size for f in files)

    return {
        "total_files":   len(files),
        "total_size_kb": round(total_size / 1024, 2),
        "total_size_mb": round(total_size / 1024 / 1024, 2),
        "max_files":     MAX_SCREENSHOTS,
        "expire_hours":  FILE_EXPIRE_HOURS,
    }


def delete_file(file_id: str) -> bool:
    """
    Hapus file berdasarkan file_id (tanpa ekstensi).
    Returns True jika berhasil, False jika tidak ditemukan.
    """
    matches = list(SCREENSHOTS_DIR.glob(f"{file_id}.*"))
    if not matches:
        return False
    for f in matches:
        f.unlink()
        logger.info(f"Deleted: {f.name}")
    return True