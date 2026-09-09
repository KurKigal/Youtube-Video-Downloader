from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ErrorCode(str, Enum):
    NETWORK = "network"
    LOGIN_REQUIRED = "login_required"
    AGE_RESTRICTED = "age_restricted"
    PRIVATE = "private"
    GEO_RESTRICTED = "geo_restricted"
    VIDEO_UNAVAILABLE = "video_unavailable"
    FORMAT_UNAVAILABLE = "format_unavailable"
    HTTP_403 = "http_403"
    DISK_FULL = "disk_full"
    MEDIA_COMPONENT_MISSING = "media_component_missing"
    FFMPEG = "ffmpeg"
    JS_RUNTIME = "js_runtime"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ClassifiedError:
    code: ErrorCode
    user_message: str
    technical_message: str


def classify_error(exc: BaseException | str) -> ClassifiedError:
    raw = str(exc)
    text = raw.lower()

    rules: tuple[tuple[tuple[str, ...], ErrorCode, str], ...] = (
        (("cancelled", "canceled", "interrupted by user"), ErrorCode.CANCELLED,
         "İndirme iptal edildi."),
        (("ffmpeg bulunamadı", "ffprobe bulunamadı", "ffmpeg not found", "ffprobe not found"),
         ErrorCode.MEDIA_COMPONENT_MISSING,
         "Gerekli medya bileşenleri bulunamadı. Uygulama bunları otomatik olarak kurabilir."),
        (("no supported javascript runtime", "javascript runtime"), ErrorCode.JS_RUNTIME,
         "YouTube çözümlemesi için Deno bulunamadı veya çalıştırılamadı."),
        (("sign in to confirm", "login required", "cookies-from-browser"), ErrorCode.LOGIN_REQUIRED,
         "Bu video oturum açılmasını gerektiriyor. Tarayıcı çerezleriyle tekrar deneyin."),
        (("age-restricted", "age restricted"), ErrorCode.AGE_RESTRICTED,
         "Bu video yaş kısıtlamalı. Erişimi olan bir tarayıcı oturumu gerekebilir."),
        (("private video", "this video is private"), ErrorCode.PRIVATE,
         "Video özel. Yalnızca videoya erişimi olan hesapla indirilebilir."),
        (("not available in your country", "geo restricted", "geo-restricted"), ErrorCode.GEO_RESTRICTED,
         "Video bulunduğunuz bölgede kullanılamıyor."),
        (("requested format is not available", "format is not available"), ErrorCode.FORMAT_UNAVAILABLE,
         "Seçilen kalite bu video için kullanılamıyor."),
        (("http error 403", "403 forbidden", "status code: 403"), ErrorCode.HTTP_403,
         "YouTube indirme isteğini reddetti (HTTP 403). Motoru ve oturum ayarlarını kontrol edin."),
        (("no space left on device", "disk full"), ErrorCode.DISK_FULL,
         "Diskte yeterli boş alan yok."),
        (("ffmpeg", "ffprobe"), ErrorCode.FFMPEG,
         "Video işlenirken FFmpeg/FFprobe işlemi başarısız oldu."),
        (("unable to download", "timed out", "connection reset", "network is unreachable"), ErrorCode.NETWORK,
         "Ağ bağlantısı sırasında hata oluştu. Bağlantıyı kontrol edip tekrar deneyin."),
        (("video unavailable", "this video is unavailable", "removed by the uploader"), ErrorCode.VIDEO_UNAVAILABLE,
         "Video artık kullanılamıyor veya kaldırılmış."),
    )

    for needles, code, message in rules:
        if any(needle in text for needle in needles):
            return ClassifiedError(code, message, raw)

    return ClassifiedError(ErrorCode.UNKNOWN, "İşlem beklenmeyen bir hata nedeniyle tamamlanamadı.", raw)
