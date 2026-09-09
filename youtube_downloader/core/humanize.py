from __future__ import annotations


def format_speed(bytes_per_second: float | int | None) -> str:
    """Return a compact, ANSI-free transfer-speed label."""
    if not bytes_per_second or bytes_per_second <= 0:
        return ""
    value = float(bytes_per_second)
    units = ("B/s", "KiB/s", "MiB/s", "GiB/s")
    index = 0
    while value >= 1024.0 and index < len(units) - 1:
        value /= 1024.0
        index += 1
    if index == 0:
        return f"{value:.0f} {units[index]}"
    return f"{value:.2f} {units[index]}"


def format_eta(seconds: float | int | None) -> str:
    """Format an ETA value without relying on yt-dlp's terminal-oriented strings."""
    if seconds is None:
        return ""
    try:
        total = max(0, int(seconds))
    except (TypeError, ValueError):
        return ""

    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
