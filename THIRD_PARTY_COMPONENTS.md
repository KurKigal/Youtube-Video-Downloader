# Third-party runtime components

YouTube Downloader V2 does **not** bundle FFmpeg or Deno inside the source repository or the default Windows executable.
When a required runtime component is missing, the Windows app can offer to download it into the current user's local application-data directory. Administrator privileges and PATH changes are not required.

## FFmpeg / FFprobe

- Download source: Gyan FFmpeg Windows release essentials build
- Package: `ffmpeg-release-essentials.zip`
- Download page: https://www.gyan.dev/ffmpeg/builds/
- The app downloads the matching `.sha256` file and verifies SHA-256 before extraction.
- FFmpeg licensing depends on the selected build and enabled libraries. See the provider page and https://ffmpeg.org/legal.html.

## Deno

- Download source: official Deno GitHub Releases
- Windows assets: `deno-x86_64-pc-windows-msvc.zip` or `deno-aarch64-pc-windows-msvc.zip`
- Releases: https://github.com/denoland/deno/releases
- The app downloads the matching `.sha256sum` file and verifies SHA-256 before extraction.
- Deno license information: https://github.com/denoland/deno

## Installation location

On Windows, automatically repaired components are stored in:

```text
%LOCALAPPDATA%\YouTube-Downloader-V2\bin
```

The app checks this location before a portable `bin/` directory and before the system PATH.
