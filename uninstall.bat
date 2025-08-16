:: uninstall.bat - Kaldırma Scripti
@echo off
chcp 65001 >nul
title Modern Video Downloader - Kaldırma

echo.
echo =========================================
echo 🗑️  Modern Video Downloader Kaldırma
echo =========================================
echo.

set /p "confirm=Uygulamayı kaldırmak istediğinizden emin misiniz? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo İptal edildi.
    pause
    exit /b 0
)

echo.
echo 🗑️  Uygulama kaldırılıyor...

:: Masaüstü kısayolunu sil
set "shortcut=%USERPROFILE%\Desktop\Modern Video Downloader.lnk"
if exist "%shortcut%" (
    del "%shortcut%"
    echo ✅ Masaüstü kısayolu silindi
)

:: Python paketlerini kaldır (isteğe bağlı)
set /p "remove_packages=Python paketlerini de kaldırmak istiyor musunuz? (Y/N): "
if /i "%remove_packages%"=="Y" (
    echo 📦 Python paketleri kaldırılıyor...
    pip uninstall -y yt-dlp
    pip uninstall -y Pillow
    pip uninstall -y requests
    echo ✅ Paketler kaldırıldı
)

:: İndirme klasörünü sil (isteğe bağlı)
set "download_dir=%USERPROFILE%\Downloads\VideoDownloader"
if exist "%download_dir%" (
    set /p "remove_downloads=İndirilen dosyaları da silmek istiyor musunuz? (Y/N): "
    if /i "!remove_downloads!"=="Y" (
        rmdir /s /q "%download_dir%"
        echo ✅ İndirme klasörü silindi
    )
)

echo.
echo ✅ Kaldırma işlemi tamamlandı!
echo.
pause