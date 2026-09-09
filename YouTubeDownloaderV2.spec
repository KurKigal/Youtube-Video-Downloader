# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all


yt_datas, yt_binaries, yt_hidden = collect_all("yt_dlp")
ejs_datas, ejs_binaries, ejs_hidden = collect_all("yt_dlp_ejs")


a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=yt_binaries + ejs_binaries,
    datas=yt_datas + ejs_datas,
    hiddenimports=yt_hidden + ejs_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="YouTube-Downloader-V2",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["icon.ico"],
)
