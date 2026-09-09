from __future__ import annotations

import requests


def fetch_thumbnail(url: str | None) -> bytes | None:
    if not url:
        return None
    try:
        response = requests.get(url, timeout=(5, 10))
        response.raise_for_status()
        if len(response.content) > 8 * 1024 * 1024:
            return None
        return response.content
    except requests.RequestException:
        return None
