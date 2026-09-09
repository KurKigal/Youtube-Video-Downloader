from youtube_downloader.services.compatibility import build_conversion_plan
from youtube_downloader.services.media_probe import ProbeResult, parse_fraction


def test_universal_mp4_needs_no_conversion():
    probe = ProbeResult("mov,mp4,m4a,3gp,3g2,mj2", "h264", "aac")
    assert build_conversion_plan(probe) is None


def test_webm_h264_aac_only_needs_remux():
    probe = ProbeResult("matroska,webm", "h264", "aac")
    plan = build_conversion_plan(probe)
    assert plan is not None
    assert plan.remux_only
    assert plan.video_codec == "copy"
    assert plan.audio_codec == "copy"


def test_av1_opus_needs_both_streams_converted():
    probe = ProbeResult("matroska,webm", "av1", "opus")
    plan = build_conversion_plan(probe)
    assert plan is not None
    assert plan.video_codec == "libx264"
    assert plan.audio_codec == "aac"


def test_fraction_parser():
    assert round(parse_fraction("60000/1001"), 2) == 59.94
    assert parse_fraction("0/0") is None
