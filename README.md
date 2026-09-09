# YouTube Downloader V2.0.0

PySide6 arayüzlü, `yt-dlp` tabanlı Windows/Linux video ve ses indirici.

V2; eski CustomTkinter sürümünün yeniden yazılmış, modüler ve daha sağlam sürümüdür. Eski kaynaklar `legacy/` altında korunur.

## Öne çıkanlar

- Windows/Linux için tek codebase
- PySide6 arayüz
- Sabit YouTube `format_id` bağımlılığı olmadan dinamik kalite çözümleme
- 4K/HDR/yüksek FPS formatlarını analiz etme
- `Uyumlu MP4`, `En iyi kalite`, `Orijinale yakın` video profilleri
- MP3, M4A, Opus, FLAC, WAV ve dönüştürmesiz ses seçenekleri
- Playlist seçimi ve batch indirme
- Retry / fragment retry / resume
- İptal durumunu hatadan ayıran download state yönetimi
- Chrome / Edge / Firefox / Brave cookie desteği
- FFprobe ile çıktı doğrulama
- Akıllı FFmpeg dönüşümü: yalnız uyumsuz stream gerektiğinde dönüştürülür
- Deno + EJS desteği

## Otomatik sistem bileşeni kurulumu

Windows sürümü FFmpeg, FFprobe veya Deno bulunmadığında kullanıcıya otomatik kurulum sunar.

Bileşenler:

```text
%LOCALAPPDATA%\YouTube-Downloader-V2\bin
```

altına kurulur. Yönetici izni ve sistem PATH değişikliği gerekmez.

Kurulum akışı:

1. Bileşen eksikliği tespit edilir.
2. Kullanıcı `Otomatik Kur / Onar` seçer.
3. Resmî/sağlayıcı kaynaktan ZIP ve SHA-256 checksum indirilir.
4. Arşiv SHA-256 ile doğrulanır.
5. `ffmpeg.exe`, `ffprobe.exe` ve/veya `deno.exe` kullanıcı-local klasöre kurulur.
6. Binary `--version` ile çalıştırılarak doğrulanır.
7. Bekleyen analiz/indirme otomatik tekrar denenebilir.

FFmpeg işlemi gerçekten başarısız olursa eksik bileşen hatasından ayrı gösterilir. Hata penceresinde `Bileşenleri Onar`, `Tekrar Dene` ve teknik detay akışı bulunur.

Üçüncü taraf bileşen ayrıntıları için `THIRD_PARTY_COMPONENTS.md` dosyasına bakın.

## Gereksinimler — kaynak koddan çalıştırma

- Python 3.12+
- Windows'ta FFmpeg/FFprobe/Deno eksikse uygulama otomatik kurabilir.

```bash
python -m pip install -r requirements.txt
python main.py
```

## Test

```bash
python -m pytest
```

Windows release script'i, Windows `%TEMP%` izin sorunlarından etkilenmemek için pytest geçici klasörünü proje içinde oluşturur ve herhangi bir test başarısızsa build'i durdurur.

## Windows release build

PowerShell:

```powershell
.\.env\Scripts\Activate.ps1
.\build_release_windows.ps1
```

Çıktı:

```text
release\YouTube-Downloader-V2-Windows-x64.zip
```

Default release ZIP'i FFmpeg/Deno binary'lerini gömmez; uygulama eksik bileşenleri ilk ihtiyaçta kullanıcı-local olarak kurabilir. İsterseniz exe yanına `bin/` klasörü koyup `ffmpeg.exe`, `ffprobe.exe`, `deno.exe` ile portable override da kullanabilirsiniz.

## Mimari

```text
youtube_downloader/
├── core/
│   ├── errors.py
│   ├── filenames.py
│   ├── formats.py
│   ├── humanize.py
│   ├── models.py
│   └── results.py
├── services/
│   ├── analyzer.py
│   ├── compatibility.py
│   ├── dependencies.py
│   ├── dependency_repair.py
│   ├── downloader.py
│   ├── media_probe.py
│   └── thumbnail.py
└── ui/
    ├── main_window.py
    └── workers.py
```

## Sınırlar

Uygulama kullanıcının normalde erişebildiği içeriklerle çalışmayı hedefler. DRM korumasını, yetkisiz private video erişimini veya kullanıcının sahip olmadığı üyelik erişimini aşmayı hedeflemez.

## License

Bkz. `LICENSE`.
