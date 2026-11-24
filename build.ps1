# Builds dist\MultiCapture_HAO.exe (single-file, no install needed).
# The file name has no version number on purpose: rebuilding overwrites the same file,
# so a pinned taskbar / Start-menu shortcut keeps working after an update.
# (Close the running app before rebuilding.)
# Usage:  powershell -ExecutionPolicy Bypass -File build.ps1
$ErrorActionPreference = "Stop"
$src  = Split-Path -Parent $MyInvocation.MyCommand.Path
$dist = Join-Path $src "dist"
Set-Location $src
python make_icon.py
python -m PyInstaller --noconfirm --clean --onefile --windowed `
    --name "MultiCapture_HAO" `
    --icon "$src\multicapture.ico" `
    --add-data "$src\multicapture.ico;." `
    --add-data "$src\multicapture.png;." `
    --exclude-module numpy --exclude-module pandas --exclude-module matplotlib `
    --exclude-module scipy --exclude-module PyQt5 --exclude-module PySide6 --exclude-module IPython `
    --distpath "$dist" --workpath "$env:TEMP\MultiCapture_HAO_build" --specpath "$env:TEMP\MultiCapture_HAO_build" `
    "$src\multicapture.py"
Write-Host "Built: $dist\MultiCapture_HAO.exe"
