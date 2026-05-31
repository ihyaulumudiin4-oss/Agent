import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger("validator")

BLOCKED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
}

DOMAIN_PATTERN = re.compile(
    r"^(?:[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,}$"
)


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validasi URL sebelum diproses agent.

    Returns:
        (True, "")            — valid
        (False, "pesan error") — tidak valid
    """
    url = url.strip()

    if not url:
        return False, "URL tidak boleh kosong"

    # Auto-prefix scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Parse
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "URL tidak dapat di-parse"

    # Scheme
    if parsed.scheme not in ("http", "https"):
        return False, "Scheme harus http atau https"

    # Netloc
    if not parsed.netloc:
        return False, "URL tidak memiliki domain"

    # Host
    host = parsed.hostname or ""

    if not host:
        return False, "Host tidak ditemukan"

    if host in BLOCKED_HOSTS:
        return False, f"Host '{host}' tidak diizinkan"

    # IP address — izinkan publik, blokir private
    if _is_private_ip(host):
        return False, f"IP private '{host}' tidak diizinkan"

    # Domain format (skip jika IP publik)
    if not _is_ip(host) and not DOMAIN_PATTERN.match(host):
        return False, f"Format domain tidak valid: '{host}'"

    logger.info(f"URL valid: {url}")
    return True, ""


def normalize_url(url: str) -> str:
    """Tambah scheme jika belum ada."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


# ── Helpers ───────────────────────────────────────────────


def _is_ip(host: str) -> bool:
    import socket
    try:
        socket.inet_aton(host)
        return True
    except OSError:
        return False


def _is_private_ip(host: str) -> bool:
    import ipaddress
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return False  # bukan IP, berarti domain