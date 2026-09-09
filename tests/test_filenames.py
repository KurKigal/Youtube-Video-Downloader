from youtube_downloader.core.filenames import sanitize_display_filename


def test_reserved_windows_name_is_prefixed():
    assert sanitize_display_filename("CON") == "_CON"


def test_unicode_is_preserved():
    assert sanitize_display_filename("Türkçe 日本語 🎵") == "Türkçe 日本語 🎵"


def test_invalid_characters_are_removed():
    assert sanitize_display_filename('a<b>:c"d/e\\f|g?h*i') == "abcdefghi"
