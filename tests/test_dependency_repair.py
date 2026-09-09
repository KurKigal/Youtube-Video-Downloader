import tempfile
from pathlib import Path

import youtube_downloader.services.dependency_repair as repair_module
from youtube_downloader.services.dependency_repair import DependencyRepairService


class FakeResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        return None


def test_checksum_parser_accepts_standard_sha256(monkeypatch):
    expected = "a" * 64
    monkeypatch.setattr(repair_module.requests, "get", lambda *args, **kwargs: FakeResponse(f"{expected}  file.zip\n"))
    assert DependencyRepairService._fetch_checksum("https://example.test/checksum") == expected


def test_find_file_locates_nested_executable():
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
        root = Path(tmp)
        nested = root / "package" / "bin"
        nested.mkdir(parents=True)
        target = nested / "ffprobe.exe"
        target.write_bytes(b"x")
        assert DependencyRepairService._find_file(root, "ffprobe.exe") == target


def test_deno_architecture_x64(monkeypatch):
    monkeypatch.setattr(repair_module.platform, "machine", lambda: "AMD64")
    assert DependencyRepairService._deno_architecture() == "x86_64"
