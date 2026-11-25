# Builds dist\MultiCapture-<version>.msix, the package uploaded to the Microsoft Store.
# The Store signs the package itself, so no certificate is needed here.
# The identity values (name, publisher) come from packaging\msix\store.json (from Partner Center).
# Needs the Windows 10/11 SDK (makeappx.exe, makepri.exe); GitHub's windows-latest runner has it.
# Usage:  powershell -ExecutionPolicy Bypass -File build_msix.ps1
$ErrorActionPreference = "Stop"
$src   = Split-Path -Parent $MyInvocation.MyCommand.Path
$dist  = Join-Path $src "dist"
$work  = Join-Path $env:TEMP "MultiCapture_msix"
$stage = Join-Path $work "package"
$pri   = Join-Path $work "pri"
Set-Location $src

# --- version: "1.4.0" in multicapture.py -> "1.4.0.0" (the Store needs the last part to be 0)
$m = Select-String -Path "$src\multicapture.py" -Pattern '^VERSION = "(\d+)\.(\d+)\.(\d+)"' | Select-Object -First 1
if (-not $m) { throw "VERSION not found in multicapture.py" }
$g = $m.Matches[0].Groups
$version = "$($g[1].Value).$($g[2].Value).$($g[3].Value).0"
$id = Get-Content -Raw "$src\packaging\msix\store.json" | ConvertFrom-Json

# --- Windows SDK tools (newest installed version)
$kits = Join-Path ${env:ProgramFiles(x86)} "Windows Kits\10\bin"
$bin = Get-ChildItem $kits -Directory | Where-Object { $_.Name -match '^10\.' -and (Test-Path (Join-Path $_.FullName "x64\makeappx.exe")) } |
       Sort-Object { [version]$_.Name } | Select-Object -Last 1
if (-not $bin) { throw "Windows SDK (makeappx.exe) not found under $kits" }
$makeappx = Join-Path $bin.FullName "x64\makeappx.exe"
$makepri  = Join-Path $bin.FullName "x64\makepri.exe"

if (Test-Path $work) { Remove-Item -Recurse -Force $work }
New-Item -ItemType Directory -Force -Path $stage, $pri, $dist | Out-Null

# --- the program: a folder build (starts faster than the single-file exe, nothing unpacked to TEMP)
python make_icon.py
python -m PyInstaller --noconfirm --clean --onedir --windowed `
    --name "MultiCapture" `
    --icon "$src\multicapture.ico" `
    --add-data "$src\multicapture.ico;." `
    --add-data "$src\multicapture.png;." `
    --add-data "$src\themes;themes" `
    --collect-data imageio_ffmpeg `
    --hidden-import pyaudiowpatch `
    --exclude-module numpy --exclude-module pandas --exclude-module matplotlib `
    --exclude-module scipy --exclude-module PyQt5 --exclude-module PySide6 --exclude-module IPython `
    --distpath "$stage" --workpath "$work\build" --specpath "$work\build" `
    "$src\multicapture.py"
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

# --- manifest
$manifest = (Get-Content -Raw "$src\packaging\msix\AppxManifest.xml").
    Replace("{{IdentityName}}", $id.IdentityName).
    Replace("{{Publisher}}", $id.Publisher).
    Replace("{{PublisherDisplayName}}", $id.PublisherDisplayName).
    Replace("{{Version}}", $version)
$utf8 = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $stage "AppxManifest.xml"), $manifest, $utf8)
[IO.File]::WriteAllText((Join-Path $pri "AppxManifest.xml"), $manifest, $utf8)

# --- tiles and icons, and the resource index that picks the right size for each screen
python "$src\packaging\msix\make_assets.py" (Join-Path $pri "Assets")
if ($LASTEXITCODE -ne 0) { throw "make_assets.py failed" }
& $makepri createconfig /cf "$work\priconfig.xml" /dq en-US /pv 10.0.0 /o
if ($LASTEXITCODE -ne 0) { throw "makepri createconfig failed" }
& $makepri new /pr "$pri" /cf "$work\priconfig.xml" /mn "$pri\AppxManifest.xml" /of "$pri\resources.pri" /o
if ($LASTEXITCODE -ne 0) { throw "makepri new failed" }
Copy-Item -Recurse "$pri\Assets" "$stage\Assets"
Copy-Item "$pri\resources.pri" "$stage\resources.pri"

# --- pack
$out = Join-Path $dist "MultiCapture-$($version).msix"
& $makeappx pack /d "$stage" /p "$out" /o
if ($LASTEXITCODE -ne 0) { throw "makeappx pack failed" }
Write-Host "Built: $out  (identity $($id.IdentityName), version $version)"
