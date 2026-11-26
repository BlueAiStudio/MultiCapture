# Copies dist\MultiCapture.exe to %LOCALAPPDATA%\Programs\MultiCapture and creates a
# Start-menu shortcut, so the app can be found in Start search and pinned to the taskbar.
# (Optional: the exe also runs fine on its own by double-clicking it.)
#
# Run it again after every rebuild to update the installed copy (close the app first).
# Usage:  powershell -ExecutionPolicy Bypass -File install_shortcut.ps1
#
# Running from the Python source instead of the .exe:
#         powershell -ExecutionPolicy Bypass -File install_shortcut.ps1 -Source
# creates a Start-menu shortcut that starts multicapture.py with pythonw.exe, with the MultiCapture
# icon and the same taskbar ID the app uses ("MultiCapture.Dev"), so the taskbar shows the
# MultiCapture icon (not the Python one) and pinning keeps working. -Python <path> picks pythonw.exe.
param([switch]$Source, [string]$Python = "")
$ErrorActionPreference = "Stop"
$src     = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Source) {
    $script = Join-Path $src "multicapture.py"
    $ico    = Join-Path $src "multicapture.ico"
    if (-not (Test-Path $script)) { throw "Not found: $script" }
    if (-not $Python) {
        $cmd = Get-Command pythonw.exe -ErrorAction SilentlyContinue
        if (-not $cmd) { throw "pythonw.exe not found - pass -Python <path to pythonw.exe>" }
        $Python = $cmd.Source
    }
    $lnk = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\MultiCapture.lnk"
    if (Test-Path $lnk) { Remove-Item $lnk -Force }
    $s = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
    $s.TargetPath = $Python
    $s.Arguments = '"' + $script + '"'
    $s.WorkingDirectory = $src
    $s.IconLocation = "$ico,0"
    $s.Description = "MultiCapture - multi-screenshot board (from source)"
    $s.Save()
    # Same AppUserModelID as multicapture.py sets when it runs from source, so the running window
    # and this shortcut are one taskbar entry with the MultiCapture icon. Done with Python + ctypes
    # (shortcut_id.py): nothing is compiled, which managed PCs may block.
    $py = Join-Path (Split-Path -Parent $Python) "python.exe"
    if (-not (Test-Path $py)) { $py = $Python }
    & $py (Join-Path $src "shortcut_id.py") $lnk "MultiCapture.Dev"
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Could not set the taskbar ID: the shortcut works, but a pinned button may show twice."
    }
    Write-Host "Shortcut : $lnk"
    Write-Host "Starts   : $Python `"$script`""
    exit 0
}

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
