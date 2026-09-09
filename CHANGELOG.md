# Changelog

## 2.0.1

- Fixed FFmpeg/FFprobe dependency detection on Windows.
- FFmpeg and FFprobe now use their correct `-version` flag during runtime checks and automatic repair verification.
- Deno continues to use `--version`.
- Prevents valid or auto-installed FFmpeg components from being incorrectly reported as missing.

## 2.0.0

- PySide6 tabanlı V2 yeniden yazımı
- Dinamik video kalite/format çözümleme
- Smart MP4 compatibility conversion + FFprobe validation
- Playlist, audio conversion, retry/resume/cancel
- Cancellation artık failure olarak raporlanmıyor
- Responsive pencere ve scroll davranışı
- Windows PyInstaller release build
- FFmpeg/FFprobe/Deno için Windows kullanıcı-local otomatik kurulum ve onarım
- Dependency arşivlerinde SHA-256 doğrulaması
- FFmpeg runtime hatalarında `Bileşenleri Onar` / `Tekrar Dene` / teknik detay UX'i
- yt-dlp için repaired FFmpeg klasörünün explicit `ffmpeg_location` olarak geçirilmesi
- Windows `%TEMP%` pytest izin probleminden bağımsız release test akışı
