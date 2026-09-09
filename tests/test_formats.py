from pathlib import Path

from youtube_downloader.core.formats import build_format_selector, quality_options_from_formats
from youtube_downloader.core.models import DownloadRequest, MediaType, VideoProfile


def test_quality_options_deduplicate_resolution_and_keep_best_fps():
    formats = [
        {"vcodec": "avc1", "height": 1080, "fps": 30, "dynamic_range": "SDR"},
        {"vcodec": "vp9", "height": 1080, "fps": 60, "dynamic_range": "SDR"},
        {"vcodec": "av01", "height": 2160, "fps": 60, "dynamic_range": "HDR10"},
        {"vcodec": "none", "height": None, "fps": None},
    ]

    options = quality_options_from_formats(formats)

    assert [item.height for item in options] == [None, 2160, 1080]
    assert options[1].label == "2160p’ye kadar · 60 FPS · HDR10"
    assert options[2].label == "1080p’ye kadar · 60 FPS"


def test_compatible_selector_has_progressive_fallbacks():
    req = DownloadRequest(
        url="https://example.com",
        output_dir=Path("."),
        media_type=MediaType.VIDEO,
        quality_height=1080,
        video_profile=VideoProfile.COMPATIBLE_MP4,
    )

    selector = build_format_selector(req)

    assert "height<=?1080" in selector
    assert "vcodec^=avc1" in selector
    assert "+ba" in selector
    assert selector.count("/") >= 3


def test_best_quality_does_not_force_container_or_codec():
    req = DownloadRequest(
        url="https://example.com",
        output_dir=Path("."),
        media_type=MediaType.VIDEO,
        quality_height=None,
        video_profile=VideoProfile.BEST_QUALITY,
    )
    assert build_format_selector(req) == "bv*+ba/b"
