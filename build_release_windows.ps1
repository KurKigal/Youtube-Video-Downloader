$ErrorActionPreference = "Stop"

Write-Host "[1/5] Build dependencies" -ForegroundColor Cyan
python -m pip install -r requirements-build.txt

Write-Host "[2/5] Tests" -ForegroundColor Cyan
python -m pytest

Write-Host "[3/5] Cleaning old build" -ForegroundColor Cyan
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

Write-Host "[4/5] Building Windows executable" -ForegroundColor Cyan
python -m PyInstaller --noconfirm --clean YouTubeDownloaderV2.spec

$releaseRoot = Join-Path $PSScriptRoot "release\YouTube-Downloader-V2-Windows-x64"
Remove-Item -Recurse -Force $releaseRoot -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $releaseRoot | Out-Null
Copy-Item (Join-Path $PSScriptRoot "dist\YouTube-Downloader-V2.exe") $releaseRoot
Copy-Item (Join-Path $PSScriptRoot "README.md") $releaseRoot
Copy-Item (Join-Path $PSScriptRoot "LICENSE") $releaseRoot

@"
OPTIONAL PORTABLE DEPENDENCIES
==============================

The application first checks a local 'bin' directory next to the executable,
then the system PATH. To make a local/private portable package, create 'bin'
and place ffmpeg.exe, ffprobe.exe and deno.exe there.

For public redistribution, review and comply with the licenses of the exact
third-party binaries you choose to bundle. This build script intentionally does
not redistribute them automatically.
"@ | Set-Content -Encoding UTF8 (Join-Path $releaseRoot "PORTABLE-DEPS.txt")

Write-Host "[5/5] Creating ZIP" -ForegroundColor Cyan
$zip = Join-Path $PSScriptRoot "release\YouTube-Downloader-V2-Windows-x64.zip"
Remove-Item -Force $zip -ErrorAction SilentlyContinue
Compress-Archive -Path "$releaseRoot\*" -DestinationPath $zip -CompressionLevel Optimal

Write-Host "" 
Write-Host "Release ready:" -ForegroundColor Green
Write-Host $zip
