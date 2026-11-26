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
    # and this shortcut are one taskbar entry with the MultiCapture icon.
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
public static class McLink {
    [ComImport, Guid("00021401-0000-0000-C000-000000000046")] class CShellLink {}
    [ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99")]
    interface IPropertyStore {
        void GetCount(out uint c);
        void GetAt(uint i, out PropKey k);
        void GetValue(ref PropKey k, out PropVar v);
        void SetValue(ref PropKey k, ref PropVar v);
        void Commit();
    }
    [StructLayout(LayoutKind.Sequential, Pack = 4)] struct PropKey { public Guid fmtid; public uint pid; }
    [StructLayout(LayoutKind.Explicit)] struct PropVar {
        [FieldOffset(0)] public ushort vt;
        [FieldOffset(8)] public IntPtr p;
        [FieldOffset(16)] public long pad;
    }
    public static void SetAppId(string lnk, string id) {
        object link = new CShellLink();
        ((IPersistFile)link).Load(lnk, 2);                      // STGM_READWRITE
        PropKey key = new PropKey { fmtid = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"), pid = 5 };
        PropVar v = new PropVar { vt = 31, p = Marshal.StringToCoTaskMemUni(id) };   // VT_LPWSTR
        try {
            IPropertyStore ps = (IPropertyStore)link;
            ps.SetValue(ref key, ref v);
            ps.Commit();
            ((IPersistFile)link).Save(lnk, true);
        } finally { Marshal.FreeCoTaskMem(v.p); }
    }
}
"@
    [McLink]::SetAppId($lnk, "MultiCapture.Dev")
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
