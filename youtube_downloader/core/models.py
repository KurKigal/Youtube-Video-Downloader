from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class MediaType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"


class VideoProfile(str, Enum):
    COMPATIBLE_MP4 = "compatible_mp4"
    BEST_QUALITY = "best_quality"
    ORIGINAL = "original"


class AudioFormat(str, Enum):
    BEST = "best"
    MP3 = "mp3"
    M4A = "m4a"
    OPUS = "opus"
    WAV = "wav"
    FLAC = "flac"


@dataclass(frozen=True, slots=True)
class QualityOption:
    height: int | None
    fps: float | None = None
    hdr: str | None = None

    @property
    def label(self) -> str:
        if self.height is None:
            return "En iyi kalite"
        parts = [f"{self.height}p’ye kadar"]
        if self.fps and self.fps >= 50:
            parts.append(f"{round(self.fps)} FPS")
        if self.hdr and self.hdr.upper() not in {"SDR", "NONE"}:
            parts.append(self.hdr.upper())
        return " · ".join(parts)


@dataclass(slots=True)
class MediaEntry:
    id: str
    url: str
    title: str
    uploader: str = ""
    duration: float | None = None
    thumbnail: str | None = None
    is_live: bool = False
    availability: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True)
class AnalysisResult:
    source_url: str
    title: str
    is_playlist: bool
    entries: list[MediaEntry]
    qualities: list[QualityOption]
    thumbnail: str | None = None
    uploader: str = ""
    duration: float | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class DownloadRequest:
    url: str
    output_dir: Path
    media_type: MediaType
    quality_height: int | None = None
    video_profile: VideoProfile = VideoProfile.COMPATIBLE_MP4
    audio_format: AudioFormat = AudioFormat.MP3
    browser_cookies: str | None = None


@dataclass(slots=True)
class DownloadProgress:
    status: str
    percent: float = 0.0
    speed: str = ""
    eta: str = ""
    filename: str = ""


@dataclass(slots=True)
class DownloadResult:
    success: bool
    title: str
    output_path: Path | None = None
    error_code: str | None = None
    error_message: str | None = None
    error_detail: str | None = None
