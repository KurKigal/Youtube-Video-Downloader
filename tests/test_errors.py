from youtube_downloader.core.errors import ErrorCode, classify_error


def test_js_runtime_error_is_classified():
    result = classify_error("No supported JavaScript runtime could be found")
    assert result.code is ErrorCode.JS_RUNTIME


def test_format_unavailable_is_classified():
    result = classify_error("Requested format is not available")
    assert result.code is ErrorCode.FORMAT_UNAVAILABLE


def test_unknown_error_keeps_technical_message():
    result = classify_error("Something entirely new happened")
    assert result.code is ErrorCode.UNKNOWN
    assert "Something entirely new" in result.technical_message


def test_missing_ffprobe_is_repairable_component_error():
    result = classify_error("FFprobe bulunamadı")
    assert result.code is ErrorCode.MEDIA_COMPONENT_MISSING


def test_runtime_ffmpeg_failure_is_not_missing_component():
    result = classify_error("FFmpeg uyumluluk dönüşümü başarısız: encoder failed")
    assert result.code is ErrorCode.FFMPEG


def test_cancelled_is_separate_terminal_state():
    result = classify_error("Download cancelled by user")
    assert result.code is ErrorCode.CANCELLED
