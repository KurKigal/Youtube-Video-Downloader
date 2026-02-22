import customtkinter as ctk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox 
import yt_dlp
import threading
import os
import shutil
import sys
import re
import requests
import webbrowser
from PIL import Image
from io import BytesIO
import platform

## Bilgilendirme: Şu an Linux ortamlarında VLC kullanıldığı varsayılarak yapılmıştır.

# Görünüm Ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# İşletim sistemine göre font seçimi
APP_FONT = "Segoe UI" if platform.system() == "Windows" else "Arial"

class YtDlpApp(ctk.CTk):
    """
    YouTube video ve playlist indirme işlemlerini yöneten ana GUI sınıfı (Linux Versiyonu).
    Linux sistemlerinde FFmpeg kontrolü yapar ve kullanıcıyı yönlendirir.
    """
    def __init__(self):
        super().__init__()

        # Pencere Yapılandırması
        self.title("Youtube Video İndirici (Linux)")
        self.geometry("950x800") 
        self.minsize(800, 650)   
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.running = True
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Durum Değişkenleri
        self.save_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        # Eğer Linux'ta Downloads klasörü yoksa Home dizinine düşsün
        if not os.path.exists(self.save_path):
            self.save_path = os.path.expanduser('~')

        self.format_map = {} 
        
        # Playlist ve Video Verileri
        self.is_playlist = False
        self.playlist_entries = [] 
        self.current_video_index = 0 
        self.current_video_data = None 

        # Uygulama Başlangıcı
        self.show_splash_screen()

    def on_closing(self):
        """Uygulama kapatıldığında çağrılır, thread'leri sonlandırır."""
        self.running = False
        self.destroy()
        sys.exit()

    # ---------------------------------------------------------
    # BÖLÜM 1: AÇILIŞ EKRANI (SPLASH SCREEN)
    # ---------------------------------------------------------
    def show_splash_screen(self):
        """Açılış ekranını gösterir ve sistem kontrollerini başlatır."""
        self.splash_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.splash_frame.grid(row=0, column=0, sticky="nsew")
        self.splash_frame.grid_columnconfigure(0, weight=1)
        self.splash_frame.grid_rowconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(self.splash_frame, fg_color="transparent")
        content_frame.grid(row=0, column=0)

        ctk.CTkLabel(content_frame, text="Youtube Video İndirici", font=(APP_FONT, 32, "bold"), text_color="#ffffff").pack(pady=(0, 20))
        self.check_label = ctk.CTkLabel(content_frame, text="⏳", font=("Arial", 50), text_color="#0084ff")
        self.check_label.pack(pady=10)
        self.info_label = ctk.CTkLabel(content_frame, text="Sistem kontrol ediliyor...", font=(APP_FONT, 14), text_color="#a0a0a0")
        self.info_label.pack(pady=(10, 30))
        self.splash_btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.splash_btn_frame.pack()

        self.after(1000, self.check_ffmpeg)

    def check_ffmpeg(self):
        """FFmpeg'in sistemde yüklü olup olmadığını kontrol eder."""
        if not self.running: return
        
        # Linux uyumlu kontrol (shutil.which path'e bakar)
        system_ffmpeg = shutil.which("ffmpeg")

        if system_ffmpeg:
            self.check_label.configure(text="✓", text_color="#00d26a")
            self.info_label.configure(text="Sistem Hazır! Başlatılıyor...", text_color="#00d26a")
            self.after(1000, self.switch_to_main_menu)
        else:
            self.check_label.configure(text="✘", text_color="#ff4444")
            self.info_label.configure(text="FFMPEG Bulunamadı.", text_color="#ff4444")
            if not hasattr(self, 'install_btn'):
                self.install_btn = ctk.CTkButton(self.splash_btn_frame, text="Nasıl Yüklenir?", command=self.install_ffmpeg_action, fg_color="#ff5555", hover_color="#cc4444")
                self.install_btn.pack(pady=5)
                self.retry_btn = ctk.CTkButton(self.splash_btn_frame, text="Tekrar Dene", command=self.retry_check_action, fg_color="#555555", hover_color="#666666")
                self.retry_btn.pack(pady=5)

    def install_ffmpeg_action(self):
        """Kullanıcıya FFmpeg yüklemesi için bilgi verir."""
        msg = (
            "FFmpeg sisteminizde bulunamadı.\n\n"
            "Yüklemek için terminali açın ve şu komutu çalıştırın:\n"
            "sudo apt install ffmpeg  (Ubuntu/Debian)\n"
            "sudo dnf install ffmpeg  (Fedora)\n"
            "sudo pacman -S ffmpeg    (Arch)\n\n"
            "Yükledikten sonra 'Tekrar Dene' butonuna basın."
        )
        CTkMessagebox(title="Bilgi", message=msg, icon="info")

    def retry_check_action(self):
        """FFmpeg kontrolünü yeniden başlatır."""
        self.check_label.configure(text="⏳", text_color="#0084ff")
        self.info_label.configure(text="Kontrol ediliyor...", text_color="#a0a0a0")
        self.after(1000, self.check_ffmpeg)

    def switch_to_main_menu(self):
        """Splash ekranını kapatıp ana arayüze geçer."""
        self.splash_frame.destroy()
        self.build_main_interface()

    # ---------------------------------------------------------
    # BÖLÜM 2: ANA ARAYÜZ YAPILANDIRMASI
    # ---------------------------------------------------------
    def build_main_interface(self):
        """Ana kullanıcı arayüzünü oluşturur."""
        self.main_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Başlık Alanı
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(20, 10))
        ctk.CTkLabel(header_frame, text="Video İndirici", font=(APP_FONT, 24, "bold"), text_color="#ffffff").pack()

        # URL Giriş Alanı
        url_section = ctk.CTkFrame(self.main_frame, fg_color="#2a2a2a", corner_radius=10)
        url_section.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        url_section.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(url_section, text="Video Linki", font=(APP_FONT, 12, "bold"), text_color="#ffffff").grid(row=0, column=0, sticky="w", padx=15, pady=(15, 0))
        self.url_entry = ctk.CTkEntry(url_section, placeholder_text="Video veya Playlist bağlantısını yapıştırın...", height=40, border_color="#0084ff", text_color="#ffffff")
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(5, 15))
        
        self.fetch_button = ctk.CTkButton(url_section, text="Getir", command=self.start_fetch_formats, width=120, height=40, fg_color="#0084ff", hover_color="#0066cc", text_color="#ffffff")
        self.fetch_button.grid(row=1, column=2, padx=15, pady=(5, 15))

        # Video Bilgi Alanı
        self.info_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.info_frame.grid_columnconfigure(1, weight=1)

        self.thumb_label = ctk.CTkLabel(self.info_frame, text="") 
        self.thumb_label.grid(row=0, column=0, rowspan=3, padx=20, pady=10)
        
        self.video_title_label = ctk.CTkLabel(self.info_frame, text="", font=(APP_FONT, 16, "bold"), text_color="#ffffff", anchor="w", wraplength=500)
        self.video_title_label.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=(10, 0))
        
        self.video_meta_label = ctk.CTkLabel(self.info_frame, text="", font=(APP_FONT, 12), text_color="#aaaaaa", anchor="w")
        self.video_meta_label.grid(row=1, column=1, sticky="nw", padx=(0, 20), pady=(0, 5))

        # Navigasyon Butonları (Playlist için)
        self.nav_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        
        self.prev_btn = ctk.CTkButton(self.nav_frame, text="< Önceki", width=80, command=self.prev_video, state="disabled", fg_color="#444444")
        self.prev_btn.pack(side="left", padx=(0, 10))
        
        self.playlist_count_label = ctk.CTkLabel(self.nav_frame, text="", font=(APP_FONT, 12, "bold"))
        self.playlist_count_label.pack(side="left", padx=10)
        
        self.next_btn = ctk.CTkButton(self.nav_frame, text="Sonraki >", width=80, command=self.next_video, state="disabled", fg_color="#444444")
        self.next_btn.pack(side="left", padx=(10, 0))

        # Ayarlar Bölümü (Kalite ve Klasör Seçimi)
        settings_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        settings_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=5)
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)

        # Kalite Seçimi
        quality_section = ctk.CTkFrame(settings_frame, fg_color="#2a2a2a", corner_radius=10)
        quality_section.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=0)
        quality_section.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(quality_section, text="Kalite Seçimi", font=(APP_FONT, 12, "bold"), text_color="#ffffff").grid(row=0, column=0, sticky="w", padx=15, pady=(10, 0))
        
        self.format_menu = ctk.CTkOptionMenu(quality_section, values=["Önce Linki Getirin"], command=self.on_quality_change, state="disabled", height=35, text_color="#ffffff")
        self.format_menu.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 15))

        # Kayıt Yeri Seçimi
        path_section = ctk.CTkFrame(settings_frame, fg_color="#2a2a2a", corner_radius=10)
        path_section.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=0)
        path_section.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(path_section, text="Kayıt Yeri", font=(APP_FONT, 12, "bold"), text_color="#ffffff").grid(row=0, column=0, sticky="w", padx=15, pady=(10, 0))
        self.select_path_btn = ctk.CTkButton(path_section, text="📂 Değiştir", command=self.select_save_path, width=80, height=35, fg_color="#444444", hover_color="#555555", text_color="#ffffff")
        self.select_path_btn.grid(row=1, column=0, padx=15, pady=(5, 15))
        self.path_label = ctk.CTkLabel(path_section, text=os.path.basename(self.save_path), anchor="w", font=(APP_FONT, 11), text_color="#a0a0a0")
        self.path_label.grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=(5, 15))

        # İndirme Başlatma Butonu
        self.download_button = ctk.CTkButton(
            self.main_frame, 
            text="İNDİRMEYİ BAŞLAT", 
            command=self.start_download, 
            state="disabled", 
            height=55, 
            font=(APP_FONT, 15, "bold"), 
            fg_color="#00d26a", 
            hover_color="#00a852",
            text_color="#000000"
        )
        self.download_button.grid(row=4, column=0, sticky="ew", padx=20, pady=20)

        # İlerleme Durumu Alanı (Progress)
        self.progress_section = ctk.CTkFrame(self.main_frame, fg_color="#2a2a2a", corner_radius=10)
        self.progress_section.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(self.progress_section, text="Durum: Bekleniyor...", font=(APP_FONT, 12), text_color="#00d26a", anchor="w")
        self.status_label.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 0))

        self.percentage_label = ctk.CTkLabel(self.progress_section, text="0%", font=(APP_FONT, 12, "bold"), text_color="#0084ff")
        self.percentage_label.grid(row=0, column=1, sticky="e", padx=15, pady=(10, 0))

        self.progressbar = ctk.CTkProgressBar(self.progress_section, height=12, progress_color="#0084ff")
        self.progressbar.set(0)
        self.progressbar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(5, 15))

        self.speed_label = ctk.CTkLabel(self.progress_section, text="", font=(APP_FONT, 10), text_color="#aaaaaa", anchor="w")
        self.speed_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 10))

        # Alt Bilgi (Footer)
        self.main_frame.grid_rowconfigure(9, weight=1) 
        
        self.footer_label = ctk.CTkLabel(
            self.main_frame, 
            text="Emirhan Keser | Github", 
            font=(APP_FONT, 12), 
            text_color="#555555", 
            cursor="hand2"
        )
        self.footer_label.grid(row=10, column=0, pady=(20, 10))
        self.footer_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/KurKigal/Youtube-Video-Downloader"))

    # ---------------------------------------------------------
    # YARDIMCI FONKSİYONLAR
    # ---------------------------------------------------------
    def clean_ansi(self, text):
        """Metindeki ANSI kaçış kodlarını temizler (konsol çıktıları için)."""
        return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

    def select_save_path(self):
        """Kullanıcının indirme klasörünü seçmesini sağlar."""
        path = filedialog.askdirectory()
        if path:
            self.save_path = path
            self.path_label.configure(text=os.path.basename(path) if path else "...")

    def on_quality_change(self, choice):
        """Kalite seçimi değiştiğinde arayüzü günceller."""
        self.progressbar.set(0)
        self.percentage_label.configure(text="0%")
        self.speed_label.configure(text="")
        self.status_label.configure(text="İndirmeye Hazır", text_color="#ffffff")
        self.download_button.configure(state="normal", text="İNDİRMEYİ BAŞLAT", fg_color="#00d26a")
        self.progress_section.grid_forget()

    # ---------------------------------------------------------
    # VERİ ÇEKME & FORMAT İŞLEMLERİ
    # ---------------------------------------------------------
    def reset_ui_for_new_fetch(self):
        """Yeni bir arama öncesi arayüzü sıfırlar."""
        self.info_frame.grid_forget()
        self.progress_section.grid_forget()
        self.nav_frame.grid_forget() 
        self.prev_btn.configure(state="disabled")
        self.next_btn.configure(state="disabled")
        self.playlist_count_label.configure(text="")
        self.playlist_entries = []
        self.is_playlist = False
        self.current_video_index = 0
        self.format_menu.configure(state="disabled", values=["Önce Linki Getirin"])
        self.format_menu.set("Önce Linki Getirin")
        self.download_button.configure(state="disabled")

    def start_fetch_formats(self):
        """URL'den video bilgilerini çekme işlemini başlatır."""
        url = self.url_entry.get()
        if not url:
            CTkMessagebox(title="Uyarı", message="URL alanı boş olamaz!", icon="warning")
            return
        
        self.reset_ui_for_new_fetch()
        
        self.fetch_button.configure(state="disabled", text="Aranıyor...")
        threading.Thread(target=self._fetch_formats_thread, args=(url,), daemon=True).start()

    def _fetch_formats_thread(self, url):
        """Video bilgilerini arka planda çeken thread fonksiyonu."""
        if not self.running: return
        try:
            # Playlist hatalarını yok say
            ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': False, 'ignoreerrors': True} 
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            if not self.running: return

            if 'entries' in info:
                # Playlist durumu
                self.is_playlist = True
                # Bozuk/Silinmiş videoları filtrele
                self.playlist_entries = [x for x in info['entries'] if x is not None]
                self.current_video_index = 0
                if not self.playlist_entries:
                    raise Exception("Playlist boş veya videolar alınamadı.")
                
                self.current_video_data = self.playlist_entries[0]
                playlist_title = info.get('title', 'Playlist')
                self.after(0, lambda: self.setup_playlist_ui(playlist_title))
            else:
                # Tek video durumu
                self.is_playlist = False
                self.current_video_data = info
                self.playlist_entries = [info]
                self.after(0, self.update_video_card)

            self.prepare_formats(self.current_video_data)
            
        except Exception as e:
            self.after(0, lambda: CTkMessagebox(title="Hata", message=f"Video bulunamadı:\n{str(e)[:100]}", icon="cancel"))
        finally:
             if self.running:
                self.after(0, lambda: self.fetch_button.configure(state="normal", text="Getir"))

    def prepare_formats(self, info_data):
        """Video formatlarını ayrıştırır ve kullanıcıya sunulacak listeyi hazırlar."""
        formats = info_data.get('formats', [])
        self.format_map = {}
        display_list = []

        # MP3 Seçeneği
        mp3_text = "🎵 Sadece Ses (MP3)"
        display_list.append(mp3_text)
        self.format_map[mp3_text] = {'type': 'audio', 'id': 'bestaudio/best', 'ext': 'mp3'}

        # Video Seçenekleri
        seen = set()
        for f in reversed(formats):
            if f.get('vcodec') != 'none' and f.get('height'):
                h = f.get('height')
                # Sadece 144p ve üzeri kaliteleri al
                if h >= 144:
                    key = f"{h}p"
                    if key not in seen:
                        ext = f.get('ext')
                        txt = f"📺 {key} ({ext.upper()})"
                        
                        # Windows Media Player Fix: Sesi M4A (AAC) tercih et (Genel uyumluluk için Linux'ta da kalabilir)
                        fid = f"bestvideo[height={h}]+bestaudio[ext=m4a]/bestvideo[height={h}]+bestaudio/best[height={h}]"
                        
                        display_list.append(txt)
                        self.format_map[txt] = {'type': 'video', 'id': fid, 'ext': 'mp4'} 
                        seen.add(key)
        
        self.after(0, lambda: self.update_dropdown(display_list))

    # ---------------------------------------------------------
    # PLAYLIST & UI GÜNCELLEMELERİ
    # ---------------------------------------------------------
    def setup_playlist_ui(self, title):
        """Playlist modu için arayüzü hazırlar."""
        self.nav_frame.grid(row=2, column=1, sticky="w", padx=(0, 20)) 
        self.update_nav_buttons()
        self.update_video_card()
        CTkMessagebox(title="Playlist Bulundu", message=f"'{title}' bulundu.\nToplam {len(self.playlist_entries)} video.\n'Sonraki' butonu ile gezebilirsiniz.", icon="info")

    def update_video_card(self):
        """Seçili videonun bilgilerini (başlık, küçük resim vb.) günceller."""
        data = self.current_video_data
        if not data: return

        title = data.get('title', 'Video')
        duration = data.get('duration_string', '??:??')
        uploader = data.get('uploader', 'Bilinmiyor')
        thumb_url = data.get('thumbnail')

        if thumb_url:
            threading.Thread(target=self._download_thumbnail, args=(thumb_url, title, duration, uploader), daemon=True).start()
        else:
            self.update_info_labels(None, title, duration, uploader)

    def _download_thumbnail(self, url, title, duration, uploader):
        """Videoya ait küçük resmi indirir."""
        try:
            response = requests.get(url)
            img_data = BytesIO(response.content)
            pil_img = Image.open(img_data)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(160, 90))
            self.after(0, lambda: self.update_info_labels(ctk_img, title, duration, uploader))
        except: pass

    def update_info_labels(self, img, title, duration, uploader):
        """Video bilgi etiketlerini günceller."""
        if img: 
            self.thumb_label.configure(image=img)
            self.thumb_label.image = img
        self.video_title_label.configure(text=title)
        self.video_meta_label.configure(text=f"Süre: {duration}  |  Kanal: {uploader}")
        self.info_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)

    def update_dropdown(self, values):
        """Format seçeneklerini içeren menüyü günceller."""
        if values:
            self.format_menu.configure(values=values, state="normal")
            self.format_menu.set(values[0])
            self.on_quality_change(values[0])

    def update_nav_buttons(self):
        """Playlist butonlarının durumunu günceller."""
        total = len(self.playlist_entries)
        current = self.current_video_index + 1
        self.playlist_count_label.configure(text=f"{current} / {total}")
        
        state_prev = "normal" if self.current_video_index > 0 else "disabled"
        color_prev = "#0084ff" if self.current_video_index > 0 else "#444444"
        self.prev_btn.configure(state=state_prev, fg_color=color_prev)
            
        state_next = "normal" if self.current_video_index < total - 1 else "disabled"
        color_next = "#0084ff" if self.current_video_index < total - 1 else "#444444"
        self.next_btn.configure(state=state_next, fg_color=color_next)

    def next_video(self):
        """Bir sonraki videoya geçer."""
        if self.current_video_index < len(self.playlist_entries) - 1:
            self.current_video_index += 1
            self.current_video_data = self.playlist_entries[self.current_video_index]
            self.update_video_card()
            self.update_nav_buttons()

    def prev_video(self):
        """Bir önceki videoya geçer."""
        if self.current_video_index > 0:
            self.current_video_index -= 1
            self.current_video_data = self.playlist_entries[self.current_video_index]
            self.update_video_card()
            self.update_nav_buttons()

    # ---------------------------------------------------------
    # İNDİRME İŞLEMLERİ
    # ---------------------------------------------------------
    def _get_unique_filename(self, path, title, ext):
        """Dosya adı çakışmalarını önlemek için benzersiz bir dosya adı oluşturur."""
        clean_title = re.sub(r'[<>:"/\\|?*]', '', title).strip()
        filename = f"{clean_title}.{ext}"
        counter = 1
        full_path = os.path.join(path, filename)
        while os.path.exists(full_path):
            filename = f"{clean_title} ({counter}).{ext}"
            full_path = os.path.join(path, filename)
            counter += 1
        return full_path

    def start_download(self):
        """Seçilen ayarlarla indirme işlemini başlatır."""
        url = self.url_entry.get()
        sel = self.format_menu.get()
        if not url or sel not in self.format_map: return

        self.progress_section.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.download_button.configure(state="disabled")
        self.fetch_button.configure(state="disabled") # İndirme bitene kadar aramayı kapat
        
        cfg = self.format_map[sel]

        threading.Thread(target=self._download_manager, args=(url, cfg), daemon=True).start()

    def _download_manager(self, url, cfg):
        """İndirme listesini yöneten ve yt-dlp'yi çalıştıran ana thread."""
        videos_to_download = []
        if self.is_playlist:
            videos_to_download = self.playlist_entries
        else:
            videos_to_download = [self.current_video_data]

        total_videos = len(videos_to_download)
        
        for idx, video_data in enumerate(videos_to_download):
            if not self.running: break
            
            # Silinmiş videoları atla
            if not video_data: continue

            self.after(0, lambda: self.update_status(f"Video {idx+1}/{total_videos} İndiriliyor: {video_data.get('title')[:30]}...", "#0084ff"))
            
            vid_title = video_data.get('title', 'video')
            vid_url = video_data.get('webpage_url', video_data.get('url'))
            
            unique_fullpath = self._get_unique_filename(self.save_path, vid_title, cfg['ext'])
            base_name_without_ext = os.path.splitext(unique_fullpath)[0]

            opts = {
                'format': cfg['id'],
                'outtmpl': f"{base_name_without_ext}.%(ext)s",
                'progress_hooks': [self.progress_hook],
                'noplaylist': True, 
                'quiet': True,
                'no_warnings': True,
                'force_overwrites': True,
                'merge_output_format': 'mp4',
            }
            
            # Ses indirmeleri için post-processor
            if cfg['type'] == 'audio':
                opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]

            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([vid_url])
            except Exception as e:
                print(f"Hata ({vid_title}): {e}")

        if self.running:
            self.after(0, self.success_ui)
            self.after(0, lambda: self.download_button.configure(state="normal"))
            self.after(0, lambda: self.fetch_button.configure(state="normal", text="Getir"))

    def success_ui(self):
        """İndirme tamamlandığında arayüzü günceller."""
        self.status_label.configure(text="Tüm İndirmeler Tamamlandı! ✔", text_color="#00d26a")
        self.progressbar.set(1)
        self.percentage_label.configure(text="100%")
        self.speed_label.configure(text="")
        CTkMessagebox(title="Başarılı", message="İşlem tamamlandı.", icon="check")

    def progress_hook(self, d):
        """yt-dlp'den gelen indirme ilerleme verilerini işler."""
        if not self.running: return
        
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                percentage = downloaded / total if total else 0
                
                pct_text = f"{int(percentage * 100)}%"
                speed = self.clean_ansi(d.get('_speed_str', '...'))
                eta = self.clean_ansi(d.get('_eta_str', '...'))
                
                self.after(0, lambda: self.update_progress_ui(percentage, pct_text, speed, eta))
            except: pass

        elif d['status'] == 'finished':
            self.after(0, lambda: self.status_label.configure(text="Dönüştürülüyor/Kaydediliyor...", text_color="#00aaff"))

    def update_progress_ui(self, val, text, speed, eta):
        """İlerleme çubuğunu ve metinleri günceller."""
        if not self.running: return
        self.progressbar.set(val)
        self.percentage_label.configure(text=text)
        self.speed_label.configure(text=f"Hız: {speed}  |  Kalan: {eta}")

    def update_status(self, text, color):
        """Durum metnini günceller."""
        self.status_label.configure(text=f"Durum: {text}", text_color=color)

if __name__ == "__main__":
    app = YtDlpApp()

    app.mainloop()
