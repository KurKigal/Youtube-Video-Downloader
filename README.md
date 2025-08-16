# Youtube Video Downloader

🎬 Modern, kullanıcı dostu Python tabanlı video indirme uygulaması. YouTube ve diğer platformlardan video/ses dosyalarını farklı kalite seçenekleriyle indirmenizi sağlar.

## 📋 Özellikler

- **Modern Windows GUI**: Koyu tema ile şık arayüz
- **Çoklu Platform Desteği**: YouTube, Vimeo ve diğer popüler platformlar
- **Kalite Seçenekleri**: 720p, 480p, 360p video ve MP3 ses formatları
- **Gerçek Zamanlı İlerleme**: İndirme durumunu canlı takip
- **Anti-Detection**: Bot algılamasına karşı koruma
- **Thumbnail Önizleme**: Video küçük resmi ve bilgileri
- **Akıllı Kurulum**: Otomatik bağımlılık yönetimi

## 📁 Dosya Yapısı

```
Modern-Video-Downloader/
├── video_downloader.py     # Ana uygulama dosyası
├── requirements.txt        # Python bağımlılıkları
├── install.bat            # Kurulum scripti
├── run.bat               # Uygulama başlatıcı
├── quick_start.bat       # Hızlı başlatma (kurulum + çalıştırma)
├── debug.bat             # Hata ayıklama modu
├── uninstall.bat         # Kaldırma scripti
└── README.md             # Bu dosya
```

### Dosya Açıklamaları

- **`video_downloader.py`**: Tkinter tabanlı ana GUI uygulaması. Video indirme, format seçimi ve progress tracking işlevlerini içerir
- **`install.bat`**: Python bağımlılıklarını kurar, FFmpeg kontrolü yapar ve masaüstü kısayolu oluşturur
- **`run.bat`**: Uygulamayı güvenli şekilde başlatır, ön kontroller yapar
- **`quick_start.bat`**: Yeni kullanıcılar için tek tıkla kurulum ve çalıştırma
- **`debug.bat`**: Sistem bilgilerini toplar ve hata ayıklama modunda çalıştırır
- **`uninstall.bat`**: Uygulamayı ve bağımlılıklarını temizler

## 🛠️ Gereksinimler

### Sistem Gereksinimleri
- **İşletim Sistemi**: Windows 10/11
- **Python**: 3.8 veya üzeri
- **RAM**: Minimum 2GB
- **Depolama**: En az 100MB boş alan

### Python Bağımlılıkları
```
Pillow>=9.0.0      # Görsel işleme
requests>=2.28.0   # HTTP istekleri
yt-dlp>=2023.12.30 # Video indirme motoru
```

### İsteğe Bağlı
- **FFmpeg**: MP3 dönüştürme için (otomatik kontrol edilir)

## 🚀 Kurulum ve Çalıştırma

### Yöntem 1: Hızlı Başlangıç (Önerilen)
```bash
# 1. Repoyu indirin
# 2. quick_start.bat dosyasını çift tıklayın
```

### Yöntem 2: Adım Adım Kurulum
```bash
# 1. Python'u indirin ve kurun (python.org)
# 2. Repoyu bir klasöre çıkarın
# 3. install.bat dosyasını çift tıklayın
# 4. run.bat ile uygulamayı başlatın
```

### Yöntem 3: Manuel Kurulum
```bash
# Terminal/CMD açın ve proje klasörüne gidin
pip install -r requirements.txt
python video_downloader.py
```

## 💡 Kullanım Kılavuzu

### Temel Kullanım
1. **URL Girişi**: Video linkini URL kutusuna yapıştırın
2. **Bilgi Alma**: "Video Bilgisi Al" butonuna tıklayın
3. **Format Seçimi**: İstediğiniz kalite/formatı seçin
4. **İndirme**: "İndir" butonuna tıklayın

### Format Seçenekleri
- **720p HD**: En iyi kalite video (MP4)
- **480p**: Orta kalite video (MP4)
- **360p**: Düşük kalite video (MP4)
- **MP3**: Sadece ses dosyası

### Ayarlar Menüsü
- **📁 İndirme Konumu**: Varsayılan `%USERPROFILE%\Downloads\VideoDownloader`
- **⚙️ Ayarlar**: Sağ üst köşedeki dişli simgesi

## 🔧 Hata Giderme

### Python Bulunamadı Hatası
```bash
# Python'u PATH'e ekleyin veya yeniden kurun
# Kurulum sırasında "Add to PATH" seçeneğini işaretleyin
```

### Paket Hatası
```bash
# install.bat dosyasını yönetici olarak çalıştırın
# Veya manuel olarak:
pip install --upgrade pip
pip install -r requirements.txt
```

### FFmpeg Uyarısı
```bash
# MP3 dönüştürme için FFmpeg gereklidir
# İndirme: https://ffmpeg.org/download.html
# FFmpeg'i sistem PATH'ine ekleyin
```

### Debug Modu
```bash
# Detaylı hata bilgisi için debug.bat çalıştırın
# Sistem bilgilerini ve paket durumunu kontrol eder
```

## 🏗️ Teknik Detaylar

### Ana Bileşenler
- **VideoDownloader**: yt-dlp tabanlı indirme motoru
- **ModernVideoDownloaderGUI**: Tkinter GUI arayüzü
- **Config**: Kullanıcı ayarlarını yönetme
- **AntiDetection**: Bot algılamasına karşı koruma

### Anti-Detection Özellikleri
- Rastgele User-Agent rotasyonu
- HTTP header maskeleme
- Rastgele gecikme ekleme
- Rate limiting koruması

### Güvenlik
- URL validasyonu
- Güvenli dosya indirme
- Error handling ve recovery
- Thread-safe işlemler

## 🤝 Geliştirmeye Katkı

Bu proje **açık kaynak** ve **geliştirmeye açıktır**! Katkılarınızı bekliyoruz.

### Katkı Yöntemleri
- 🐛 **Bug Report**: Hata bildirimi yapın
- 💡 **Feature Request**: Yeni özellik önerileri
- 🔧 **Code Contribution**: Kod geliştirmeleri
- 📝 **Documentation**: Dokümantasyon iyileştirmeleri

### Geliştirme Ortamı Kurulumu
```bash
# Repoyu fork edin ve clone edin
git clone https://github.com/KurKigal/Youtube-Video-Downloader.git
cd Youtube-Video-Downloader

# Geliştirme bağımlılıklarını kurun
pip install -r requirements.txt
pip install -r requirements-dev.txt  # (gelecek için)

# Test ortamını kurun
python video_downloader.py
```

### Potansiyel Geliştirme Alanları
- 🌐 **Çoklu Dil Desteği**: İngilizce, Almanca vb.
- 🎨 **Tema Seçenekleri**: Açık tema, renkli temalar
- 📊 **Batch İndirme**: Çoklu video indirme
- 🔄 **Otomatik Güncelleme**: Uygulama güncellemeleri
- ⏯️ **Resume İndirme**: Kesintiden kaldığı yerden devam
- 📱 **Mobil Versiyon**: Android/iOS uygulaması
- 🎵 **Playlist Desteği**: Tüm playlist indirme
- 🏃‍♂️ **Performans İyileştirmeleri**: Daha hızlı indirme

### Kod Standartları
- Python PEP 8 standartlarına uygun yazım
- Türkçe yorum ve değişken isimleri
- Type hints kullanımı (gelecek)
- Unit test yazımı (gelecek)

## 📞 Destek

### İletişim
- **Issues**: GitHub Issues kısmını kullanın
- **Discussions**: Genel sorular için GitHub Discussions
- **Email**: [keseremirhann@gmail.com]

### SSS
**S: Hangi siteleri destekliyor?**
A: YouTube, Vimeo, Dailymotion ve yt-dlp'nin desteklediği 1000+ site

**S: İndirme hızı neden yavaş?**
A: Anti-detection sistemi güvenlik için gecikme ekler

**S: Linux/Mac versiyonu var mı?**
A: Şu anda sadece Windows. Linux/Mac desteği geliştirilmeye açık!

## 📄 Lisans

Bu proje MIT Lisansı altında yayınlanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- **yt-dlp**: Video indirme motoru
- **Tkinter**: GUI framework
- **Pillow**: Görsel işleme
- **Python Community**: Sürekli destek

---

**Not**: Bu uygulama eğitim amaçlıdır. İndirdiğiniz içeriklerin telif haklarına saygı gösterin.

**Version**: 1.0.0 | **Last Updated**: 2025
