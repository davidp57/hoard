$env:MEDIA_ROOT = "$PSScriptRoot\dev-media"
$env:PREDEFINED_FOLDERS = "Vu,A revoir,A supprimer"
$env:DB_PATH = "$PSScriptRoot\dev-media\progress.db"

if (-not (Test-Path "$PSScriptRoot\dev-media")) {
    New-Item -ItemType Directory "$PSScriptRoot\dev-media" | Out-Null
}

# Resolve ffmpeg binary
$ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ffmpegCmd) {
    $env:FFMPEG_BIN = $ffmpegCmd.Source
} else {
    $ffmpegExe = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter "ffmpeg.exe" -ErrorAction SilentlyContinue |
        Where-Object { $_.DirectoryName -notlike "*LosslessCut*" } |
        Select-Object -First 1 -ExpandProperty FullName
    if ($ffmpegExe) {
        $env:FFMPEG_BIN = $ffmpegExe
        Write-Host "ffmpeg trouve : $ffmpegExe"
    } else {
        Write-Warning "ffmpeg introuvable - le cut ne fonctionnera pas"
    }
}

& "$PSScriptRoot\.venv\Scripts\uvicorn" backend.main:app --reload --port 8000
