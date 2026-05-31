import logging
from pathlib import Path

from PIL import Image

logger = logging.getLogger("image_processor")


def compress_image(file_path: Path, quality: int = 85) -> Path:
    """
    Compress gambar in-place.
    PNG dilewati (lossless), JPEG & WEBP di-compress.
    """
    img = Image.open(file_path)
    fmt = (img.format or file_path.suffix.upper().lstrip(".")).upper()

    if fmt in ("JPEG", "JPG", "WEBP"):
        img.save(file_path, format=fmt, quality=quality, optimize=True)
        logger.info(f"Compressed: {file_path.name} (quality={quality})")
    else:
        logger.info(f"Skipped compress (PNG): {file_path.name}")

    return file_path


def get_image_info(file_path: Path) -> dict:
    """Ambil metadata gambar."""
    img = Image.open(file_path)
    return {
        "width":  img.width,
        "height": img.height,
        "format": img.format,
        "mode":   img.mode,
    }


def resize_image(
    file_path: Path,
    max_width: int = 1920,
    max_height: int = 1080,
) -> Path:
    """
    Resize gambar jika melebihi batas max.
    Aspect ratio tetap terjaga.
    """
    img = Image.open(file_path)
    img.thumbnail((max_width, max_height), Image.LANCZOS)
    img.save(file_path)
    logger.info(f"Resized: {file_path.name} → {img.width}×{img.height}")
    return file_path