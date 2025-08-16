:: quick_start.bat - Hızlı Başlangıç (Tek dosyada her şey)
@echo off
chcp 65001 >nul
title Modern Video Downloader - Hızlı Başlangıç

echo.
echo ==============================================
echo 🚀 Modern Video Downloader - Hızlı Başlangıç
echo ==============================================
echo.

:: Python kontrolü
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python bulunamadı!
    echo 📥 Python indirmek için: https://www.python.org/downloads/
    echo 💡 Kurulum sırasında "Add to PATH" seçeneğini işaretleyin
    pause
    exit /b 1
)

:: Ana dosya kontrolü
if not exist "video_downloader.py" (
    echo ❌ video_downloader.py dosyası bulunamadı!
    pause
    exit /b 1
)

:: Paketleri kontrol et ve yükle
echo 📦 Gerekli paketler kontrol ediliyor ve yükleniyor...

python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📥 Pillow yükleniyor...
    pip install Pillow
)

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📥 Requests yükleniyor...
    pip install requests
)

python -c "import yt_dlp" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📥 yt-dlp yükleniyor...
    pip install yt-dlp
)

echo ✅ Hazırlık tamamlandı!
echo.

:: Uygulamayı başlat
echo 🎬 Uygulama başlatılıyor...
python video_downloader.py

if %errorlevel% neq 0 (
    echo ❌ Hata oluştu!
    pause
)
