<p align="center"><img src="multicapture.png" width="128" alt="MultiCapture HAO icon"></p>

<h1 align="center">MultiCapture HAO</h1>

<p align="center">A multi-screenshot board for Windows: every capture is kept, laid out in a grid, annotated and copied to the clipboard automatically.</p>

<p align="center"><a href="#english">English</a> · <a href="#中文">中文</a> · <a href="#français">Français</a></p>

---

## English

The built-in Snipping Tool keeps one capture at a time. MultiCapture HAO keeps **all** of them in a history panel, so you can compare, arrange and paste several screenshots at once without saving files.

### Features

- **Nothing is overwritten**: every capture goes into the history panel (and survives a restart).
- **Board views**: Single / 2×2 / 3×3 / 4×4 / All. Drag cells to reorder them.
- **Auto-copy**: the current view (single image or whole grid) is put on the clipboard and pastes straight into Outlook, Word, Excel or Teams.
- **Editable annotations**: pen, highlighter, line, arrow, rectangle, ellipse, numbered markers, stamps, blur and callouts. Everything stays movable and editable.
- **Word-like text boxes**: font, size, bold / italic / underline, colour, background, border and alignment, with a ✥ grip to move them.
- **PDF-style measurement**: distance, perimeter, area and angle, with a calibrated scale.
- **Notes panel** for each screenshot, optionally included in copies and exports.
- **Export** to PNG / JPG / BMP / PDF, either one image or all of them (separate PNG files or one PDF).
- **On close**, the app asks whether to save, with a choice of folder and formats.
- **Delete menu**: delete the selected capture, the current board, or everything.
- **Global hotkey** `Ctrl+Alt+S`. Region, full-screen and last-region modes, with an optional delay.
- **Languages**: English, Français, 中文. A built-in user guide is under Help.

### Download

Get `MultiCapture_HAO.exe` from the [latest release](https://github.com/xieganglaoliu/MultiCapture/releases/latest). It is portable: no installer and no Python needed. Windows SmartScreen may warn because the exe is not code-signed; choose **More info → Run anyway**.

### Run from source

Requires Windows 10/11 and Python 3.10+.

```powershell
pip install Pillow
python multicapture.py
```

### Build the single-file .exe

```powershell
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File build.ps1
```

This produces `dist\MultiCapture_HAO.exe`. The exe is portable: no installer is needed, just double-click it.

You can also add it to the Start menu, so it shows up in Start search and pins cleanly to the taskbar:

```powershell
powershell -ExecutionPolicy Bypass -File install_shortcut.ps1
```

### Files

| File | Purpose |
|---|---|
| `multicapture.py` | The application |
| `i18n.py` | Translations (fr / zh) and the user guide |
| `make_icon.py` | Generates `multicapture.ico` / `.png` |
| `build.ps1` | PyInstaller build script |
| `install_shortcut.ps1` | Optional local install plus Start-menu shortcut |

Session data is stored in `%APPDATA%\MultiCapture_HAO\`.

---

## 中文

系统自带的截图工具每次只保留一张。MultiCapture HAO 会把**每一次**截图都保存在左侧的历史栏里，不会被覆盖。

- 支持单张、2×2、3×3、4×4 和全部宫格视图，拖动格子就能调整顺序；
- 当前视图会自动复制到剪贴板，可以直接粘贴到 Outlook、Word、Excel 或 Teams；
- 提供可编辑的标注：画笔、箭头、框、编号、印章、马赛克、标注框，以及类似 Word 的文字框（可设字体、字号、颜色，用 ✥ 拖动）；
- 提供类似 PDF 阅读器的测量功能：距离、周长、面积、角度，可以标定比例；
- 右侧是笔记栏，可以选择是否把笔记一起复制或导出；
- 可导出为 PNG、JPG、BMP 或 PDF；关闭软件时会提示是否保存；
- 「删除」菜单可以删除当前截图、整个宫格或全部截图；
- 全局快捷键 `Ctrl+Alt+S`；界面支持中文、英文、法文，并内置使用说明。

下载：在 [Releases](https://github.com/xieganglaoliu/MultiCapture/releases/latest) 页面下载 `MultiCapture_HAO.exe`，免安装、不需要 Python。

运行源码：`pip install Pillow`，然后执行 `python multicapture.py`。打包：运行 `build.ps1`，生成的 `dist\MultiCapture_HAO.exe` 是免安装版，双击即可使用。

---

## Français

L'Outil Capture d'écran ne garde qu'une capture à la fois. MultiCapture HAO les garde **toutes** dans un historique.

- Vues en grille 2×2 / 3×3 / 4×4, réorganisables par glisser-déposer ;
- La vue courante est copiée automatiquement dans le presse-papiers (Outlook, Word, Excel…) ;
- Annotations modifiables et zones de texte de type Word ;
- Mesures façon PDF : distance, périmètre, surface, angle ;
- Panneau de notes, export PNG / JPG / BMP / PDF, demande d'enregistrement à la fermeture ;
- Interface en français, anglais et chinois, avec un guide intégré.

Téléchargement : `MultiCapture_HAO.exe` dans les [Releases](https://github.com/xieganglaoliu/MultiCapture/releases/latest), sans installation ni Python.

Lancement : `pip install Pillow`, puis `python multicapture.py`. Pour créer l'exe portable, lancez `build.ps1`.

---

## License

[MIT](LICENSE)
