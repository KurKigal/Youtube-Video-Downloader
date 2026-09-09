# YouTube Downloader V2 — Release Candidate 1

PySide6 arayüzlü, `yt-dlp` tabanlı Windows/Linux video ve ses indirici.

> V2 kullanıcı testleri için Release Candidate aşamasındadır. Eski CustomTkinter sürümü `legacy/` altında korunur.


## RC1’de değişenler

- Kullanıcı iptali artık hata olarak raporlanmaz; `İndirme iptal edildi` ayrı terminal durumudur.
- Playlist indirirken iptal isteği videolar arasında kaybolmaz; tüm batch için tek cancellation state kullanılır.
- FFmpeg dönüşümü sırasında yapılan iptal de `FFmpeg hatası` yerine doğru şekilde iptal olarak sınıflandırılır.
- Pencere başlangıç boyutu ekranın kullanılabilir alanına göre otomatik ayarlanır ve ortalanır.
- 980 px altındaki pencere genişliklerinde önizleme ve ayarlar kartları otomatik olarak alt alta geçer.
- Ana içerik QScrollArea üzerinde kaldığı için küçük ekranlarda dikey scroll ile tüm kontrollere erişilebilir.
- Release build için `YouTubeDownloaderV2.spec`, `requirements-build.txt` ve `build_release_windows.ps1` eklendi.
- Release exe, `bin/ffmpeg(.exe)`, `bin/ffprobe(.exe)` ve `bin/deno(.exe)` gibi uygulama-yanı bağımlılıkları PATH'ten önce algılayabilir.

Windows release build:

```powershell
.\build_release_windows.ps1
```

Çıktı: `release/YouTube-Downloader-V2-Windows-x64.zip`

## Alpha 2'de değişenler

- Arayüz yeniden düzenlendi: kart içi siyah label şeritleri kaldırıldı, spacing ve tipografi iyileştirildi.
- Önizleme alanı pencere boyutuna göre daha düzgün ölçeklenir.
- İndirme ayarları daha okunur form düzenine taşındı.
- Kayıt konumu salt-okunur alan + daha belirgin `Klasör seç` butonuna dönüştürüldü.
- Playlist için `Tümünü seç` ve `Seçimi temizle` kontrolleri eklendi.
- İndirme durum kartı sadeleştirildi; terminal/debug görünümlü satır kaldırıldı.
- yt-dlp'nin ANSI renk kodlu `_speed_str` / `_eta_str` değerleri artık UI'a taşınmıyor. Hız ve ETA ham sayısal veriden uygulama tarafından formatlanıyor.
- Geçici `.f616.mp4` benzeri stream dosya adları ilerleme ekranında gösterilmiyor.
- Windows'ta görülen `QFont::setPointSize ... -1` uyarısını önlemek için uygulama fontu geçerli point size ile açıkça ayarlanıyor.

## V2'deki temel mimari değişiklikler

- Windows ve Linux için **tek codebase**.
- UI ile indirme motoru birbirinden ayrıldı.
- Kalite seçimi sabit YouTube `format_id`'lerine bağlı değil; her video için indirme anında yeniden çözülür.
- Playlist'te her videoya aynı format ID'sini zorlama kaldırıldı.
- `Uyumlu MP4`, `En iyi kalite` ve `Orijinale yakın` video profilleri bulunur.
- Ses için MP3, M4A, Opus, FLAC, WAV ve dönüştürmesiz en iyi ses seçenekleri bulunur.
- Retry, fragment retry, continue/resume ve hata sınıflandırma altyapısı bulunur.
- Başarısız indirmeler başarı olarak gösterilmez; playlist sonuçları ayrı raporlanır.
- İptal desteği vardır.
- FFmpeg, FFprobe, Deno, yt-dlp ve EJS bağımlılık kontrolleri bulunur.
- `Uyumlu MP4` çıktısı FFprobe ile doğrulanır; gerekiyorsa FFmpeg ile H.264/AAC uyumluluğu sağlanır.
- Chrome, Edge, Firefox ve Brave tarayıcı çerezlerini kullanma seçeneği bulunur.

## Gereksinimler

- Python 3.12+
- FFmpeg + FFprobe
- Deno 2.3+

Python bağımlılıkları:

```bash
python -m pip install -r requirements.txt
```

Kontroller:

```bash
deno --version
ffmpeg -version
ffprobe -version
```

## Çalıştırma

```bash
python main.py
```

veya editable kurulumdan sonra:

```bash
python -m pip install -e .
youtube-downloader
```

## Test

```bash
pytest
```

## Mimari

```text
youtube_downloader/
├── core/
│   ├── errors.py
│   ├── filenames.py
│   ├── formats.py
│   ├── humanize.py
│   └── models.py
├── services/
│   ├── analyzer.py
│   ├── compatibility.py
│   ├── dependencies.py
│   ├── downloader.py
│   ├── media_probe.py
│   └── thumbnail.py
└── ui/
    ├── main_window.py
    └── workers.py
```

## Sınırlar

Uygulama kullanıcının normalde erişebildiği içeriklerle çalışmayı hedefler. DRM korumasını, yetkisiz private video erişimini veya kullanıcının sahip olmadığı üyelik erişimini aşmayı hedeflemez.

## Legacy

V1 kaynakları:

```text
legacy/downloader-windows.py
legacy/downloader-linux.py
```

## License

Bkz. `LICENSE`.
