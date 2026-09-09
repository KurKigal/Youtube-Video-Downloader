from youtube_downloader.core.errors import ErrorCode
from youtube_downloader.core.models import DownloadResult
from youtube_downloader.core.results import BatchState, summarize_results


def ok(title: str = "ok") -> DownloadResult:
    return DownloadResult(True, title=title)


def failed(title: str = "bad") -> DownloadResult:
    return DownloadResult(False, title=title, error_code="network", error_message="Ağ hatası")


def cancelled(title: str = "cancel") -> DownloadResult:
    return DownloadResult(
        False,
        title=title,
        error_code=ErrorCode.CANCELLED.value,
        error_message="İndirme iptal edildi.",
    )


def test_only_cancelled_is_not_failure():
    summary = summarize_results([cancelled()])
    assert summary.state is BatchState.CANCELLED
    assert not summary.failures
    assert len(summary.cancelled) == 1


def test_success_before_cancel_is_cancelled_batch():
    summary = summarize_results([ok(), cancelled()])
    assert summary.state is BatchState.CANCELLED
    assert summary.completed_count == 1
    assert not summary.failures


def test_real_failure_remains_failure():
    summary = summarize_results([failed()])
    assert summary.state is BatchState.FAILED
    assert len(summary.failures) == 1


def test_success_and_failure_is_partial():
    summary = summarize_results([ok(), failed()])
    assert summary.state is BatchState.PARTIAL
