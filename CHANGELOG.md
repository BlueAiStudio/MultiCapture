# Changelog

## Unreleased

- Themes: a theme changes the colours, the icon of each function and the decorations (header and canvas pictures), and can put a frame around copied and exported screenshots (picture frame or card style, with stickers such as flowers, a moon or stars). Open them with the new 🎨 Themes button.
- Built-in themes: Flowers, Night and Simple card.
- "Get online themes" downloads new or updated themes from the `themes/` folder of the GitHub repository. The app only goes online when you click it.
- Themes can be imported and exported as .zip files, and "Make my own from this…" starts a new theme from an existing one. See `docs/THEMES.md`.

## 1.3.2

- Renamed the app from "MultiCapture HAO" to "MultiCapture". The exe is now `MultiCapture.exe`.
- Settings and history move automatically from `%APPDATA%\MultiCapture_HAO` to `%APPDATA%\MultiCapture` on first start.
- `install_shortcut.ps1` removes the old "MultiCapture HAO" Start-menu shortcut and install folder.

## 1.3.1

- Lower memory use: only the 16 most recently used screenshots are kept in memory at full size. The others are reloaded from the session folder when you open them, so a long history no longer takes several GB of RAM. Startup is also faster because old screenshots are not decoded until needed.
- The app no longer fails to start when a session file is damaged. Bad files are skipped, and metadata left behind by an interrupted save is cleaned up.
- Screenshots are no longer lost when the app is closed right after a capture. Session PNGs are written to a temporary file first, and the app waits for pending writes before it exits.
- Restarting after a language change now works in the packaged exe.
- "Save all as PNG" and "Save as PDF" show an error instead of stopping silently when a file cannot be written.
- "Last region" falls back to region selection if the screen layout has changed.
- A GitHub Actions workflow builds the exe on Windows and attaches it to each tagged release.

## 1.3

- First public release.
