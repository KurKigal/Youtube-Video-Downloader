from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from youtube_downloader.core.errors import ErrorCode
from youtube_downloader.core.models import DownloadResult


class BatchState(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class BatchSummary:
    state: BatchState
    successes: tuple[DownloadResult, ...]
    failures: tuple[DownloadResult, ...]
    cancelled: tuple[DownloadResult, ...]



def summarize_results(results: list[DownloadResult]) -> BatchSummary:
    successes = tuple(item for item in results if item.success)
    cancelled = tuple(
        item for item in results
        if not item.success and item.error_code == ErrorCode.CANCELLED.value
    )
    failures = tuple(
        item for item in results
        if not item.success and item.error_code != ErrorCode.CANCELLED.value
    )

    if failures and successes:
        state = BatchState.PARTIAL
    elif failures:
        state = BatchState.FAILED
    elif cancelled:
        state = BatchState.CANCELLED
    else:
        state = BatchState.COMPLETED

    return BatchSummary(state, successes, failures, cancelled)
