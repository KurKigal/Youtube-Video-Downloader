from pathlib import Path

from youtube_downloader.services.dependencies import DependencyService


def test_find_executable_can_use_project_local_bin(monkeypatch, tmp_path: Path):
    binary = tmp_path / ("deno.exe" if __import__("os").name == "nt" else "deno")
    binary.write_bytes(b"placeholder")

    monkeypatch.setattr(DependencyService, "_candidate_bin_dirs", staticmethod(lambda: [tmp_path]))
    assert DependencyService._find_executable("deno") == str(binary)
