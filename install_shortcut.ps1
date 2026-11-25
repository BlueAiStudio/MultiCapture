# Copies dist\MultiCapture.exe to %LOCALAPPDATA%\Programs\MultiCapture and creates a
# Start-menu shortcut, so the app can be found in Start search and pinned to the taskbar.
# (Optional: the exe also runs fine on its own by double-clicking it.)
#
# Run it again after every rebuild to update the installed copy (close the app first).
# Usage:  powershell -ExecutionPolicy Bypass -File install_shortcut.ps1
$ErrorActionPreference = "Stop"
$src     = Split-Path -Parent $MyInvocation.MyCommand.Path
$built   = Join-Path $src "dist\MultiCapture.exe"
$instDir = Join-Path $env:LOCALAPPDATA "Programs\MultiCapture"
$exe     = Join-Path $instDir "MultiCapture.exe"
$lnk     = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\MultiCapture.lnk"
if (-not (Test-Path $built)) { throw "Not found: $built" }
if (Get-Process | Where-Object { $_.Path -eq $exe }) { throw "Close MultiCapture first, then run this again." }

New-Item -ItemType Directory -Force $instDir | Out-Null
Copy-Item $built $exe -Force

if (Test-Path $lnk) { Remove-Item $lnk -Force }
# remove the shortcut and install folder from versions up to 1.3.1 (named "MultiCapture HAO")
$oldLnk = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\MultiCapture HAO.lnk"
$oldDir = Join-Path $env:LOCALAPPDATA "Programs\MultiCapture_HAO"
if (Test-Path $oldLnk) { Remove-Item $oldLnk -Force }
if (Test-Path $oldDir) { Remove-Item $oldDir -Recurse -Force -ErrorAction SilentlyContinue }
$s = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
$s.TargetPath = $exe
$s.WorkingDirectory = $instDir
$s.IconLocation = "$exe,0"
$s.Description = "MultiCapture - multi-screenshot board"
$s.Save()
Write-Host "Installed: $exe"
Write-Host "Shortcut : $lnk"
