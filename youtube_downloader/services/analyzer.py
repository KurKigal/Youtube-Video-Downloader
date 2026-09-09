from __future__ import annotations

from typing import Callable

import yt_dlp

from youtube_downloader.core.formats import quality_options_from_formats
from youtube_downloader.core.models import AnalysisResult, MediaEntry
from youtube_downloader.services.dependencies import DependencyService


class MediaAnalyzer:
    def __init__(self, dependencies: DependencyService | None = None):
        self.dependencies = dependencies or DependencyService()

    def analyze(self, url: str) -> AnalysisResult:
        base_opts = self._base_options()
        base_opts.update({
            "quiet": True,
            "no_warnings": False,
            "skip_download": True,
            "extract_flat": "in_playlist",
            "ignoreerrors": False,
        })

        with yt_dlp.YoutubeDL(base_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            raise RuntimeError("Video bilgisi alınamadı.")

        if info.get("entries") is not None:
            entries = [self._entry_from_info(item) for item in info.get("entries") or [] if item]
            if not entries:
                raise RuntimeError("Playlist boş veya erişilebilir video bulunamadı.")

            # Fetch the first accessible entry fully to provide real quality choices.
            detailed = self.analyze_single(entries[0].url)
            return AnalysisResult(
                source_url=url,
                title=info.get("title") or "Playlist",
                is_playlist=True,
                entries=entries,
                qualities=detailed.qualities,
                thumbnail=info.get("thumbnail") or detailed.thumbnail,
                uploader=info.get("uploader") or info.get("channel") or detailed.uploader,
                duration=None,
                warnings=[
                    "Playlist kalitesi her video için indirme anında yeniden çözülür; listedeki videolar farklı maksimum kaliteye sahip olabilir."
                ],
            )

        return self._analysis_from_single(url, info)

    def analyze_single(self, url: str) -> AnalysisResult:
        opts = self._base_options()
        opts.update({
            "quiet": True,
            "no_warnings": False,
            "skip_download": True,
            "noplaylist": True,
            "ignoreerrors": False,
        })
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            raise RuntimeError("Video bilgisi alınamadı.")
        return self._analysis_from_single(url, info)

    def _analysis_from_single(self, url: str, info: dict) -> AnalysisResult:
        entry = self._entry_from_info(info)
        return AnalysisResult(
            source_url=url,
            title=entry.title,
            is_playlist=False,
            entries=[entry],
            qualities=quality_options_from_formats(info.get("formats") or []),
            thumbnail=entry.thumbnail,
            uploader=entry.uploader,
            duration=entry.duration,
        )

    def _base_options(self) -> dict:
        opts: dict = {
            "socket_timeout": 20,
            "extractor_retries": 3,
            "retries": 5,
        }
        deno = self.dependencies.deno_path()
        if deno:
            opts["js_runtimes"] = {"deno": {"path": deno}}
        return opts

    @staticmethod
    def _entry_from_info(info: dict) -> MediaEntry:
        video_id = str(info.get("id") or "")
        webpage_url = info.get("webpage_url") or info.get("url")
        if webpage_url and not str(webpage_url).startswith(("http://", "https://")) and video_id:
            webpage_url = f"https://www.youtube.com/watch?v={video_id}"
        return MediaEntry(
            id=video_id,
            url=str(webpage_url or ""),
            title=info.get("title") or "Video",
            uploader=info.get("uploader") or info.get("channel") or "",
            duration=info.get("duration"),
            thumbnail=info.get("thumbnail"),
            is_live=bool(info.get("is_live")),
            availability=info.get("availability"),
            raw=info,
        )
