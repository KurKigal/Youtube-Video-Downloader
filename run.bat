:: run.bat - Uygulama Başlatıcı
@echo off
chcp 65001 >nul
title Modern Video Downloader

echo.
echo ==========================================
echo 🎬 Modern Video Downloader başlatılıyor...
echo ==========================================
echo.

:: Python kontrolü
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python bulunamadı!
    echo 💡 Lütfen önce install.bat dosyasını çalıştırın
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✅ Python %%i bulundu
)

:: Gerekli paketleri kontrol et
echo 🔍 Gerekli paketler kontrol ediliyor...

python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pillow paketi bulunamadı!
    echo 💡 install.bat dosyasını çalıştırın
    pause
    exit /b 1
)

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Requests paketi bulunamadı!
    echo 💡 install.bat dosyasını çalıştırın
    pause
    exit /b 1
)

python -c "import yt_dlp" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ yt-dlp paketi bulunamadı!
    echo 💡 install.bat dosyasını çalıştırın
    pause
    exit /b 1
)

echo ✅ Tüm paketler mevcut

:: video_downloader.py dosyası var mı kontrol et
if not exist "video_downloader.py" (
    echo ❌ video_downloader.py dosyası bulunamadı!
    echo 💡 Ana Python dosyasının bu klasörde olduğundan emin olun
    pause
    exit /b 1
)

echo ✅ Ana dosya bulundu

:: İndirme klasörü var mı kontrol et
set "download_dir=%USERPROFILE%\Downloads\VideoDownloader"
if not exist "%download_dir%" (
    echo 📁 İndirme klasörü oluşturuluyor...
    mkdir "%download_dir%"
)

echo ✅ İndirme klasörü hazır: %download_dir%

:: FFmpeg kontrolü (uyarı olarak)
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  FFmpeg bulunamadı (MP3 dönüştürme sınırlı olacak)
) else (
    echo ✅ FFmpeg mevcut
)

echo.
echo 🚀 Uygulama başlatılıyor...
echo ⏹️  Kapatmak için pencereyi kapatın
echo.

:: Ana uygulamayı çalıştır
python video_downloader.py

:: Hata kontrolü
if %errorlevel% neq 0 (
    echo.
    echo ❌ Uygulama çalıştırma hatası!
    echo.
    echo 🔧 Olası çözümler:
    echo 1. install.bat dosyasını tekrar çalıştırın
    echo 2. Python'u yeniden yükleyin: https://www.python.org/downloads/
    echo 3. video_downloader.py dosyasının bu klasörde olduğunu kontrol edin
    echo.
    pause
) else (
    echo.
    echo ✅ Uygulama normal şekilde kapatıldı
)
