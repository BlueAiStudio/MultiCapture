# Changelog

## Unreleased

- **Table tool** (`W`): choose rows × columns (e.g. 3 × 2) in the TABLE section and drag on the screenshot. Double-click a cell to type; Tab = next cell (adds a row in the last cell), Enter = cell below, Shift+Enter = new line. Drag the white dots on the lines to resize columns and rows; right-click a cell to insert / delete rows and columns. Line colour and width, font, size, bold and alignment, header row and white background are editable at any time; cells grow to fit their text.
- **Symbol panel** (Ω Symbols… in the TEXT section, More symbols… in the stamp section): one click inserts ✓ ✗ ★ → ⚠ ± ° Ø ⌀ ≤ ≥ ① α … into the text box or table cell being typed, otherwise makes it the stamp. Symbols in text boxes and tables are now drawn with the symbol font, so they no longer turn into empty boxes in copies and exports.
- **Microsoft Store package**: `build_msix.ps1` builds an MSIX package (signed by the Store when published). In the Store version, settings and history live in the package's own data folder, so "Open folder" opens the right place. CI test-installs the package, checks that it starts, and makes the Store screenshots.
- **Code signing** of `MultiCapture.exe` in CI with Azure Artifact Signing, switched on by adding the repository secrets (see `docs/CODE_SIGNING.md`).
- winget manifests (`packaging/winget`), Store listing texts (`docs/STORE.md`) and a privacy policy (`PRIVACY.md`).

## 1.4.0

Four optional features. Each one is off by default and switched on in **Options → Extra features**; while it is off the window looks exactly as before.

- **Pin to screen** (`Ctrl+P`, 📌 button or history-card menu): the screenshot floats above all windows. Drag to move, wheel to zoom, Ctrl+wheel for opacity, double-click or Esc to close.
- **Text recognition (OCR)** (`Ctrl+T`, 🔤 button): uses the OCR engine built into Windows 10/11 through Windows PowerShell, fully offline and without extra downloads. The text is copied to the clipboard and can be edited; the language can be chosen. Spaces Windows OCR puts between Chinese characters are removed.
- **Scrolling capture**: new "Scrolling" capture mode. Select the part of a window that scrolls; it is scrolled automatically (or by hand after Pause) and the frames are stitched into one long image. Fixed headers and footers are kept once.
- **Screen recording to GIF** (`Ctrl+R`, ⏺ button): records a region (or the full screen in Full screen mode) at 5, 10 or 15 fps, up to 60 s, and saves an animated GIF. The mouse pointer is drawn in the recording.
- The control bar and the frame around the captured or recorded region are hidden from the capture.
- Unit tests for the stitching, OCR text clean-up and GIF writing run in CI (`python -m unittest discover tests`).
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
