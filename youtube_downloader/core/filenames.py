from __future__ import annotations

import re

WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def sanitize_display_filename(value: str, fallback: str = "video", max_chars: int = 160) -> str:
    """Sanitize a title for display/custom paths while preserving Unicode."""
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", value).strip().rstrip(". ")
    if not value:
        value = fallback
    stem = value.split(".", 1)[0].upper()
    if stem in WINDOWS_RESERVED:
        value = f"_{value}"
    if len(value) > max_chars:
        value = value[:max_chars].rstrip(". ")
    return value or fallback
