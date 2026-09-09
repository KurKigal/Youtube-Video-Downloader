from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Callable

import yt_dlp

from youtube_downloader.core.errors import classify_error
from youtube_downloader.core.formats import build_format_selector, build_postprocessors, expected_extension
from youtube_downloader.core.humanize import format_eta, format_speed
from youtube_downloader.core.models import (
    DownloadProgress,
    DownloadRequest,
    DownloadResult,
    MediaType,
    VideoProfile,
)
from youtube_downloader.services.compatibility import CompatibilityService
from youtube_downloader.services.dependencies import DependencyService


class DownloadCancelled(RuntimeError):
    pass


class YtDlpBackend:
    def __init__(self, dependencies: DependencyService | None = None):
        self.dependencies = dependencies or DependencyService()
        self._cancel = threading.Event()
        self.compatibility = CompatibilityService(
            self.dependencies.ffmpeg_path(),
            self.dependencies.ffprobe_path(),
        )

    def cancel(self) -> None:
        self._cancel.set()
        self.compatibility.cancel()

    def reset_cancel(self) -> None:
        self._cancel.clear()

    @property
    def cancelled(self) -> bool:
        return self._cancel.is_set()

    def refresh_runtime_dependencies(self) -> None:
        self.compatibility = CompatibilityService(
            self.dependencies.ffmpeg_path(),
            self.dependencies.ffprobe_path(),
        )

    def download(
        self,
        request: DownloadRequest,
        on_progress: Callable[[DownloadProgress], None] | None = None,
    ) -> DownloadResult:
        self.refresh_runtime_dependencies()
        request.output_dir.mkdir(parents=True, exist_ok=True)
        last_path: Path | None = None
        title = "Video"

        def emit(progress: DownloadProgress) -> None:
            if on_progress:
                on_progress(progress)

        def progress_hook(data: dict) -> None:
            nonlocal last_path
            if self._cancel.is_set():
                raise DownloadCancelled("Download cancelled by user")

            status = data.get("status") or ""
            filename = data.get("filename") or data.get("info_dict", {}).get("filepath") or ""
            if filename:
                last_path = Path(filename)

            if status == "downloading":
                total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
                downloaded = data.get("downloaded_bytes") or 0
                percent = (downloaded / total * 100.0) if total else 0.0
                emit(DownloadProgress(
                    status="İndiriliyor",
                    percent=max(0.0, min(percent, 100.0)),
                    speed=format_speed(data.get("speed")),
                    eta=format_eta(data.get("eta")),
                    filename=filename,
                ))
            elif status == "finished":
                emit(DownloadProgress(status="Birleştiriliyor / dönüştürülüyor", percent=100.0, filename=filename))

        def postprocessor_hook(data: dict) -> None:
            nonlocal last_path
            info_dict = data.get("info_dict") or {}
            filepath = info_dict.get("filepath") or info_dict.get("_filename")
            if filepath:
                last_path = Path(filepath)
            if data.get("status") == "started":
                emit(DownloadProgress(status="Son işlem uygulanıyor", percent=100.0, filename=str(filepath or "")))

        opts = self._build_options(request, progress_hook, postprocessor_hook)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(request.url, download=True)
                if info:
                    title = info.get("title") or title
                    candidate = info.get("filepath") or info.get("_filename")
                    if candidate:
                        last_path = Path(candidate)

            resolved = self._resolve_final_path(request, last_path, info if info else {})
            if not resolved or not resolved.exists():
                raise RuntimeError("İndirme tamamlandı ancak çıktı dosyası bulunamadı")

            if request.media_type is MediaType.VIDEO and request.video_profile is VideoProfile.COMPATIBLE_MP4:
                if self._cancel.is_set():
                    raise DownloadCancelled("Download cancelled by user")
                emit(DownloadProgress(status="Codec uyumluluğu doğrulanıyor", percent=100.0, filename=str(resolved)))
                resolved, probe, converted = self.compatibility.ensure_universal_mp4(resolved)
                if converted:
                    emit(DownloadProgress(status="Uyumlu MP4 hazır", percent=100.0, filename=str(resolved)))

            emit(DownloadProgress(status="Tamamlandı", percent=100.0, filename=str(resolved or "")))
            return DownloadResult(True, title=title, output_path=resolved)
        except Exception as exc:
            if self._cancel.is_set():
                classified = classify_error(DownloadCancelled("Download cancelled by user"))
            else:
                classified = classify_error(exc)
            return DownloadResult(
                False,
                title=title,
                output_path=last_path,
                error_code=classified.code.value,
                error_message=classified.user_message,
                error_detail=classified.technical_message,
            )

    def _build_options(self, request: DownloadRequest, progress_hook, postprocessor_hook) -> dict:
        # ID suffix prevents collisions while keeping filenames readable. The byte-limit
        # protects common Windows path-length edge cases without stripping Unicode.
        output_template = str(request.output_dir / "%(title).160B [%(id)s].%(ext)s")

        opts: dict = {
            "format": build_format_selector(request),
            "outtmpl": {"default": output_template},
            "progress_hooks": [progress_hook],
            "postprocessor_hooks": [postprocessor_hook],
            "noplaylist": True,
            "quiet": True,
            "no_warnings": False,
            "overwrites": False,
            "continuedl": True,
            "retries": 5,
            "fragment_retries": 10,
            "extractor_retries": 3,
            "file_access_retries": 3,
            "socket_timeout": 20,
            "concurrent_fragment_downloads": 4,
            "windowsfilenames": os.name == "nt",
        }

        deno = self.dependencies.deno_path()
        if deno:
            opts["js_runtimes"] = {"deno": {"path": deno}}

        ffmpeg = self.dependencies.ffmpeg_path()
        if ffmpeg:
            # yt-dlp needs the directory explicitly because repaired components live
            # in a user-local app folder and are intentionally not added to PATH.
            opts["ffmpeg_location"] = str(Path(ffmpeg).parent)

        if request.browser_cookies:
            opts["cookiesfrombrowser"] = (request.browser_cookies, None, None, None)

        postprocessors = build_postprocessors(request)
        if postprocessors:
            opts["postprocessors"] = postprocessors

        if request.media_type is MediaType.VIDEO and request.video_profile is VideoProfile.COMPATIBLE_MP4:
            opts["merge_output_format"] = "mp4"
            # The format selector itself expresses AVC/AAC preference and fallback order.

        return opts

    @staticmethod
    def _resolve_final_path(request: DownloadRequest, candidate: Path | None, info: dict) -> Path | None:
        candidates: list[Path] = []
        for value in (
            candidate,
            Path(info["filepath"]) if info.get("filepath") else None,
            Path(info["_filename"]) if info.get("_filename") else None,
        ):
            if value and value not in candidates:
                candidates.append(value)

        for item in info.get("requested_downloads") or []:
            value = item.get("filepath")
            if value:
                path = Path(value)
                if path not in candidates:
                    candidates.append(path)

        ext = expected_extension(request)
        expanded: list[Path] = []
        for path in candidates:
            expanded.append(path)
            if ext:
                expanded.append(path.with_suffix(f".{ext}"))
            # Merged video commonly ends in mp4/mkv/webm regardless of requested stream paths.
            if request.media_type is MediaType.VIDEO:
                expanded.extend(path.with_suffix(suffix) for suffix in (".mp4", ".mkv", ".webm"))

        for path in expanded:
            if path.exists() and path.is_file() and not path.name.endswith((".part", ".ytdl")):
                return path

        video_id = str(info.get("id") or "")
        if video_id and request.output_dir.exists():
            matches = [
                p for p in request.output_dir.iterdir()
                if p.is_file() and f"[{video_id}]" in p.name and not p.name.endswith((".part", ".ytdl"))
            ]
            if matches:
                return max(matches, key=lambda p: p.stat().st_mtime)
        return candidate
