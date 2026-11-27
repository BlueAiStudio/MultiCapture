# Microsoft Store: package and listing

Everything needed to publish MultiCapture in the Microsoft Store. The Store signs the package with
Microsoft's certificate, so Store users never see the SmartScreen "unknown app" warning.

## How the package is made

- `build_msix.ps1` builds `dist\MultiCapture-<version>.0.msix` (a folder build of the app, tiles and icons
  made from `multicapture.png` by `packaging/msix/make_assets.py`, and `packaging/msix/AppxManifest.xml`).
- GitHub Actions runs it on every build, installs a test copy, checks that it starts, and uploads the package
  as the **MultiCapture-msix-for-Store** artifact. It also makes the Store screenshots
  (`tools/store_screenshots.py`, artifact **Store-screenshots**, 1920 × 1080 in en / zh / fr).
  A copy of the current ones is in [docs/store/screenshots](store/screenshots).
- The package identity comes from `packaging/msix/store.json`. Copy the three values from
  Partner Center → your app → **Product identity** into it once:

  | store.json             | Partner Center field                     |
  |------------------------|------------------------------------------|
  | `IdentityName`         | Package/Identity/Name                    |
  | `Publisher`            | Package/Identity/Publisher (`CN=…`)      |
  | `PublisherDisplayName` | Package/Properties/PublisherDisplayName  |

  `PublisherDisplayName` must match the publisher display name in Partner Center → Account settings →
  Legal info → Developer (now **Blueaistudio**). `IdentityName` and `Publisher` must never change: they are
  the app's identity, and a package with other values is refused as an update. The GitHub account was
  renamed from `xieganglaoliu` to `Blueaistudio`; the old name stays only in these identity values.

- Version: taken from `VERSION` in `multicapture.py` (`1.4.0` → `1.4.0.0`). Each Store upload needs a
  higher version than the last one.
- Store version data folder: `%LOCALAPPDATA%\Packages\<package family>\LocalState\MultiCapture`
  (the app finds it by itself; "Open folder" buttons open the right place).

## Submission settings

| Item | Value |
|---|---|
| Pricing | Free |
| Category | Productivity (subcategory: none) — or Utilities & tools |
| Privacy policy URL | https://github.com/Blueaistudio/MultiCapture/blob/main/PRIVACY.md |
| Website | https://github.com/Blueaistudio/MultiCapture |
| Support contact | https://github.com/Blueaistudio/MultiCapture/issues |
| Age rating questionnaire | No user interaction, no shared content, no purchases, no location → expected rating 3+ / Everyone |
| Restricted capability `runFullTrust` justification | Desktop (Win32) app: it captures the screen, registers the global hotkey Ctrl+Alt+S and writes images to folders the user picks. |
| Notes for certification | No account or test credentials needed. Press Ctrl+Alt+S (or the Capture button) and drag a region. Network is only used when the user clicks "Get online themes". |

## Listing text

### English (en-us)

**Product name:** MultiCapture

**Short description** (max 270 characters):
Take as many screenshots as you like and keep them all. MultiCapture lays them out in a grid, lets you
annotate them, and copies the result straight into Outlook, Word, Teams or Excel.

**Description:**

The built-in Snipping Tool keeps one capture at a time. MultiCapture keeps all of them in a history panel,
so you can compare, arrange, annotate and paste several screenshots at once, without saving files.

• Nothing is overwritten: every capture goes into the history panel and survives a restart.
• Board views: Single, 2×2, 3×3, 4×4 or All. Drag cells to reorder them.
• Auto-copy: the current view, one image or the whole grid, goes on the clipboard and pastes straight into
  Outlook, Word, Excel or Teams.
• Editable annotations: pen, highlighter, line, arrow, rectangle, ellipse, numbered markers, stamps, blur and
  callouts. Everything stays movable and editable.
• Word-like text boxes with font, size, bold, italic, underline, colour, background, border and alignment.
• PDF-style measurement: distance, perimeter, area and angle, with a calibrated scale.
• A notes panel for each screenshot, optionally included in copies and exports.
• Export to PNG, JPG, BMP or PDF, one image or all of them.
• Global hotkey Ctrl+Alt+S, with region, full-screen and last-region modes and an optional delay.
• Themes: change the colours, the icon of each function and the decorations, and frame your screenshots.
• Optional extras, off by default: text recognition (OCR, offline), pin a capture on top, scrolling capture
  and GIF recording.
• English, Français and 中文.

Free and open source (MIT). No account, no ads, no tracking. Your screenshots never leave your computer.

**What's new in this version:**
Drag pictures in from Explorer or a web browser and float them over a screenshot. Screen recording to MP4
with microphone and system sound, no time limit. Paint-style eraser, fill and colour picker, crop / rotate /
resize. Same-spot recapture with a before / after compare. Board report as PDF or Word. Tables, symbols,
3D-look shapes, Undo / Redo buttons and a random theme.

**Product features** (one per line, max 200 characters each):
- Keeps every screenshot in a history panel instead of overwriting the last one
- Grid views (2×2, 3×3, 4×4) to compare screenshots side by side
- Copies the current view automatically, ready to paste into Outlook, Word, Teams or Excel
- Editable arrows, boxes, numbered markers, blur and text
- Distance, area and angle measurement with a calibrated scale
- Export to PNG, JPG, BMP or a single PDF
- Global hotkey Ctrl+Alt+S
- Themes, plus optional OCR, pin on top, scrolling capture and GIF recording
- Works offline, no account, no tracking

**Search terms** (max 7): screenshot, screen capture, snipping tool, annotate, snip, OCR, GIF

---

### 中文（zh-cn）

**产品名称：** MultiCapture

**简短说明：**
想截多少张就截多少张，全部保留。MultiCapture 把截图按网格排列，可以直接标注，并把结果一键复制到 Outlook、Word、Teams 或 Excel。

**说明：**

系统自带的截图工具一次只保留一张。MultiCapture 把所有截图都放在历史面板里，不用存文件，就能同时对比、排列、标注和粘贴多张截图。

• 不会被覆盖：每张截图都进入历史面板，重启后依然在。
• 白板视图：单张、2×2、3×3、4×4 或全部，拖动格子即可调整顺序。
• 自动复制：当前视图（单张或整个网格）自动放入剪贴板，直接粘贴到 Outlook、Word、Excel 或 Teams。
• 可再编辑的标注：画笔、荧光笔、直线、箭头、矩形、椭圆、编号、印章、马赛克和标注框，全部可以移动和修改。
• 像 Word 一样的文本框：字体、字号、粗体、斜体、下划线、颜色、背景、边框和对齐。
• 像 PDF 一样的测量：距离、周长、面积和角度，支持比例校准。
• 每张截图都有备注栏，可选择是否一起复制和导出。
• 导出为 PNG、JPG、BMP 或 PDF，单张或全部。
• 全局快捷键 Ctrl+Alt+S，支持区域、全屏、上次区域和延时截图。
• 主题：更换配色、每个功能的图标和装饰，还能给截图加边框。
• 可选功能（默认关闭）：文字识别（离线 OCR）、置顶贴图、滚动截图和 GIF 录制。
• 支持中文、English、Français。

免费开源（MIT）。无需账号、无广告、不跟踪。你的截图不会离开你的电脑。

**此版本的新增内容：**
可以从资源管理器或浏览器拖入图片，并悬浮在截图上。录屏可保存为 MP4，同时录麦克风和系统声音，不限时长。新增像“画图”一样的橡皮擦、油漆桶、取色器，以及裁剪、旋转、调整大小。同位置重截，并可对比前后变化。拼图可导出为 PDF 或 Word 报告。新增表格、符号、立体图形、撤销 / 重做按钮和随机主题。

**产品功能：**
- 每张截图都保留在历史面板里，不会覆盖上一张
- 网格视图（2×2、3×3、4×4），并排对比截图
- 自动复制当前视图，直接粘贴到 Outlook、Word、Teams 或 Excel
- 可再编辑的箭头、方框、编号、马赛克和文字
- 距离、面积和角度测量，支持比例校准
- 导出为 PNG、JPG、BMP 或合并成一个 PDF
- 全局快捷键 Ctrl+Alt+S
- 主题，以及可选的 OCR、置顶贴图、滚动截图和 GIF 录制
- 离线可用，无需账号，不跟踪

**搜索词：** 截图, 截屏, 截图工具, 标注, 贴图, 文字识别, GIF

---

### Français (fr-fr et fr-ca)

**Nom du produit :** MultiCapture

**Description courte :**
Prenez autant de captures d'écran que vous voulez et gardez-les toutes. MultiCapture les dispose en grille,
vous permet de les annoter et copie le résultat directement dans Outlook, Word, Teams ou Excel.

**Description :**

L'Outil Capture d'écran intégré ne garde qu'une capture à la fois. MultiCapture les garde toutes dans un
panneau d'historique : comparez, disposez, annotez et collez plusieurs captures à la fois, sans enregistrer de fichiers.

• Rien n'est écrasé : chaque capture va dans l'historique et est conservée après un redémarrage.
• Vues tableau : Unique, 2×2, 3×3, 4×4 ou Tout. Faites glisser les cases pour les réordonner.
• Copie automatique : la vue actuelle, une image ou toute la grille, va dans le presse-papiers et se colle
  directement dans Outlook, Word, Excel ou Teams.
• Annotations modifiables : stylo, surligneur, ligne, flèche, rectangle, ellipse, repères numérotés, tampons,
  flou et bulles. Tout reste déplaçable et modifiable.
• Zones de texte comme dans Word : police, taille, gras, italique, souligné, couleur, fond, bordure et alignement.
• Mesures comme dans un PDF : distance, périmètre, surface et angle, avec une échelle étalonnée.
• Un panneau de notes pour chaque capture, inclus au besoin dans les copies et les exports.
• Export en PNG, JPG, BMP ou PDF, une image ou toutes.
• Raccourci global Ctrl+Alt+S, modes zone, plein écran et dernière zone, avec délai facultatif.
• Thèmes : changez les couleurs, l'icône de chaque fonction et les décorations, et encadrez vos captures.
• Extras facultatifs, désactivés par défaut : reconnaissance de texte (OCR hors ligne), épinglage au premier
  plan, capture défilante et enregistrement GIF.
• Français, English et 中文.

Gratuit et open source (MIT). Sans compte, sans publicité, sans suivi. Vos captures ne quittent jamais votre ordinateur.

**Nouveautés de cette version :**
Glissez des images depuis l'Explorateur ou un navigateur et superposez-les sur une capture. Enregistrement
d'écran en MP4 avec le micro et le son du système, sans limite de durée. Gomme, remplissage et pipette comme
dans Paint, recadrer / pivoter / redimensionner. Nouvelle capture au même endroit avec comparaison avant / après.
Rapport de la planche en PDF ou Word. Tableaux, symboles, formes en 3D, boutons Annuler / Rétablir et thème au hasard.

**Fonctionnalités du produit :**
- Garde chaque capture dans un historique au lieu d'écraser la précédente
- Vues en grille (2×2, 3×3, 4×4) pour comparer les captures côte à côte
- Copie automatiquement la vue actuelle, prête à coller dans Outlook, Word, Teams ou Excel
- Flèches, cadres, repères numérotés, flou et texte modifiables
- Mesure de distance, de surface et d'angle avec une échelle étalonnée
- Export en PNG, JPG, BMP ou en un seul PDF
- Raccourci global Ctrl+Alt+S
- Thèmes, et en option OCR, épinglage, capture défilante et enregistrement GIF
- Fonctionne hors ligne, sans compte, sans suivi

**Termes de recherche :** capture d'écran, capture, outil capture, annoter, OCR, GIF, screenshot
