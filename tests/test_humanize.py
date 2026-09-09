from youtube_downloader.core.humanize import format_eta, format_speed


def test_format_speed_is_human_readable_and_clean():
    assert format_speed(1_048_576) == "1.00 MiB/s"
    assert "\x1b" not in format_speed(2_500_000)


def test_format_speed_empty_for_missing_value():
    assert format_speed(None) == ""
    assert format_speed(0) == ""


def test_format_eta_short_and_long():
    assert format_eta(86) == "01:26"
    assert format_eta(3723) == "1:02:03"


def test_format_eta_empty_for_invalid_value():
    assert format_eta(None) == ""
