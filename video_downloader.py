import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
import json
import uuid
import subprocess
import webbrowser
from datetime import datetime
import requests
from PIL import Image, ImageTk
import io
import random
import yt_dlp
from urllib.parse import urlparse

class Config:
    """Uygulama konfigürasyonu"""
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.video_downloader")
        self.config_file = os.path.join(self.config_dir, "config.json")
        os.makedirs(self.config_dir, exist_ok=True)
        self.load_config()
    
    def load_config(self):
        """Konfigürasyonu yükle"""
        default_config = {
            "download_dir": os.path.join(os.path.expanduser("~"), "Downloads", "VideoDownloader"),
            "preferred_quality": "720p",
            "last_window_geometry": "900x640+100+100",
            "theme": "modern"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
        except:
            pass
        
        self.config = default_config
        self.save_config()
    
    def save_config(self):
        """Konfigürasyonu kaydet"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()

class AntiDetection:
    """IP ban ve bot detection'a karşı koruma"""
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    @staticmethod
    def get_random_user_agent():
        return random.choice(AntiDetection.USER_AGENTS)
    
    @staticmethod
    def get_headers():
        return {
            'User-Agent': AntiDetection.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    @staticmethod
    def add_random_delay():
        """Random delay bot detection'ı önlemek için"""
        time.sleep(random.uniform(1, 3))

class VideoDownloader:
    """Güçlendirilmiş video indirici"""
    def __init__(self, download_dir):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.active_downloads = {}
        self.find_ffmpeg()
    
    def find_ffmpeg(self):
        """FFmpeg yolunu bul"""
        possible_paths = [
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
            r'C:\ffmpeg\bin\ffmpeg.exe',
            'ffmpeg.exe'
        ]
        
        self.ffmpeg_path = None
        for path in possible_paths:
            try:
                result = subprocess.run([path, '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.ffmpeg_path = path
                    break
            except:
                continue
    
    def get_ydl_opts(self, format_selector='best', progress_hook=None):
        """Anti-detection yt-dlp seçenekleri"""
        opts = {
            'format': format_selector,
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            # Anti-detection
            'user_agent': AntiDetection.get_random_user_agent(),
            'referer': 'https://www.youtube.com/',
            'http_headers': AntiDetection.get_headers(),
            # Rate limiting ve retry
            'sleep_interval': random.uniform(1, 3),
            'max_sleep_interval': 10,
            'retries': 5,
            'fragment_retries': 5,
            'extract_flat': False,
            # Proxy (gerekirse)
            'proxy': None,
            # FFmpeg
            'ffmpeg_location': self.ffmpeg_path,
        }
        if progress_hook:
            opts['progress_hooks'] = [progress_hook]
        return opts
    
    def get_video_info(self, url):
        """Video bilgilerini güvenli şekilde al"""
        try:
            AntiDetection.add_random_delay()
            ydl_opts = self.get_ydl_opts('best')
            ydl_opts['quiet'] = True
            ydl_opts['extract_flat'] = False
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_info = {
                    'title': info.get('title', 'Başlık bulunamadı'),
                    'uploader': info.get('uploader', 'Bilinmiyor'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', url),
                    'formats': self.get_available_formats(info)
                }
                return video_info
        except Exception as e:
            raise Exception(f"Video bilgisi alınamadı: {str(e)}")
    
    def get_available_formats(self, info):
        """Mevcut formatları listele"""
        formats = [
            {
                'format_id': 'best[height<=720]',
                'quality': '720p HD',
                'type': 'video+audio',
                'ext': 'mp4'
            },
            {
                'format_id': 'best[height<=480]',
                'quality': '480p',
                'type': 'video+audio', 
                'ext': 'mp4'
            },
            {
                'format_id': 'best[height<=360]',
                'quality': '360p',
                'type': 'video+audio',
                'ext': 'mp4'
            },
            {
                'format_id': 'bestaudio',
                'quality': 'En İyi Ses (MP3)',
                'type': 'audio',
                'ext': 'mp3'
            }
        ]
        return formats
    
    def start_download(self, url, format_id, quality, progress_callback=None, status_callback=None):
        """İndirmeyi başlat"""
        download_id = str(uuid.uuid4())
        self.active_downloads[download_id] = {
            'status': 'başlatıldı',
            'progress': 0,
            'url': url,
            'format_id': format_id,
            'quality': quality,
            'start_time': datetime.now(),
            'filename': '',
            'error': None
        }
        
        def progress_hook(d):
            try:
                if download_id not in self.active_downloads:
                    return
                status = d['status']
                if status == 'downloading':
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    if total_bytes > 0:
                        progress = (downloaded_bytes / total_bytes) * 100
                    else:
                        progress = 50
                    filename = os.path.basename(d.get('filename', '')) if d.get('filename') else 'İndiriliyor...'
                    self.active_downloads[download_id].update({
                        'status': 'indiriliyor',
                        'progress': round(progress, 1),
                        'filename': filename
                    })
                    if progress_callback:
                        progress_callback(progress, filename)
                elif status == 'finished':
                    filename = os.path.basename(d.get('filename', '')) if d.get('filename') else 'Tamamlandı'
                    self.active_downloads[download_id].update({
                        'status': 'tamamlandı',
                        'progress': 100,
                        'filename': filename
                    })
                    if status_callback:
                        status_callback('tamamlandı', filename)
            except Exception as e:
                print(f"Progress hook hatası: {e}")
        
        def download_thread():
            try:
                AntiDetection.add_random_delay()
                ydl_opts = self.get_ydl_opts(format_id, progress_hook)
                # MP3 için özel ayarlar
                if format_id == 'bestaudio' or 'MP3' in quality.upper():
                    ydl_opts.update({
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    })
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                if download_id in self.active_downloads and self.active_downloads[download_id]['status'] != 'tamamlandı':
                    self.active_downloads[download_id].update({
                        'status': 'tamamlandı',
                        'progress': 100,
                        'filename': 'Video başarıyla indirildi'
                    })
                    if status_callback:
                        status_callback('tamamlandı', 'Video başarıyla indirildi')
            except Exception as e:
                error_msg = str(e)
                if download_id in self.active_downloads:
                    self.active_downloads[download_id].update({
                        'status': 'hata',
                        'error': error_msg,
                        'progress': 0
                    })
                if status_callback:
                    status_callback('hata', error_msg)
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
        return download_id

class ModernVideoDownloaderGUI:
    """Modern Windows GUI"""
    def __init__(self):
        self.config = Config()
        self.downloader = VideoDownloader(self.config.get('download_dir'))
        
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        self.setup_layout()
        
        self.current_video_info = None
        self.download_in_progress = False
        
        # Widget referansları başlangıç değerleri
        self.thumbnail_label = None
        self.video_title = None  
        self.video_details = None
        self.progress_label = None
        self.progress_bar = None
        self.download_btn = None
    
    def setup_window(self):
        """Pencere ayarları"""
        self.root.title("Modern Video Downloader")
        self.root.geometry(self.config.get('last_window_geometry', '900x640+100+100'))
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(True, True)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Modern stil ayarları"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.colors = {
            'bg': '#1e1e1e',
            'card_bg': '#2d2d2d',
            'primary': '#0078d4',
            'success': '#107c10',
            'error': '#d13438',
            'text': '#ffffff',
            'text_secondary': '#b3b3b3',
            'border': '#404040'
        }
        self.style.configure('Modern.TFrame', background=self.colors['bg'])
        self.style.configure('Card.TFrame', background=self.colors['card_bg'], relief='flat', borderwidth=1)
        self.style.configure('Modern.TLabel', background=self.colors['bg'], foreground=self.colors['text'])
        self.style.configure('Card.TLabel', background=self.colors['card_bg'], foreground=self.colors['text'])
        self.style.configure('Title.TLabel', background=self.colors['card_bg'], foreground=self.colors['text'], font=('Segoe UI', 14, 'bold'))
        self.style.configure('Modern.TEntry', fieldbackground=self.colors['card_bg'], foreground=self.colors['text'], borderwidth=1)
        self.style.configure('Modern.TButton', background=self.colors['primary'], foreground='white', padding=(20, 10))
        self.style.map('Modern.TButton', background=[('active', '#106ebe'), ('pressed', '#005a9e')])
    
    def create_widgets(self):
        """Widget'ları oluştur"""
        # Ana frame
        self.main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        # Header
        self.header_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        self.settings_btn = tk.Button(
            self.header_frame,
            text="⚙️",
            font=('Segoe UI', 14),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            border=0,
            cursor='hand2',
            command=self.show_settings_menu,
            relief='flat',
            padx=10,
            pady=5
        )
        # URL section
        self.url_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        self.url_label = ttk.Label(
            self.url_frame, 
            text="Video URL'sini girin:",
            style='Card.TLabel',
            font=('Segoe UI', 11, 'bold')
        )
        # URL satırı için alt frame'i create_widgets içinde oluşturuyoruz
        self.url_input_row = tk.Frame(self.url_frame, bg=self.colors['card_bg'])
        self.url_entry = tk.Entry(
            self.url_input_row,
            font=('Segoe UI', 11),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief='flat',
            bd=5
        )
        self.fetch_btn = tk.Button(
            self.url_input_row,
            text="Video Bilgisi Al",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['primary'],
            fg='white',
            border=0,
            cursor='hand2',
            command=self.fetch_video_info,
            relief='flat',
            padx=20,
            pady=8
        )
        # Video info section (başlangıçta boş)
        self.info_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        # Format selection section (başlangıçta boş)
        self.format_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        self.format_label = None
        self.format_var = tk.StringVar()
        self.format_options = []
        # Download section (başlangıçta boş ama frame mevcut OLMALI)
        self.download_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        # Progress section (başlangıçta boş ama frame mevcut OLMALI)
        self.progress_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
    
    def setup_layout(self):
        """Layout düzenlemesi"""
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        # Header
        self.header_frame.pack(fill='x', pady=(0, 20))
        self.settings_btn.pack(side='right')
        # URL section
        self.url_frame.pack(fill='x', pady=(0, 20), padx=10, ipady=20)
        self.url_label.pack(anchor='w', padx=20, pady=(20, 5))
        self.url_input_row.pack(fill='x', padx=20, pady=(0, 20))
        self.url_entry.pack(side='left', fill='x', expand=True, ipady=8)
        self.fetch_btn.pack(side='right', padx=(10, 0))
        # Diğer bölümler dinamik olarak gösterilecek
        # self.info_frame.pack(...)
        # self.format_frame.pack(...)
        # self.download_frame.pack(...)
        # self.progress_frame.pack(...)
    
    def show_settings_menu(self):
        """Ayarlar menüsünü göster"""
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors['card_bg'], fg=self.colors['text'])
        menu.add_command(
            label=f"📁 İndirme Konumu: {os.path.basename(self.config.get('download_dir'))}",
            command=self.select_download_dir
        )
        menu.add_separator()
        menu.add_command(label="👨‍💻 Yapımcı", command=self.open_github)
        try:
            menu.tk_popup(self.settings_btn.winfo_rootx(), 
                          self.settings_btn.winfo_rooty() + self.settings_btn.winfo_height())
        finally:
            menu.grab_release()
    
    def select_download_dir(self):
        """İndirme dizini seç"""
        directory = filedialog.askdirectory(
            title="İndirme Konumunu Seçin",
            initialdir=self.config.get('download_dir')
        )
        if directory:
            self.config.set('download_dir', directory)
            self.downloader = VideoDownloader(directory)
            messagebox.showinfo("Başarılı", f"İndirme konumu güncellendi:\n{directory}")
    
    def open_github(self):
        """GitHub sayfasını aç"""
        webbrowser.open("https://github.com/KurKigal")
    
    def fetch_video_info(self):
        """Video bilgilerini getir"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Hata", "Lütfen bir URL girin")
            return
        if not self.is_valid_url(url):
            messagebox.showerror("Hata", "Geçerli bir video URL'si girin")
            return
        # UI
        self.fetch_btn.config(state='disabled', text="Yükleniyor...")
        self.hide_video_info()
        self.hide_progress()
        self.clear_frame_safely(self.format_frame)
        self.format_frame.pack_forget()
        self.clear_frame_safely(self.download_frame)
        self.download_frame.pack_forget()
        def fetch_thread():
            try:
                video_info = self.downloader.get_video_info(url)
                self.root.after(0, lambda: self.display_video_info(video_info))
            except Exception as e:
                self.root.after(0, lambda: self.handle_fetch_error(str(e)))
        threading.Thread(target=fetch_thread, daemon=True).start()
    
    def is_valid_url(self, url):
        """URL geçerliliğini kontrol et"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def display_video_info(self, video_info):
        """Video bilgilerini göster"""
        self.current_video_info = video_info
        self.show_video_info()
        # Widget'lar oluşturulduktan biraz sonra doldur
        self.root.after(50, lambda: self.update_video_display(video_info))
        # Format seçenekleri
        self.create_format_options(video_info['formats'])
        self.fetch_btn.config(state='normal', text="Video Bilgisi Al")
    
    def update_video_display(self, video_info):
        """Video gösterimini güncelle"""
        try:
            self.load_thumbnail(video_info.get('thumbnail', ''))
            if self.video_title and self.video_title.winfo_exists():
                self.video_title.config(text=video_info['title'])
            if self.video_details and self.video_details.winfo_exists():
                details = f"👤 {video_info['uploader']}\n"
                if video_info['duration']:
                    details += f"⏱️ {self.format_duration(video_info['duration'])}\n"
                if video_info['view_count']:
                    details += f"👁️ {self.format_number(video_info['view_count'])} görüntüleme"
                self.video_details.config(text=details)
        except Exception as e:
            print(f"Video display güncelleme hatası: {e}")
    
    def load_thumbnail(self, thumbnail_url):
        """Thumbnail yükle"""
        def load_image():
            try:
                if thumbnail_url and self.thumbnail_label and self.thumbnail_label.winfo_exists():
                    response = requests.get(thumbnail_url, timeout=10)
                    image = Image.open(io.BytesIO(response.content))
                    image = image.resize((150, 100), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    def update_thumbnail():
                        try:
                            if self.thumbnail_label and self.thumbnail_label.winfo_exists():
                                self.thumbnail_label.config(image=photo)
                                self.thumbnail_label.image = photo
                        except:
                            pass
                    self.root.after(0, update_thumbnail)
            except Exception as e:
                print(f"Thumbnail yükleme hatası: {e}")
        if thumbnail_url:
            threading.Thread(target=load_image, daemon=True).start()
    
    def create_format_options(self, formats):
        """Format seçenekleri oluştur"""
        self.clear_frame_safely(self.format_frame)
        self.format_label = ttk.Label(
            self.format_frame,
            text="İndirme formatını seçin:",
            style='Card.TLabel',
            font=('Segoe UI', 11, 'bold')
        )
        self.format_label.pack(anchor='w', padx=20, pady=(20, 10))
        self.format_options = formats
        self.format_var.set("")  # başlangıçta seçili format olmasın
        for i, fmt in enumerate(formats):
            rb = tk.Radiobutton(
                self.format_frame,
                text=f"{fmt['quality']} ({fmt['ext'].upper()})",
                variable=self.format_var,
                value=str(i),
                bg=self.colors['card_bg'],
                fg=self.colors['text'],
                selectcolor=self.colors['primary'],
                font=('Segoe UI', 10),
                command=self.on_format_select
            )
            rb.pack(anchor='w', padx=40, pady=2)
        self.format_frame.pack(fill='x', pady=(0, 20), padx=10)
        self.show_download_button()
    
    def on_format_select(self):
        """Format seçildiğinde"""
        self.update_download_button()
    
    def update_download_button(self):
        """İndirme butonunun durumunu güncelle"""
        if self.download_btn and self.download_btn.winfo_exists():
            if self.format_var.get():
                self.download_btn.config(text="İndir", state='normal', bg=self.colors['success'])
            else:
                self.download_btn.config(text="Format Seçin", state='disabled', bg=self.colors['success'])
    
    def show_download_button(self):
        """İndirme butonunu göster"""
        self.clear_frame_safely(self.download_frame)
        download_content = tk.Frame(self.download_frame, bg=self.colors['card_bg'])
        download_content.pack(fill='x', padx=20, pady=20)
        self.download_btn = tk.Button(
            download_content,
            text="Format Seçin",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['success'],
            fg='white',
            border=0,
            cursor='hand2',
            command=self.start_download,
            relief='flat',
            padx=40,
            pady=12,
            state='disabled'
        )
        self.download_btn.pack()
        self.download_frame.pack(fill='x', pady=(0, 20), padx=10)
    
    def start_download(self):
        """İndirmeyi başlat"""
        if not self.current_video_info or not self.format_var.get():
            messagebox.showwarning("Uyarı", "Lütfen bir format seçin")
            return
        if self.download_in_progress:
            messagebox.showwarning("Uyarı", "Bir indirme zaten devam ediyor")
            return
        try:
            format_index = int(self.format_var.get())
            selected_format = self.format_options[format_index]
            self.download_in_progress = True
            if self.download_btn and self.download_btn.winfo_exists():
                self.download_btn.config(state='disabled', text="İndiriliyor...")
            self.show_progress()
            url = self.url_entry.get().strip()
            self.downloader.start_download(
                url=url,
                format_id=selected_format['format_id'],
                quality=selected_format['quality'],
                progress_callback=self.update_progress,
                status_callback=self.download_finished
            )
        except Exception as e:
            messagebox.showerror("Hata", f"İndirme başlatılamadı: {str(e)}")
            self.download_in_progress = False
            if self.download_btn and self.download_btn.winfo_exists():
                self.download_btn.config(state='normal')
                self.update_download_button()
            self.hide_progress()
    
    def update_progress(self, progress, filename):
        """Progress güncelle"""
        try:
            if self.progress_bar and self.progress_bar.winfo_exists():
                self.progress_bar['value'] = progress
            if self.progress_label and self.progress_label.winfo_exists():
                self.progress_label.config(text=f"İndiriliyor: {filename} (%{progress:.1f})")
        except Exception as e:
            print(f"Progress güncelleme hatası: {e}")
    
    def download_finished(self, status, message):
        """İndirme tamamlandığında"""
        self.download_in_progress = False
        if self.download_btn and self.download_btn.winfo_exists():
            self.download_btn.config(state='normal')
            self.update_download_button()
        try:
            if status == 'tamamlandı':
                if self.progress_label and self.progress_label.winfo_exists():
                    self.progress_label.config(text=f"✅ Tamamlandı: {message}")
                if self.progress_bar and self.progress_bar.winfo_exists():
                    self.progress_bar['value'] = 100
                result = messagebox.askyesno(
                    "İndirme Tamamlandı", 
                    "Video başarıyla indirildi!\n\nİndirme klasörünü açmak ister misiniz?"
                )
                if result:
                    try:
                        os.startfile(self.config.get('download_dir'))
                    except:
                        webbrowser.open(self.config.get('download_dir'))
            else:
                if self.progress_label and self.progress_label.winfo_exists():
                    self.progress_label.config(text=f"❌ Hata: {message}")
                messagebox.showerror("İndirme Hatası", message)
                self.hide_progress()
        except Exception as e:
            print(f"Download finished güncelleme hatası: {e}")
    
    def show_video_info(self):
        """Video bilgi bölümünü göster"""
        self.clear_frame_safely(self.info_frame)
        info_content_frame = tk.Frame(self.info_frame, bg=self.colors['card_bg'])
        info_content_frame.pack(fill='x', padx=20, pady=20)
        left_frame = tk.Frame(info_content_frame, bg=self.colors['card_bg'])
        left_frame.pack(side='left', padx=(0, 20))
        self.thumbnail_label = tk.Label(
            left_frame,
            bg=self.colors['card_bg'],
            width=20,
            height=10,
            text="📺",
            font=('Segoe UI', 24),
            fg=self.colors['text_secondary']
        )
        self.thumbnail_label.pack()
        right_frame = tk.Frame(info_content_frame, bg=self.colors['card_bg'])
        right_frame.pack(side='left', fill='x', expand=True)
        self.video_title = ttk.Label(
            right_frame,
            text="",
            style='Title.TLabel',
            wraplength=500
        )
        self.video_title.pack(anchor='w', pady=(0, 10))
        self.video_details = ttk.Label(
            right_frame,
            text="",
            style='Card.TLabel',
            font=('Segoe UI', 9)
        )
        self.video_details.pack(anchor='w')
        self.info_frame.pack(fill='x', pady=(0, 20), padx=10)
    
    def clear_frame_safely(self, frame):
        """Frame'i güvenli şekilde temizle"""
        try:
            if frame and hasattr(frame, 'winfo_children'):
                for widget in frame.winfo_children():
                    try:
                        if hasattr(widget, 'destroy'):
                            widget.destroy()
                    except:
                        pass
        except:
            pass
    
    def hide_video_info(self):
        """Video bilgi bölümünü gizle"""
        self.clear_frame_safely(self.info_frame)
        self.info_frame.pack_forget()
        self.thumbnail_label = None
        self.video_title = None
        self.video_details = None
    
    def show_progress(self):
        """Progress bölümünü göster"""
        self.clear_frame_safely(self.progress_frame)
        progress_content = tk.Frame(self.progress_frame, bg=self.colors['card_bg'])
        progress_content.pack(fill='x', padx=20, pady=20)
        self.progress_label = ttk.Label(
            progress_content,
            text="İndirme başlatılıyor...",
            style='Card.TLabel',
            font=('Segoe UI', 10)
        )
        self.progress_label.pack(anchor='w', pady=(0, 10))
        self.progress_bar = ttk.Progressbar(
            progress_content,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(fill='x')
        self.progress_frame.pack(fill='x', padx=10, pady=(0, 20))
    
    def hide_progress(self):
        """Progress bölümünü gizle"""
        self.clear_frame_safely(self.progress_frame)
        self.progress_frame.pack_forget()
        self.progress_label = None
        self.progress_bar = None
    
    def handle_fetch_error(self, error_message):
        """Video getirme hatası"""
        self.fetch_btn.config(state='normal', text="Video Bilgisi Al")
        messagebox.showerror("Hata", f"Video bilgisi alınamadı:\n{error_message}")
    
    def format_duration(self, seconds):
        """Süreyi formatla"""
        if not seconds:
            return "Bilinmiyor"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def format_number(self, num):
        """Sayıları formatla"""
        try:
            num = int(num)
        except:
            return str(num)
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return str(num)
    
    def on_closing(self):
        """Uygulama kapatılırken"""
        self.config.set('last_window_geometry', self.root.geometry())
        # Tüm threadler daemon olduğu için pencere kapanınca sonlanır.
        self.root.destroy()
    
    def run(self):
        """Uygulamayı başlat"""
        self.root.mainloop()

# Requirements.txt için önerilen paketler
REQUIREMENTS = """
Pillow>=9.0.0
requests>=2.28.0
yt-dlp>=2023.12.30
"""

def check_dependencies():
    """Gerekli bağımlılıkları kontrol et"""
    required_packages = ['PIL', 'requests', 'yt_dlp']
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    if missing_packages:
        print("❌ Eksik paketler tespit edildi:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nGerekli paketleri yüklemek için:")
        print("pip install Pillow requests yt-dlp")
        return False
    return True

def main():
    """Ana fonksiyon"""
    print("🚀 Modern Video Downloader başlatılıyor...")
    if not check_dependencies():
        input("\nEnter tuşuna basarak çıkın...")
        return
    try:
        app = ModernVideoDownloaderGUI()
        print("✅ GUI başarıyla yüklendi")
        app.run()
    except Exception as e:
        print(f"❌ Uygulama başlatma hatası: {e}")
        input("\nEnter tuşuna basarak çıkın...")

if __name__ == "__main__":
    main()
