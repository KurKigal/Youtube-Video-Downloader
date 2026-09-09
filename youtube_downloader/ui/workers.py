from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from youtube_downloader.core.models import DownloadProgress, DownloadRequest
from youtube_downloader.services.analyzer import MediaAnalyzer
from youtube_downloader.services.dependency_repair import DependencyRepairService
from youtube_downloader.services.downloader import YtDlpBackend
from youtube_downloader.services.thumbnail import fetch_thumbnail


class AnalysisWorker(QObject):
    finished = Signal(object, object)
    failed = Signal(object)

    def __init__(self, analyzer: MediaAnalyzer, url: str):
        super().__init__()
        self.analyzer = analyzer
        self.url = url

    @Slot()
    def run(self) -> None:
        try:
            result = self.analyzer.analyze(self.url)
            thumbnail = fetch_thumbnail(result.thumbnail)
            self.finished.emit(result, thumbnail)
        except Exception as exc:
            self.failed.emit(exc)


class DownloadWorker(QObject):
    progress = Signal(object)
    finished = Signal(object)

    def __init__(self, backend: YtDlpBackend, requests: list[DownloadRequest]):
        super().__init__()
        self.backend = backend
        self.requests = requests

    @Slot()
    def run(self) -> None:
        results = []
        total = len(self.requests)
        for index, request in enumerate(self.requests, start=1):
            if self.backend.cancelled:
                break
            def report(progress: DownloadProgress, i=index, count=total):
                if count > 1:
                    progress.status = f"{i}/{count} · {progress.status}"
                self.progress.emit(progress)

            result = self.backend.download(request, report)
            results.append(result)
            if result.error_code == "cancelled":
                break
        self.finished.emit(results)


class DependencyRepairWorker(QObject):
    progress = Signal(object)
    finished = Signal(object)
    failed = Signal(object)

    def __init__(self, service: DependencyRepairService, components: set[str]):
        super().__init__()
        self.service = service
        self.components = components

    @Slot()
    def run(self) -> None:
        try:
            result = self.service.repair(self.components, self.progress.emit)
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(exc)
