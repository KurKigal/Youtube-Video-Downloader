from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DependencyStatus:
    name: str
    available: bool
    version: str = ""
    path: str = ""
    required: bool = True
    hint: str = ""


class DependencyService:
    def check_all(self) -> list[DependencyStatus]:
        return [
            self._check_python_package("yt-dlp", "yt_dlp", required=True),
            self._check_python_package("yt-dlp-ejs", "yt_dlp_ejs", required=True),
            self._check_executable("FFmpeg", "ffmpeg", required=True),
            self._check_executable("FFprobe", "ffprobe", required=True),
            self._check_executable(
                "Deno",
                "deno",
                required=True,
                hint="YouTube formatlarının eksiksiz çözümlenmesi için Deno 2.3+ önerilir.",
            ),
        ]

    def deno_path(self) -> str | None:
        return self._find_executable("deno")

    def ffmpeg_path(self) -> str | None:
        return self._find_executable("ffmpeg")

    def ffprobe_path(self) -> str | None:
        return self._find_executable("ffprobe")

    @staticmethod
    def _candidate_bin_dirs() -> list[Path]:
        dirs: list[Path] = []
        if getattr(sys, "frozen", False):
            dirs.extend([Path(sys.executable).resolve().parent / "bin", Path(sys.executable).resolve().parent])
        else:
            project_root = Path(__file__).resolve().parents[2]
            dirs.extend([project_root / "bin", project_root])
        return dirs

    @classmethod
    def _find_executable(cls, command: str) -> str | None:
        suffix = ".exe" if os.name == "nt" else ""
        executable_name = command if command.endswith(suffix) else f"{command}{suffix}"

        # Prefer a release-local bin directory so a portable package can be used
        # without changing the user's global PATH. Fall back to normal PATH lookup.
        for directory in cls._candidate_bin_dirs():
            candidate = directory / executable_name
            if candidate.is_file():
                return str(candidate)
        return shutil.which(command)

    @classmethod
    def _check_executable(cls, name: str, command: str, required: bool, hint: str = "") -> DependencyStatus:
        path = cls._find_executable(command)
        if not path:
            return DependencyStatus(name, False, required=required, hint=hint)
        try:
            completed = subprocess.run(
                [path, "--version"], capture_output=True, text=True, timeout=5, check=False
            )
            first_line = (completed.stdout or completed.stderr).strip().splitlines()
            version = first_line[0] if first_line else ""
        except Exception:
            version = ""
        return DependencyStatus(name, True, version=version, path=str(Path(path)), required=required, hint=hint)

    @staticmethod
    def _check_python_package(name: str, module: str, required: bool) -> DependencyStatus:
        spec = importlib.util.find_spec(module)
        if spec is None:
            return DependencyStatus(name, False, required=required)
        version = ""
        try:
            from importlib.metadata import version as package_version
            version = package_version(name)
        except Exception:
            pass
        return DependencyStatus(name, True, version=version, required=required)
