from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


APP_DIR_NAME = "YouTube-Downloader-V2"


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
                hint="YouTube formatlarının eksiksiz çözümlenmesi için Deno gerekir.",
            ),
        ]

    @staticmethod
    def user_data_dir() -> Path:
        if os.name == "nt":
            root = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
            return root / APP_DIR_NAME
        root = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
        return root / APP_DIR_NAME

    @classmethod
    def user_bin_dir(cls) -> Path:
        return cls.user_data_dir() / "bin"

    @staticmethod
    def release_bin_dirs() -> list[Path]:
        dirs: list[Path] = []
        if getattr(sys, "frozen", False):
            exe_dir = Path(sys.executable).resolve().parent
            dirs.extend([exe_dir / "bin", exe_dir])
        else:
            project_root = Path(__file__).resolve().parents[2]
            dirs.extend([project_root / "bin", project_root])
        return dirs

    @classmethod
    def candidate_bin_dirs(cls) -> list[Path]:
        # User-local repaired components take priority, then portable release-local
        # components, then the system PATH.
        return [cls.user_bin_dir(), *cls.release_bin_dirs()]

    @classmethod
    def find_executable(cls, command: str) -> str | None:
        suffix = ".exe" if os.name == "nt" else ""
        executable_name = command if command.endswith(suffix) else f"{command}{suffix}"
        for directory in cls.candidate_bin_dirs():
            candidate = directory / executable_name
            if candidate.is_file():
                return str(candidate)
        return shutil.which(command)

    def deno_path(self) -> str | None:
        return self.find_executable("deno")

    def ffmpeg_path(self) -> str | None:
        return self.find_executable("ffmpeg")

    def ffprobe_path(self) -> str | None:
        return self.find_executable("ffprobe")

    @staticmethod
    def version_args(command: str) -> tuple[str, ...]:
        """Return the version flag expected by each runtime.

        FFmpeg and FFprobe use the single-dash ``-version`` option, while Deno
        uses the conventional ``--version`` option. Treating them all the same
        caused valid FFmpeg installations to be reported as missing.
        """
        stem = Path(command).stem.lower()
        if stem in {"ffmpeg", "ffprobe"}:
            return ("-version",)
        return ("--version",)

    @classmethod
    def _check_executable(cls, name: str, command: str, required: bool, hint: str = "") -> DependencyStatus:
        path = cls.find_executable(command)
        if not path:
            return DependencyStatus(name, False, required=required, hint=hint)
        try:
            completed = subprocess.run(
                [path, *cls.version_args(command)],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            first_line = (completed.stdout or completed.stderr).strip().splitlines()
            version = first_line[0] if first_line else ""
            available = completed.returncode == 0
        except Exception:
            version = ""
            available = False
        return DependencyStatus(name, available, version=version, path=str(Path(path)), required=required, hint=hint)

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
