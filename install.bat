:: install.bat - Kurulum Scripti
@echo off
chcp 65001 >nul
title Modern Video Downloader - Kurulum

echo.
echo ====================================
echo 🚀 Modern Video Downloader Kurulumu
echo ====================================
echo.

:: Python kontrolü
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python bulunamadı! Lütfen Python 3.8+ yükleyin.
    echo 📥 İndirme linki: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    echo ✅ Python bulundu
)

:: Pip kontrolü
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pip bulunamadı!
    pause
    exit /b 1
) else (
    echo ✅ Pip bulundu
)

echo.
echo 📦 Gerekli paketler yükleniyor...
echo.

:: Python paketlerini yükle
pip install Pillow>=9.0.0
if %errorlevel% neq 0 (
    echo ❌ Pillow yükleme hatası!
    pause
    exit /b 1
)

pip install requests>=2.28.0
if %errorlevel% neq 0 (
    echo ❌ Requests yükleme hatası!
    pause
    exit /b 1
)

pip install yt-dlp>=2023.12.30
if %errorlevel% neq 0 (
    echo ❌ yt-dlp yükleme hatası!
    pause
    exit /b 1
)

echo.
echo ✅ Tüm paketler başarıyla yüklendi!
echo.

:: FFmpeg kontrolü
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  FFmpeg bulunamadı (MP3 dönüştürme için gerekli)
    echo 📥 İndirme linki: https://ffmpeg.org/download.html#build-windows
    echo 💡 FFmpeg'i PATH'e eklemeyi unutmayın
    echo.
) else (
    echo ✅ FFmpeg bulundu
)

:: İndirme klasörü oluştur
set "download_dir=%USERPROFILE%\Downloads\VideoDownloader"
if not exist "%download_dir%" (
    mkdir "%download_dir%"
    echo ✅ İndirme klasörü oluşturuldu: %download_dir%
)

:: Kısayol oluştur
echo 🔗 Masaüstü kısayolu oluşturuluyor...

set "desktop=%USERPROFILE%\Desktop"
set "shortcut=%desktop%\Modern Video Downloader.lnk"
set "target=%cd%\run.bat"

:: PowerShell ile kısayol oluştur
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcut%'); $Shortcut.TargetPath = '%target%'; $Shortcut.WorkingDirectory = '%cd%'; $Shortcut.Save()" >nul 2>&1

if exist "%shortcut%" (
    echo ✅ Masaüstü kısayolu oluşturuldu
) else (
    echo ⚠️  Kısayol oluşturulamadı (normal kullanıcı sorunu değil)
)

echo.
echo 🎉 Kurulum tamamlandı!
echo.
echo 📁 İndirme klasörü: %download_dir%
echo 🖥️  Uygulamayı başlatmak için: run.bat çalıştırın
echo 🔗 Masaüstünde kısayol oluşturuldu
echo.
echo 💡 İlk çalıştırma için run.bat dosyasını çift tıklayın
echo.
pause
