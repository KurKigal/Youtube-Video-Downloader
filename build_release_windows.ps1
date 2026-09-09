$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$PytestTemp = Join-Path $ProjectRoot ".pytest-tmp"

Write-Host "[1/5] Build dependencies" -ForegroundColor Cyan
python -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

Write-Host "[2/5] Tests" -ForegroundColor Cyan
Remove-Item -Recurse -Force $PytestTemp -ErrorAction SilentlyContinue
python -m pytest --basetemp $PytestTemp
$TestExit = $LASTEXITCODE
Remove-Item -Recurse -Force $PytestTemp -ErrorAction SilentlyContinue
if ($TestExit -ne 0) { throw "Tests failed. Release build stopped." }

Write-Host "[3/5] Cleaning old build" -ForegroundColor Cyan
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

Write-Host "[4/5] Building Windows executable" -ForegroundColor Cyan
python -m PyInstaller --noconfirm --clean YouTubeDownloaderV2.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

$ReleaseRoot = Join-Path $ProjectRoot "release\YouTube-Downloader-V2-Windows-x64"
Remove-Item -Recurse -Force $ReleaseRoot -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $ReleaseRoot | Out-Null
Copy-Item (Join-Path $ProjectRoot "dist\YouTube-Downloader-V2.exe") $ReleaseRoot
Copy-Item (Join-Path $ProjectRoot "README.md") $ReleaseRoot
Copy-Item (Join-Path $ProjectRoot "LICENSE") $ReleaseRoot
Copy-Item (Join-Path $ProjectRoot "THIRD_PARTY_COMPONENTS.md") $ReleaseRoot

@"
DEPENDENCY BEHAVIOR
===================

If FFmpeg, FFprobe or Deno is missing, the application can download and verify
those components automatically into:

%LOCALAPPDATA%\YouTube-Downloader-V2\bin

No administrator permission or system PATH modification is required.

Portable override:
You may alternatively create a 'bin' directory next to the executable and place
ffmpeg.exe, ffprobe.exe and deno.exe there. Release-local files are detected
automatically if no repaired user-local copy exists.
"@ | Set-Content -Encoding UTF8 (Join-Path $ReleaseRoot "DEPENDENCIES.txt")

Write-Host "[5/5] Creating ZIP" -ForegroundColor Cyan
$Zip = Join-Path $ProjectRoot "release\YouTube-Downloader-V2-Windows-x64.zip"
Remove-Item -Force $Zip -ErrorAction SilentlyContinue
Compress-Archive -Path "$ReleaseRoot\*" -DestinationPath $Zip -CompressionLevel Optimal

Write-Host ""
Write-Host "Release ready:" -ForegroundColor Green
Write-Host $Zip
