# Youtube Video İndirici (GUI) v2.4

Modern, kullanıcı dostu ve **Cross-Platform** (Windows & Linux) destekli, **yt-dlp** tabanlı gelişmiş Youtube video ve playlist indirme uygulaması.

<img width="950" height="832" alt="Ekran Görüntüsü" src="https://github.com/user-attachments/assets/9fdec04e-10fa-4cc5-9506-618b343d6f41" />

## 🚀 Özellikler

- **Çoklu Platform Desteği:** Hem Windows hem de Linux için optimize edilmiş ayrı sürümler.
- **📺 Gelişmiş Playlist Desteği:** - Playlist linklerini otomatik algılar.
  - Videolar arasında `Önceki` ve `Sonraki` butonları ile gezinebilirsiniz.
  - Tüm listeyi sırayla indirir.
- **⚙️ Otomatik FFmpeg Kurulumu (Windows):** Windows sürümünde FFmpeg eksikse program otomatik olarak indirip kurar. Manuel ayar gerektirmez.
- **🖼️ Görsel Önizleme:** İndirilecek videonun kapağını (thumbnail), başlığını, kanalını ve süresini gösterir.
- **🛡️ Akıllı Dosya Yönetimi:** - Aynı isimde dosya varsa üzerine yazmaz, `(1)`, `(2)` şeklinde numaralandırır.
  - Windows Media Player uyumluluğu için sesleri otomatik optimize eder.
- **🎨 Modern Arayüz:** `customtkinter` ile hazırlanmış, göze hitap eden karanlık mod tasarımı.

---

## 📥 Kurulum ve Kullanım

### 🪟 Windows Kullanıcıları İçin

**Yöntem 1: Hazır .EXE (Önerilen)**
Python kurmanıza gerek yoktur.
1. [Releases](https://github.com/KurKigal/Youtube-Video-Downloader/releases) kısmından en son sürümü (`downloader_app.exe`) indirin.
2. Çift tıklayıp çalıştırın.
3. *Not: FFmpeg eksikse program ilk açılışta otomatik olarak indirecektir.*

**Yöntem 2: Kaynak Koddan Çalıştırma**
1. Repoyu klonlayın veya indirin.
2. Gerekli kütüphaneleri kurun:
   ```bash
   pip install -r requirements.txt

```

3. Windows sürümünü çalıştırın:
```bash
python downloader_windows.py

```



### 🐧 Linux Kullanıcıları İçin (Arch, Ubuntu, Fedora...)

Linux sürümü sistem temasını ve fontlarını otomatik algılar.

1. Repoyu klonlayın:
```bash
git clone [https://github.com/KurKigal/Youtube-Video-Downloader.git](https://github.com/KurKigal/Youtube-Video-Downloader.git)
cd Youtube-Video-Downloader

```


2. Gerekli kütüphaneleri kurun:
```bash
pip install -r requirements.txt

```


3. **Önemli:** Sisteminizde FFmpeg yüklü olmalıdır. Yüklü değilse terminalden kurun:
* **Arch Linux:** `sudo pacman -S ffmpeg`
* **Ubuntu/Debian:** `sudo apt install ffmpeg`
* **Fedora:** `sudo dnf install ffmpeg`


4. Uygulamayı çalıştırın:
```bash
python downloader_linux.py

```



---

## 🛠️ Gereksinimler (Kaynak Kod İçin)

* Python 3.x
* `customtkinter`
* `yt-dlp`
* `Pillow`
* `requests`
* `CTkMessagebox`

## 🤝 Katkıda Bulunma

Hataları bildirmek veya özellik isteğinde bulunmak için [Issues](https://www.google.com/search?q=https://github.com/KurKigal/Youtube-Video-Downloader/issues) kısmını kullanabilirsiniz. Pull request'ler memnuniyetle karşılanır.

## 📄 Lisans

Bu proje açık kaynaklıdır ve eğitim amaçlı geliştirilmiştir.

---

*Geliştirici: [Emirhan Keser*](https://github.com/KurKigal)

```

### Neleri Değiştirdim/Ekledim?

1.  **Dosya İsimleri:** Artık `downloader_app.py` yerine `downloader_windows.py` ve `downloader_linux.py` referansı verdik.
2.  **Linux Özel Bölümü:** Linux kullanıcıları için FFmpeg'in terminalden nasıl kurulacağını ekledim (Çünkü Linux kodunda otomatik indirme yok, uyarı var).
3.  **Yeni Özellikler:** Playlist navigasyonu, overwrite koruması ve Windows Media Player uyumluluğu gibi yeni eklediğimiz özellikleri listeye yazdım.
4.  **Yapı:** Windows ve Linux kurulumlarını birbirinden ayırarak okuyucunun kafasının karışmasını engelledim.

```
