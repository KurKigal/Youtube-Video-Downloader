# Youtube Video İndirici (GUI)

Modern ve kullanıcı dostu bir arayüze sahip, **yt-dlp** tabanlı Youtube video ve playlist indirme uygulaması.

<img width="950" height="832" alt="Ekran Görüntüsü" src="https://github.com/user-attachments/assets/9fdec04e-10fa-4cc5-9506-618b343d6f41" />


## Özellikler

- **Video ve Ses İndirme:** Videoları istenilen kalitede (1080p, 720p vb.) veya sadece ses (MP3) olarak indirebilirsiniz.
- **Playlist Desteği:** Bir playlist linki yapıştırdığınızda tüm videoları algılar ve sırayla indirir.
- **Modern Arayüz:** `customtkinter` ile geliştirilmiş şık ve karanlık mod destekli arayüz.
- **Küçük Resim Önizleme:** İndirilecek videonun başlık, süre ve küçük resmini (thumbnail) gösterir.
- **FFmpeg Kontrolü:** Uygulama açılışta `ffmpeg` kontrolü yapar ve eksikse kurulum için yönlendirir.

## Kurulum

1.  Proje dosyalarını indirin.
2.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```
3.  Uygulamayı çalıştırın:
    ```bash
    python downloader_app.py
    ```

## Gereksinimler

- Python 3.x
- [FFmpeg](https://ffmpeg.org/download.html) (Sistemde yüklü olmalı veya `ffmpeg.exe` proje klasöründe bulunmalı)

> **Not:** Windows kullanıcıları için hazır `.exe` sürümüne [Releases](https://github.com/KurKigal/Youtube-Video-Downloader/releases) kısmından ulaşabilirsiniz. `.exe` sürümünü kullanıyorsanız Python kurmanıza gerek yoktur, ancak `ffmpeg` yine de gereklidir. Uygulama açılışta size bu konuda yardımcı olacaktır.

## Kullanım

1.  Youtube video veya playlist bağlantısını "Video Linki" alanına yapıştırın.
2.  "Getir" butonuna tıklayın.
3.  Video bilgileri geldikten sonra "Kalite Seçimi" menüsünden istediğiniz formatı seçin.
4.  "İNDİRMEYİ BAŞLAT" butonuna tıklayarak indirmeyi başlatın.

## Lisans

Bu proje açık kaynaklıdır ve eğitim amaçlı geliştirilmiştir.

---
*Geliştirici: Emirhan Keser*
