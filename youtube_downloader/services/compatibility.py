from __future__ import annotations

import os
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path

from .media_probe import MediaProbeService, ProbeResult


@dataclass(frozen=True, slots=True)
class ConversionPlan:
    video_codec: str
    audio_codec: str
    remux_only: bool


def build_conversion_plan(probe: ProbeResult) -> ConversionPlan | None:
    if probe.is_universal_mp4:
        return None
    video_codec = "copy" if probe.video_codec in {None, "h264"} else "libx264"
    audio_codec = "copy" if probe.audio_codec in {None, "aac"} else "aac"
    return ConversionPlan(
        video_codec=video_codec,
        audio_codec=audio_codec,
        remux_only=(video_codec == "copy" and audio_codec == "copy"),
    )


class CompatibilityService:
    def __init__(self, ffmpeg_path: str | None, ffprobe_path: str | None):
        self.ffmpeg_path = ffmpeg_path
        self.probe_service = MediaProbeService(ffprobe_path)
        self._process_lock = threading.Lock()
        self._active_process: subprocess.Popen | None = None

    def cancel(self) -> None:
        with self._process_lock:
            process = self._active_process
        if process and process.poll() is None:
            process.terminate()

    def ensure_universal_mp4(self, source: Path) -> tuple[Path, ProbeResult, bool]:
        """Return a verified MP4 (H.264 + AAC where streams exist).

        Re-encodes only the incompatible stream(s). If both streams are already compatible
        but the container is not MP4, performs a lossless remux.
        """
        probe = self.probe_service.probe(source)
        plan = build_conversion_plan(probe)
        if plan is None:
            return source, probe, False
        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg bulunamadı")

        destination = source.with_suffix(".mp4")
        temp = source.with_name(f".{source.stem}.compat-{os.getpid()}.mp4")
        command = [self.ffmpeg_path, "-y", "-hide_banner", "-loglevel", "error", "-i", str(source)]
        command += ["-map", "0:v:0?", "-map", "0:a:0?"]

        if plan.video_codec == "libx264":
            command += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"]
        else:
            command += ["-c:v", "copy"]

        if plan.audio_codec == "aac":
            command += ["-c:a", "aac", "-b:a", "192k"]
        else:
            command += ["-c:a", "copy"]

        command += ["-movflags", "+faststart", str(temp)]

        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        with self._process_lock:
            self._active_process = process
        _, stderr = process.communicate()
        with self._process_lock:
            self._active_process = None

        if process.returncode != 0:
            temp.unlink(missing_ok=True)
            raise RuntimeError(f"FFmpeg uyumluluk dönüşümü başarısız: {(stderr or '').strip()}")

        verified = self.probe_service.probe(temp)
        if not verified.is_universal_mp4:
            temp.unlink(missing_ok=True)
            raise RuntimeError(
                f"FFmpeg çıktısı doğrulanamadı: container={verified.container}, "
                f"video={verified.video_codec}, audio={verified.audio_codec}"
            )

        # If source already had .mp4, replace atomically-ish after successful verification.
        # Otherwise create the sibling .mp4 and remove the source only after success.
        if destination.exists() and destination != source:
            destination.unlink()
        if destination == source:
            backup = source.with_suffix(source.suffix + ".old")
            backup.unlink(missing_ok=True)
            source.replace(backup)
            try:
                temp.replace(destination)
                backup.unlink(missing_ok=True)
            except Exception:
                if not source.exists() and backup.exists():
                    backup.replace(source)
                raise
        else:
            temp.replace(destination)
            source.unlink(missing_ok=True)

        return destination, verified, True
