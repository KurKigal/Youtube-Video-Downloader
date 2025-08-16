:: debug.bat - Hata Ayıklama Modu
@echo off
chcp 65001 >nul
title Modern Video Downloader - Debug Mode

echo.
echo =======================================
echo 🐛 Modern Video Downloader - Debug
echo =======================================
echo.

echo 🔍 Sistem bilgileri kontrol ediliyor...
echo.

:: Windows sürümü
echo 💻 Windows Sürümü:
ver
echo.

:: Python bilgileri
echo 🐍 Python Bilgileri:
python --version 2>&1
python -c "import sys; print('Python Path:', sys.executable)"
echo.

:: Pip bilgileri
echo 📦 Pip Sürümü:
pip --version 2>&1
echo.

:: Yüklü paketler
echo 📋 Yüklü Python Paketleri:
pip list | findstr -i "pillow requests yt-dlp"
echo.

:: FFmpeg kontrolü
echo 🎵 FFmpeg Kontrolü:
ffmpeg -version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ FFmpeg mevcut
    ffmpeg -version 2>&1 | findstr "ffmpeg version"
) else (
    echo ❌ FFmpeg bulunamadı
)
echo.

:: Dosya kontrolü
echo 📁 Dosya Kontrolü:
if exist "video_downloader.py" (
    echo ✅ video_downloader.py mevcut
    for %%A in (video_downloader.py) do echo    Boyut: %%~zA bytes
) else (
    echo ❌ video_downloader.py bulunamadı
)
echo.

:: İndirme klasörü
set "download_dir=%USERPROFILE%\Downloads\VideoDownloader"
echo 📁 İndirme Klasörü:
if exist "%download_dir%" (
    echo ✅ %download_dir% mevcut
) else (
    echo ❌ %download_dir% bulunamadı
)
echo.

:: Paket testi
echo 🧪 Paket Testleri:
python -c "import PIL; print('✅ Pillow OK')" 2>&1
python -c "import requests; print('✅ Requests OK')" 2>&1
python -c "import yt_dlp; print('✅ yt-dlp OK')" 2>&1
python -c "import tkinter; print('✅ Tkinter OK')" 2>&1
echo.

echo 🚀 Debug modunda uygulama başlatılıyor...
echo (Hata mesajları gösterilecek)
echo.

python video_downloader.py

echo.
echo Debug tamamlandı.
pause