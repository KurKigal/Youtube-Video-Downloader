from __future__ import annotations

import hashlib
import os
import platform
import re
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import requests

from youtube_downloader.services.dependencies import DependencyService


FFMPEG_ARCHIVE_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_CHECKSUM_URL = FFMPEG_ARCHIVE_URL + ".sha256"
DENO_RELEASE_BASE = "https://github.com/denoland/deno/releases/latest/download"


@dataclass(frozen=True, slots=True)
class RepairProgress:
    component: str
    message: str
    percent: int


@dataclass(frozen=True, slots=True)
class RepairResult:
    success: bool
    installed: tuple[str, ...]
    failed: tuple[str, ...]
    details: str = ""


class DependencyRepairService:
    def __init__(self, dependencies: DependencyService | None = None):
        self.dependencies = dependencies or DependencyService()

    def repair(
        self,
        components: set[str],
        on_progress: Callable[[RepairProgress], None] | None = None,
    ) -> RepairResult:
        if os.name != "nt":
            return RepairResult(False, (), tuple(sorted(components)), "Otomatik kurulum şu anda yalnız Windows'ta destekleniyor.")

        requested = set(components)
        installed: list[str] = []
        failed: list[str] = []
        details: list[str] = []

        try:
            if requested.intersection({"FFmpeg", "FFprobe"}):
                self._install_ffmpeg(on_progress)
                installed.extend(["FFmpeg", "FFprobe"])
        except Exception as exc:
            failed.extend([name for name in ("FFmpeg", "FFprobe") if name in requested or requested.intersection({"FFmpeg", "FFprobe"})])
            details.append(f"FFmpeg/FFprobe: {exc}")

        if "Deno" in requested:
            try:
                self._install_deno(on_progress)
                installed.append("Deno")
            except Exception as exc:
                failed.append("Deno")
                details.append(f"Deno: {exc}")

        # Verify actual executability after writing files.
        status = {item.name: item for item in self.dependencies.check_all()}
        for name in sorted(requested):
            if name in {"FFmpeg", "FFprobe", "Deno"} and not status.get(name, None).available:
                if name not in failed:
                    failed.append(name)
                if name in installed:
                    installed.remove(name)

        return RepairResult(not failed, tuple(dict.fromkeys(installed)), tuple(dict.fromkeys(failed)), "\n".join(details))

    def _install_ffmpeg(self, on_progress) -> None:
        self._emit(on_progress, "FFmpeg", "FFmpeg paketi hazırlanıyor…", 3)
        target = self.dependencies.user_bin_dir()
        target.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="ytdl-ffmpeg-") as tmp:
            tmp_dir = Path(tmp)
            archive = tmp_dir / "ffmpeg.zip"
            self._download_verified(
                FFMPEG_ARCHIVE_URL,
                FFMPEG_CHECKSUM_URL,
                archive,
                component="FFmpeg",
                on_progress=on_progress,
                start_percent=5,
                end_percent=75,
            )
            self._emit(on_progress, "FFmpeg", "FFmpeg paketi açılıyor…", 80)
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(tmp_dir / "extract")

            ffmpeg = self._find_file(tmp_dir / "extract", "ffmpeg.exe")
            ffprobe = self._find_file(tmp_dir / "extract", "ffprobe.exe")
            if not ffmpeg or not ffprobe:
                raise RuntimeError("İndirilen pakette ffmpeg.exe veya ffprobe.exe bulunamadı")

            self._atomic_copy(ffmpeg, target / "ffmpeg.exe")
            self._atomic_copy(ffprobe, target / "ffprobe.exe")

        self._verify_executable(target / "ffmpeg.exe", ("-version",))
        self._verify_executable(target / "ffprobe.exe", ("-version",))
        self._emit(on_progress, "FFmpeg", "FFmpeg ve FFprobe hazır.", 100)

    def _install_deno(self, on_progress) -> None:
        arch = self._deno_architecture()
        filename = f"deno-{arch}-pc-windows-msvc.zip"
        url = f"{DENO_RELEASE_BASE}/{filename}"
        checksum_url = url + ".sha256sum"
        target = self.dependencies.user_bin_dir()
        target.mkdir(parents=True, exist_ok=True)

        self._emit(on_progress, "Deno", "Deno paketi hazırlanıyor…", 3)
        with tempfile.TemporaryDirectory(prefix="ytdl-deno-") as tmp:
            tmp_dir = Path(tmp)
            archive = tmp_dir / "deno.zip"
            self._download_verified(
                url,
                checksum_url,
                archive,
                component="Deno",
                on_progress=on_progress,
                start_percent=5,
                end_percent=80,
            )
            self._emit(on_progress, "Deno", "Deno paketi açılıyor…", 85)
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(tmp_dir / "extract")
            deno = self._find_file(tmp_dir / "extract", "deno.exe")
            if not deno:
                raise RuntimeError("İndirilen pakette deno.exe bulunamadı")
            self._atomic_copy(deno, target / "deno.exe")

        self._verify_executable(target / "deno.exe", ("--version",))
        self._emit(on_progress, "Deno", "Deno hazır.", 100)

    @staticmethod
    def _deno_architecture() -> str:
        machine = platform.machine().lower()
        if machine in {"amd64", "x86_64", "x64"}:
            return "x86_64"
        if machine in {"arm64", "aarch64"}:
            return "aarch64"
        raise RuntimeError(f"Desteklenmeyen Windows mimarisi: {platform.machine()}")

    def _download_verified(
        self,
        url: str,
        checksum_url: str,
        destination: Path,
        *,
        component: str,
        on_progress,
        start_percent: int,
        end_percent: int,
    ) -> None:
        expected = self._fetch_checksum(checksum_url)
        digest = hashlib.sha256()
        try:
            with requests.get(url, stream=True, timeout=(15, 120)) as response:
                response.raise_for_status()
                total = int(response.headers.get("content-length") or 0)
                downloaded = 0
                with destination.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if not chunk:
                            continue
                        handle.write(chunk)
                        digest.update(chunk)
                        downloaded += len(chunk)
                        if total:
                            ratio = min(downloaded / total, 1.0)
                            percent = start_percent + int((end_percent - start_percent) * ratio)
                            self._emit(on_progress, component, f"{component} indiriliyor… %{int(ratio * 100)}", percent)
        except requests.RequestException as exc:
            raise RuntimeError(f"İndirme başarısız: {exc}") from exc

        actual = digest.hexdigest().lower()
        if actual != expected.lower():
            destination.unlink(missing_ok=True)
            raise RuntimeError("İndirilen dosyanın SHA-256 doğrulaması başarısız oldu")

    @staticmethod
    def _fetch_checksum(url: str) -> str:
        try:
            response = requests.get(url, timeout=(15, 30))
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Checksum alınamadı: {exc}") from exc
        text = response.text.strip()

        # Checksum assets are not guaranteed to use the classic
        # "<hash>  <filename>" layout. Deno's Windows release workflow can
        # publish PowerShell Format-List output, for example:
        #
        #   Algorithm : SHA256
        #   Hash      : ABCDEF...
        #   Path      : ...
        #
        # Extract a standalone SHA-256 token instead of assuming the first
        # whitespace-separated token is the digest. Verification remains
        # strict: exactly one distinct 64-hex digest must be present.
        matches = re.findall(r"(?i)(?<![0-9a-f])([0-9a-f]{64})(?![0-9a-f])", text)
        unique = list(dict.fromkeys(match.lower() for match in matches))
        if len(unique) != 1:
            raise RuntimeError("Checksum dosyasında geçerli tek bir SHA-256 değeri bulunamadı")
        return unique[0]

    @staticmethod
    def _find_file(root: Path, filename: str) -> Path | None:
        return next((item for item in root.rglob(filename) if item.is_file()), None)

    @staticmethod
    def _atomic_copy(source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp = destination.with_suffix(destination.suffix + ".new")
        shutil.copy2(source, temp)
        os.replace(temp, destination)

    @staticmethod
    def _verify_executable(path: Path, version_args: tuple[str, ...]) -> None:
        completed = subprocess.run(
            [str(path), *version_args],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip().splitlines()
            suffix = f": {detail[0]}" if detail else ""
            raise RuntimeError(f"{path.name} çalıştırılamadı{suffix}")

    @staticmethod
    def _emit(callback, component: str, message: str, percent: int) -> None:
        if callback:
            callback(RepairProgress(component, message, max(0, min(percent, 100))))
