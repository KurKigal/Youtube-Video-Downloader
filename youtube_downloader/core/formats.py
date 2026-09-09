from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .models import AudioFormat, DownloadRequest, MediaType, QualityOption, VideoProfile


COMMON_HEIGHTS = (144, 240, 360, 480, 720, 1080, 1440, 2160, 4320)


def quality_options_from_formats(formats: Iterable[dict]) -> list[QualityOption]:
    """Create stable, human-friendly quality choices from extractor formats.

    Multiple codecs/containers with the same resolution are intentionally collapsed.
    The backend resolves the best concrete stream at download time for each video.
    """
    grouped: dict[int, dict[str, object]] = defaultdict(lambda: {"fps": 0.0, "hdr": None})

    for fmt in formats:
        if fmt.get("vcodec") in (None, "none"):
            continue
        height = fmt.get("height")
        if not isinstance(height, (int, float)) or height < 100:
            continue

        height_i = int(height)
        fps = float(fmt.get("fps") or 0.0)
        dynamic_range = fmt.get("dynamic_range") or fmt.get("hdr")

        if fps > float(grouped[height_i]["fps"] or 0.0):
            grouped[height_i]["fps"] = fps
        if dynamic_range and str(dynamic_range).upper() not in {"SDR", "NONE"}:
            grouped[height_i]["hdr"] = str(dynamic_range)

    result = [QualityOption(height=None)]
    for height in sorted(grouped, reverse=True):
        result.append(
            QualityOption(
                height=height,
                fps=float(grouped[height]["fps"] or 0.0) or None,
                hdr=grouped[height]["hdr"] and str(grouped[height]["hdr"]),
            )
        )
    return result


def build_format_selector(request: DownloadRequest) -> str:
    if request.media_type is MediaType.AUDIO:
        return "ba/b"

    height_filter = "" if request.quality_height is None else f"[height<=?{request.quality_height}]"
    fallback_height = "" if request.quality_height is None else f"[height<=?{request.quality_height}]"

    if request.video_profile is VideoProfile.COMPATIBLE_MP4:
        # Prefer AVC/H.264 video + M4A/AAC audio for broad device compatibility.
        # Fall back progressively instead of failing when YouTube does not expose AVC.
        return (
            f"bv*{height_filter}[vcodec^=avc1]+ba[ext=m4a]/"
            f"bv*{height_filter}[ext=mp4]+ba[ext=m4a]/"
            f"bv*{height_filter}+ba/"
            f"b{fallback_height}"
        )

    # BEST_QUALITY and ORIGINAL both preserve source codecs. ORIGINAL is kept as a
    # separate product-level profile so its post-processing policy can diverge later.
    return f"bv*{height_filter}+ba/b{fallback_height}"


def build_postprocessors(request: DownloadRequest) -> list[dict]:
    if request.media_type is not MediaType.AUDIO:
        return []
    if request.audio_format is AudioFormat.BEST:
        return []

    codec = request.audio_format.value
    preferred_quality = "192" if codec == "mp3" else "0"
    return [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": codec,
            "preferredquality": preferred_quality,
        }
    ]


def expected_extension(request: DownloadRequest) -> str | None:
    if request.media_type is MediaType.AUDIO:
        return None if request.audio_format is AudioFormat.BEST else request.audio_format.value
    if request.video_profile is VideoProfile.COMPATIBLE_MP4:
        return "mp4"
    return None
