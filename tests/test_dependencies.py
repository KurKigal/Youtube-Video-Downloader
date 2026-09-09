import os
import tempfile
from pathlib import Path

from youtube_downloader.services.dependencies import DependencyService


def test_user_bin_is_under_localappdata_on_windows(monkeypatch):
    if os.name != "nt":
        return
    monkeypatch.setenv("LOCALAPPDATA", r"C:\\Users\\Test\\AppData\\Local")
    assert str(DependencyService.user_bin_dir()).endswith(r"YouTube-Downloader-V2\bin")


def test_find_executable_prefers_candidate_bin(monkeypatch):
    # Use the project directory rather than pytest's system temp fixture so this
    # test also works on Windows machines with a locked %TEMP%/pytest-of-user dir.
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
        root = Path(tmp)
        binary_name = "deno.exe" if os.name == "nt" else "deno"
        binary = root / binary_name
        binary.write_bytes(b"placeholder")
        monkeypatch.setattr(DependencyService, "candidate_bin_dirs", classmethod(lambda cls: [root]))
        assert DependencyService.find_executable("deno") == str(binary)
