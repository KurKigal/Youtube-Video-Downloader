from youtube_downloader.core.errors import ErrorCode
from youtube_downloader.core.models import DownloadResult
from youtube_downloader.core.results import BatchState, summarize_results


def test_cancelled_result_is_not_failure():
    result = DownloadResult(False, "Video", error_code=ErrorCode.CANCELLED.value)
    summary = summarize_results([result])
    assert summary.state is BatchState.CANCELLED
    assert not summary.failures
    assert len(summary.cancelled) == 1


def test_success_before_cancel_keeps_completed_result():
    summary = summarize_results([
        DownloadResult(True, "A"),
        DownloadResult(False, "B", error_code=ErrorCode.CANCELLED.value),
    ])
    assert summary.state is BatchState.CANCELLED
    assert len(summary.successes) == 1


def test_real_failure_is_still_failure():
    summary = summarize_results([
        DownloadResult(False, "Video", error_code=ErrorCode.NETWORK.value),
    ])
    assert summary.state is BatchState.FAILED
    assert len(summary.failures) == 1
