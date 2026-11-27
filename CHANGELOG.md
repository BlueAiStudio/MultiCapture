# Changelog

## Unreleased

- **Publisher is now BlueAiStudio**: the GitHub account moved from `xieganglaoliu` to `BlueAiStudio`. Online themes, links and the Store publisher name use the new name. The app is still called MultiCapture, and the Store package identity is unchanged, so it updates as before.
- **Taskbar icon when running from source**: the window now sets its own big and small icons, and `install_shortcut.ps1 -Source` creates a Start-menu shortcut that starts `multicapture.py` with `pythonw.exe`, with the MultiCapture icon and the app's taskbar ID, so the taskbar shows MultiCapture instead of the Python icon and pinning works.
- **Narrow windows**: when the window is too narrow for the whole top bar (e.g. not maximized, or in French), the buttons show only their icons (the tooltip still names them) instead of being cut off at the right edge. A window saved on a larger or another screen is moved and shrunk back inside the screen on start.
- **Scrolling capture of an inner panel**: when the rectangle also covers parts that stay still (a dialog's side pane, a comment column, a page sidebar), only the panel that scrolls was not recognised and the capture lost track. The moving panel is now found from the first scroll step, and the long image keeps just that panel.
- **Fix**: scrolling capture stopped right after the rectangle was drawn in browsers and many other apps (the pointer was left on the rectangle's edge, so the automatic scroll never reached the window). The pointer is now moved into the rectangle while it scrolls automatically, and a window that does not scroll by itself switches to scrolling by hand instead of stopping.
- **Fix**: a maximized window now comes back maximized after a capture, same-spot capture, scrolling capture or recording (it used to come back in its normal size).
- **Select several annotations**: with Select, `Ctrl` / `Shift` + click adds or removes one, `Shift` + drag on an empty spot selects with a box, `Ctrl+A` selects all. Move them together (drag or arrow keys), Delete, Duplicate, Bring to front / Send to back, and change colour, width, fill or font for all of them at once, each in one undo step.
- **Select several screenshots** in the history (or on the board): `Ctrl` + click toggles, `Shift` + click takes a range, `Ctrl+A` on the board takes all, Esc ends it. Right-click: copy together as one picture, compare the two, put at the end of the board, save as PNG files or one PDF, delete. The Delete key deletes them all after one confirmation; `Ctrl+Shift+C` compares the two selected.

## 1.5.0

- **Undo / Redo buttons** in the top bar (`Ctrl+Z` / `Ctrl+Y`, and now also `Ctrl+Shift+Z` for redo).
- **Drag pictures in** from Explorer or a web browser (files, or the picture of a web page). A dialog asks what to do: **merge with the other screenshots** (added to the history and the board, view switches to a grid), **open on its own** (added to the history but kept out of the board; right-click its card → "Add to board" later), or **float on top of the current screenshot**.
- **Float on top (overlay)**: a picture placed over a screenshot behaves like an annotation: move it, resize it from a corner (proportions kept), give it a border and an opacity, 1:1 size, undo / redo, Delete. It is merged into the screenshot when copying, saving or exporting. Right-click another history card → "Float on top of the current screenshot" lays one of your own screenshots over the current one. The pictures are kept as PNG files in `session\overlays`.
- Drag and drop uses `tkinterdnd2` (now in `requirements.txt`; PyInstaller bundles it through its own hook). Without it the app works as before, without dropping.
- **Table tool** (`W`): choose rows × columns (e.g. 3 × 2) in the TABLE section and drag on the screenshot. Double-click a cell to type; Tab = next cell (adds a row in the last cell), Enter = cell below, Shift+Enter = new line. Drag the white dots on the lines to resize columns and rows; right-click a cell to insert / delete rows and columns. Line colour and width, font, size, bold and alignment, header row and white background are editable at any time; cells grow to fit their text.
- **Symbol panel** (Ω Symbols… in the TEXT section, More symbols… in the stamp section): one click inserts ✓ ✗ ★ → ⚠ ± ° Ø ⌀ ≤ ≥ ① α … into the text box or table cell being typed, otherwise makes it the stamp. Symbols in text boxes and tables are now drawn with the symbol font, so they no longer turn into empty boxes in copies and exports.
- **Same spot** (⟳ button, `Ctrl+Shift+R`, global `Ctrl+Alt+R`, or history-card menu): captures exactly the same screen rectangle as the selected screenshot again and adds it as a new screenshot. Every capture now keeps its screen position (also across restarts).
- **Compare** (◧ button, `Ctrl+Shift+C`, or history-card menu): before / after window with a draggable slider or side by side, always with one shared zoom and pan. **Highlight differences** tints changed pixels red and boxes each changed area (adjustable tolerance); "Mark differences on 'After'" turns the boxes into editable rectangles; "Copy comparison" copies both images side by side. Opens by itself after a same-spot capture (can be switched off). Images of different sizes are compared on their overlapping top-left part.
- **Synced board zoom**: Ctrl+wheel over a board cell zooms all cells to the same place; wheel / middle-drag pans them together; Ctrl+0 or Fit resets.
- **Board report** (Save menu → "Export board as a report (PDF / Word)…"): the screenshots of the current view with a title, the date, each screenshot's notes and measurements, and a measurement summary table. Saved as PDF (A4) or Word .docx. No new dependency: the .docx is written directly, so the exe and the Store package need nothing extra.
- **Measurement table** (Save menu → "Copy board measurements as a table (Excel)"): every distance, area, perimeter, angle and scale reference on the board, copied as a table that pastes into Excel.
- **3D look for shapes**: select a rectangle, ellipse or area polygon and click **Make 3D** (right panel or right-click menu) to turn it into a shaded box, cylinder or prism. Drag the orange ◆ handle to set the depth and the angle; **Pocket (cut)** cuts a hole into the front face. Hidden edges show dashed through see-through solids. It is a drawing on the screenshot (no real 3D model) and is flattened like any other annotation when copying or exporting.
- **Paint-style drawing tools** (like the Paint app in Windows):
  - **Eraser** (`X`): rubs out pen and highlighter strokes and fills where you drag; other annotations it touches are removed. The screenshot itself is never erased. The line width sets the eraser size.
  - **Fill bucket** (`F`): fills the area of similar colour you click, as seen with the annotations. The fill is an annotation, so it can be recoloured, moved, erased or deleted.
  - **Colour picker** (`I`): takes the colour under the cursor and goes back to the previous tool.
  - **Crop**, **Rotate left / right**, **Flip horizontal / vertical** and **Resize…** in the new IMAGE section of the right panel (and the right-click menu). Annotations follow the picture; `Ctrl+Z` undoes.
  - **New blank canvas…** (`Ctrl+Shift+N`): an empty page in the history to draw on, with a size and background colour.
  - The tool bar switches to two columns when the window is too low for one.
- **Screen recording to MP4 with sound**: new Options → Extra features → Recording format (MP4 video by default, or GIF). MP4 is encoded while recording, so there is no length limit and memory use stays flat. MP4 can also record the microphone and/or the system sound (WASAPI loopback), each switched on separately in the same menu. MP4 uses ffmpeg from the optional `imageio-ffmpeg` package and sound uses the optional `PyAudioWPatch` package; the .exe and the Store package include both. Without them, recordings are GIF / silent. GIF recordings keep the 60 s limit.
- **Random theme**: in 🎨 Themes, "🎲 Random theme now" switches to a random installed theme, and "Use a random theme each time the app starts" picks a different one at every start (off by default).
- **Microsoft Store package**: `build_msix.ps1` builds an MSIX package (signed by the Store when published). In the Store version, settings and history live in the package's own data folder, so "Open folder" opens the right place. CI test-installs the package, checks that it starts, and makes the Store screenshots.
- **Code signing** of `MultiCapture.exe` in CI with Azure Artifact Signing, switched on by adding the repository secrets (see `docs/CODE_SIGNING.md`).
- **History limit** (Options › History limit): keep only the last 20 / 50 / 100 / 200 / 500 screenshots, or unlimited. The oldest are removed automatically; lowering the limit asks before deleting.
- **Temporary board**: with "Keep history between launches" switched off, screenshots are still written to the session folder so they can leave memory like the others, and are deleted on close (leftovers from a crash are removed at the next start). Long sessions no longer keep every image in RAM.
- History cards keep their thumbnail, so adding a capture no longer reloads every old screenshot from disk.
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
