from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProbeResult:
    container: str
    video_codec: str | None
    audio_codec: str | None
    width: int | None = None
    height: int | None = None
    fps: float | None = None

    @property
    def is_universal_mp4(self) -> bool:
        is_mp4 = "mp4" in self.container.lower()
        video_ok = self.video_codec in {None, "h264"}
        audio_ok = self.audio_codec in {None, "aac"}
        return is_mp4 and video_ok and audio_ok


def parse_fraction(value: str | None) -> float | None:
    if not value or value in {"0/0", "N/A"}:
        return None
    try:
        if "/" in value:
            numerator, denominator = value.split("/", 1)
            denominator_f = float(denominator)
            return float(numerator) / denominator_f if denominator_f else None
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


class MediaProbeService:
    def __init__(self, ffprobe_path: str | None):
        self.ffprobe_path = ffprobe_path

    def probe(self, path: Path) -> ProbeResult:
        if not self.ffprobe_path:
            raise RuntimeError("FFprobe bulunamadı")
        completed = subprocess.run(
            [
                self.ffprobe_path,
                "-v", "error",
                "-show_entries", "format=format_name:stream=codec_type,codec_name,width,height,avg_frame_rate",
                "-of", "json",
                str(path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or "FFprobe dosyayı okuyamadı")
        payload = json.loads(completed.stdout or "{}")
        video = next((s for s in payload.get("streams", []) if s.get("codec_type") == "video"), {})
        audio = next((s for s in payload.get("streams", []) if s.get("codec_type") == "audio"), {})
        return ProbeResult(
            container=(payload.get("format") or {}).get("format_name") or "",
            video_codec=video.get("codec_name"),
            audio_codec=audio.get("codec_name"),
            width=video.get("width"),
            height=video.get("height"),
            fps=parse_fraction(video.get("avg_frame_rate")),
        )
