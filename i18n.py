# -*- coding: utf-8 -*-
"""Translations (English source strings -> French, Chinese) and the in-app user guide."""
import ctypes

LANG = ["en"]
LANGS = [("en", "English"), ("fr", "Français"), ("zh", "中文")]


def detect_lang():
    try:
        lid = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF
    except Exception:
        return "en"
    return {0x04: "zh", 0x0C: "fr"}.get(lid, "en")


def tr(s, **kw):
    if LANG[0] != "en":
        t = TR.get(s)
        if t:
            s = t[0] if LANG[0] == "fr" else t[1]
    return s.format(**kw) if kw else s


TR = {
    # ---------------------------------------------------------------- pictures dragged in / laid over
    "Picture": ("Image", "图片"),
    "PICTURE": ("IMAGE", "图片"),
    "Add pictures": ("Ajouter des images", "添加图片"),
    "{n} picture(s) dropped – what should happen?": ("{n} image(s) déposée(s) – que faire ?", "拖入了 {n} 张图片，要怎么处理？"),
    "Merge with the other screenshots": ("Fusionner avec les autres captures", "和现有其他图片合并"),
    "Added to the history and to the board (2×2, 3×3 …), copied together as one picture.":
        ("Ajoutée(s) à l'historique et à la planche (2×2, 3×3 …), copiées ensemble en une seule image.",
         "加入历史记录和拼图（2×2、3×3 …），和其他截图一起合成一张图复制。"),
    "Open on its own": ("Ouvrir à part", "单独打开"),
    "Added to the history and shown alone, kept out of the board.":
        ("Ajoutée(s) à l'historique et affichée(s) seule(s), hors de la planche.",
         "加入历史记录并单独显示，不放进拼图。"),
    "Float on top of the current screenshot": ("Superposer sur la capture actuelle", "悬浮到当前图片上"),
    "Laid over {t} as a picture you can move and resize; merged into it when copying or saving.":
        ("Posée sur {t}, déplaçable et redimensionnable ; fusionnée avec elle à la copie ou à l'enregistrement.",
         "放在 {t} 上面，可以拖动和缩放；复制或保存时合并成一张图。"),
    "Open a screenshot first.": ("Ouvrez d'abord une capture.", "请先打开一张截图。"),
    "Float on top of the current screenshot (#{n})": ("Superposer sur la capture actuelle (n° {n})", "悬浮到当前图片上 (#{n})"),
    "Add to board": ("Ajouter à la planche", "加入拼图"),
    "Opening dropped pictures…": ("Ouverture des images déposées…", "正在打开拖入的图片…"),
    "These could not be opened as pictures:": ("Impossible d'ouvrir ces éléments comme images :", "以下内容无法作为图片打开："),
    "Nothing added – drop picture files, or pictures from a web page":
        ("Rien n'a été ajouté – déposez des fichiers image ou des images d'une page web",
         "没有添加任何内容 —— 请拖入图片文件，或网页上的图片"),
    "Cancelled": ("Annulé", "已取消"),
    "{n} picture(s) added": ("{n} image(s) ajoutée(s)", "已添加 {n} 张图片"),
    "  ·  merged into the board": ("  ·  fusionnée(s) dans la planche", "  ·  已合并到拼图"),
    "{n} picture(s) placed on #{num}  ·  drag to move, corners to resize":
        ("{n} image(s) posée(s) sur n° {num}  ·  glisser pour déplacer, coins pour redimensionner",
         "已在 #{num} 上放置 {n} 张图片  ·  拖动可移动，拖角可缩放"),
    "Original size": ("Taille d'origine", "原始大小"),
    "Show the picture at its own pixel size (1:1)": ("Afficher l'image à sa taille en pixels (1:1)", "按图片自身像素大小显示 (1:1)"),
    "Drag to move · drag a corner to resize · merged into the screenshot when copying or saving":
        ("Glisser pour déplacer · un coin pour redimensionner · fusionnée avec la capture à la copie ou à l'enregistrement",
         "拖动可移动 · 拖角可缩放 · 复制或保存时与截图合并"),
    # ---------------------------------------------------------------- header
    "New capture": ("Nouvelle capture", "新建截图"),
    "New capture  (Ctrl+N)\nGlobal hotkey from anywhere: Ctrl+Alt+S":
        ("Nouvelle capture  (Ctrl+N)\nRaccourci global partout : Ctrl+Alt+S", "新建截图  (Ctrl+N)\n任意位置全局快捷键：Ctrl+Alt+S"),
    "Region": ("Zone", "矩形区域"),
    "Full screen": ("Plein écran", "全屏"),
    "Last region": ("Dernière zone", "上次区域"),
    "No delay": ("Sans délai", "无延迟"),
    "3 s": ("3 s", "3 秒"),
    "5 s": ("5 s", "5 秒"),
    "10 s": ("10 s", "10 秒"),
    "Capture mode": ("Mode de capture", "截图模式"),
    "Delay before capture": ("Délai avant capture", "截图前延迟"),
    "View": ("Vue", "视图"),
    "Single": ("Unique", "单张"),
    "All": ("Tout", "全部"),
    "Show one screenshot  (key {k})": ("Afficher une capture  (touche {k})", "显示单张截图  (按键 {k})"),
    "Show all screenshots  (key {k})": ("Afficher toutes les captures  (touche {k})", "显示全部截图  (按键 {k})"),
    "Show the last {n} screenshots  (key {k})": ("Afficher les {n} dernières captures  (touche {k})", "显示最近 {n} 张截图  (按键 {k})"),
    "Copy": ("Copier", "复制"),
    "Copy the current view to the clipboard  (Ctrl+C)":
        ("Copier la vue actuelle dans le presse-papiers  (Ctrl+C)", "将当前视图复制到剪贴板  (Ctrl+C)"),
    "Save": ("Enregistrer", "保存"),
    "Save / export": ("Enregistrer / exporter", "保存 / 导出"),
    "Delete": ("Supprimer", "删除"),
    "Delete the selected screenshot": ("Supprimer la capture sélectionnée", "删除选中的截图"),
    "Options": ("Options", "选项"),
    "Help": ("Aide", "帮助"),
    "User guide  (F1)": ("Guide d'utilisation  (F1)", "使用说明  (F1)"),
    "HISTORY": ("HISTORIQUE", "历史记录"),
    "HISTORY  ·  {n}": ("HISTORIQUE  ·  {n}", "历史记录  ·  {n}"),
    "Ready  ·  Ctrl+Alt+S to capture from anywhere":
        ("Prêt  ·  Ctrl+Alt+S pour capturer depuis n'importe où", "就绪  ·  在任意位置按 Ctrl+Alt+S 截图"),
    "Fit": ("Ajuster", "适应"),
    "Fit to window  (Ctrl+0)": ("Ajuster à la fenêtre  (Ctrl+0)", "适应窗口  (Ctrl+0)"),
    "Actual size  (Ctrl+1)": ("Taille réelle  (Ctrl+1)", "实际大小  (Ctrl+1)"),
    "Zoom out  (Ctrl+−)": ("Zoom arrière  (Ctrl+−)", "缩小  (Ctrl+−)"),
    "Zoom in  (Ctrl++ / Ctrl+wheel)": ("Zoom avant  (Ctrl++ / Ctrl+molette)", "放大  (Ctrl++ / Ctrl+滚轮)"),

    # ---------------------------------------------------------------- right panel
    "SELECTION": ("SÉLECTION", "选中对象"),
    "Nothing selected": ("Aucune sélection", "未选中"),
    "Duplicate": ("Dupliquer", "复制"),
    "Front": ("Devant", "置前"),
    "Back": ("Derrière", "置后"),
    "Bring to front": ("Mettre au premier plan", "置于顶层"),
    "Send to back": ("Mettre en arrière-plan", "置于底层"),
    "Delete key": ("Touche Suppr", "Delete 键"),
    "COLOUR": ("COULEUR", "颜色"),
    "Custom…": ("Personnalisée…", "自定义…"),
    "LINE WIDTH": ("ÉPAISSEUR", "线宽"),
    "FILL": ("REMPLISSAGE", "填充"),
    "Fill shape": ("Remplir", "填充形状"),
    "3D": ("3D", "立体"),
    "Make 3D": ("Rendre en 3D", "变立体"),
    "Make flat": ("Remettre à plat", "恢复平面"),
    "Pocket (cut)": ("Poche (découpe)", "挖槽（切除）"),
    "Rectangle → box, ellipse → cylinder, polygon → prism":
        ("Rectangle → boîte, ellipse → cylindre, polygone → prisme", "矩形 → 立方体，椭圆 → 圆柱，多边形 → 棱柱"),
    "Drag the orange ◆ handle to set depth and angle":
        ("Faites glisser la poignée orange ◆ pour régler la profondeur et l'angle", "拖动橙色 ◆ 手柄调整深度和角度"),
    "Opacity": ("Opacité", "不透明度"),
    "TEXT": ("TEXTE", "文字"),
    "Bold": ("Gras", "粗体"),
    "Italic": ("Italique", "斜体"),
    "Underline": ("Souligné", "下划线"),
    "Align left": ("Aligner à gauche", "左对齐"),
    "Align center": ("Centrer", "居中"),
    "Align right": ("Aligner à droite", "右对齐"),
    "Background": ("Fond", "背景"),
    "Border": ("Bordure", "边框"),
    "Double-click a text to edit it · drag to move":
        ("Double-clic pour modifier · glisser pour déplacer", "双击文字可编辑 · 拖动可移动"),
    "SIZE": ("TAILLE", "大小"),
    "SYMBOL": ("SYMBOLE", "符号"),
    "MEASURE": ("MESURE", "测量"),
    "Set scale…": ("Échelle…", "设置比例…"),
    "Enter how much one pixel represents": ("Saisir la valeur réelle d'un pixel", "输入 1 像素代表的实际长度"),
    "Calibrate": ("Calibrer", "校准"),
    "Draw a line over a known length": ("Tracer une ligne sur une longueur connue", "在已知长度上画一条线"),
    "Reset": ("Réinit.", "重置"),
    "Dec.": ("Déc.", "小数位"),
    "NOTES": ("NOTES", "备注"),
    "NOTES  ·  #{n}": ("NOTES  ·  #{n}", "备注  ·  #{n}"),
    "Include notes when copying / exporting": ("Inclure les notes (copie / export)", "复制 / 导出时包含备注"),
    "  (callout)": ("  (bulle)", "  (标注框)"),
    "Nothing selected  ·  click an annotation  ·  Ctrl / Shift + click for several":
        ("Aucune sélection  ·  cliquez une annotation  ·  Ctrl / Maj + clic pour plusieurs",
         "未选中  ·  点击一个标注  ·  按住 Ctrl / Shift 点击可多选"),
    "New: {name}": ("Nouveau : {name}", "新建：{name}"),
    "Scale: 1 px = {k} {u}\nSource: {src}": ("Échelle : 1 px = {k} {u}\nSource : {src}", "比例：1 px = {k} {u}\n来源：{src}"),
    "reference line": ("ligne de référence", "参考线"),
    "this screenshot": ("cette capture", "本截图"),
    "default": ("par défaut", "默认比例"),
    "Scale: pixels (not calibrated)": ("Échelle : pixels (non calibrée)", "比例：像素（未校准）"),

    # ---------------------------------------------------------------- tools
    "Select": ("Sélection", "选择"),
    "Pen": ("Stylo", "画笔"),
    "Highlighter": ("Surligneur", "荧光笔"),
    "Line": ("Ligne", "直线"),
    "Arrow": ("Flèche", "箭头"),
    "Rectangle": ("Rectangle", "矩形"),
    "Ellipse": ("Ellipse", "椭圆"),
    "Text box": ("Zone de texte", "文本框"),
    "Callout": ("Bulle", "标注框"),
    "Numbered marker": ("Repère numéroté", "编号标记"),
    "Stamp": ("Tampon", "符号"),
    "Blur": ("Flou", "马赛克"),
    "Distance": ("Distance", "距离"),
    "Perimeter": ("Périmètre", "周长"),
    "Area": ("Surface", "面积"),
    "Angle": ("Angle", "角度"),
    "Scale reference": ("Référence d'échelle", "比例参考"),
    "Select / move / resize  (V)\nCtrl / Shift + click: select several · Shift + drag: select with a box · Ctrl+A: all":
        ("Sélection / déplacer / redimensionner  (V)\nCtrl / Maj + clic : sélection multiple · Maj + glisser : sélection par cadre · Ctrl+A : tout",
         "选择 / 移动 / 调整大小  (V)\nCtrl / Shift + 点击：多选 · Shift + 拖动：框选 · Ctrl+A：全选"),
    "Pen  (P)": ("Stylo  (P)", "画笔  (P)"),
    "Highlighter  (H)": ("Surligneur  (H)", "荧光笔  (H)"),
    "Line  (L)  - hold Shift for 45°": ("Ligne  (L)  - Maj pour 45°", "直线  (L)  - 按住 Shift 锁定 45°"),
    "Arrow  (A)  - hold Shift for 45°": ("Flèche  (A)  - Maj pour 45°", "箭头  (A)  - 按住 Shift 锁定 45°"),
    "Rectangle  (R)  - hold Shift for square": ("Rectangle  (R)  - Maj pour un carré", "矩形  (R)  - 按住 Shift 画正方形"),
    "Ellipse  (E)  - hold Shift for circle": ("Ellipse  (E)  - Maj pour un cercle", "椭圆  (E)  - 按住 Shift 画圆"),
    "Text box  (T)  - Word-like formatting on the right":
        ("Zone de texte  (T)  - mise en forme type Word à droite", "文本框  (T)  - 右侧可像 Word 一样设置格式"),
    "Callout: drag from target to text  (C)": ("Bulle : glisser de la cible vers le texte  (C)", "标注框：从目标点拖到文字位置  (C)"),
    "Numbered marker  (N)": ("Repère numéroté  (N)", "编号标记  (N)"),
    "Stamp / symbol  (S)": ("Tampon / symbole  (S)", "符号印章  (S)"),
    "Blur / pixelate area  (B)": ("Flouter / pixeliser une zone  (B)", "马赛克 / 模糊区域  (B)"),
    "Measure distance  (D)": ("Mesurer une distance  (D)", "测量距离  (D)"),
    "Measure perimeter / polyline  (M)\nclick points, double-click or Enter to finish":
        ("Mesurer un périmètre / polyligne  (M)\ncliquer les points, double-clic ou Entrée pour finir",
         "测量周长 / 折线  (M)\n依次点击各点，双击或回车结束"),
    "Measure area (polygon)  (G)\nclick points, double-click or Enter to finish":
        ("Mesurer une surface (polygone)  (G)\ncliquer les points, double-clic ou Entrée pour finir",
         "测量面积（多边形）  (G)\n依次点击各点，双击或回车结束"),
    "Measure angle  (Q) - click 3 points, vertex 2nd":
        ("Mesurer un angle  (Q) - cliquer 3 points, sommet en 2e", "测量角度  (Q) - 点击 3 个点，第 2 个为顶点"),
    "Set scale from a known length  (K)": ("Définir l'échelle avec une longueur connue  (K)", "用已知长度设置比例  (K)"),
    "Tool: {name}": ("Outil : {name}", "工具：{name}"),
    "  ·  click points, double-click / Enter to finish, Esc to cancel":
        ("  ·  cliquer les points, double-clic / Entrée pour finir, Échap pour annuler", "  ·  依次点击各点，双击 / 回车结束，Esc 取消"),
    "  ·  click 3 points (vertex second)": ("  ·  cliquer 3 points (sommet en 2e)", "  ·  点击 3 个点（第 2 个为顶点）"),
    "  ·  draw a line over a known length": ("  ·  tracer une ligne sur une longueur connue", "  ·  在已知长度上画一条线"),
    "  ·  press on the target, drag to where the text goes":
        ("  ·  appuyer sur la cible, glisser jusqu'à l'emplacement du texte", "  ·  在目标处按下，拖到文字要放的位置"),
    "  ·  click to add text, click an existing text to edit it":
        ("  ·  cliquer pour ajouter du texte, cliquer un texte existant pour le modifier", "  ·  点击添加文字，点击已有文字可编辑"),

    # ---------------------------------------------------------------- status / messages
    "Capture cancelled": ("Capture annulée", "已取消截图"),
    "Capture failed": ("Échec de la capture", "截图失败"),
    "Screenshot #{n} added  ({w} × {h})": ("Capture n°{n} ajoutée  ({w} × {h})", "已添加截图 #{n}  ({w} × {h})"),
    "{n} screenshots restored from last session": ("{n} captures restaurées de la dernière session", "已恢复上次的 {n} 张截图"),
    "Auto-save failed: {e}": ("Échec de l'enregistrement auto : {e}", "自动保存失败：{e}"),
    "Screenshot #{n} deleted": ("Capture n°{n} supprimée", "截图 #{n} 已删除"),
    "Delete screenshot": ("Supprimer la capture", "删除截图"),
    "Delete screenshot #{n} from the history?": ("Supprimer la capture n°{n} de l'historique ?", "从历史记录中删除截图 #{n}？"),
    "Board: {n} screenshot(s)  ·  drag to reorder": ("Planche : {n} capture(s)  ·  glisser pour réorganiser", "拼图：{n} 张截图  ·  拖动可调整位置"),
    "Position {k}": ("Position {k}", "位置 {k}"),
    "annotated": ("annotée", "已标注"),
    "notes": ("notes", "有备注"),
    "Board positions swapped": ("Positions échangées", "已交换位置"),
    "Need at least {n} points": ("Il faut au moins {n} points", "至少需要 {n} 个点"),
    "{name} measurement added": ("Mesure ajoutée : {name}", "已添加测量：{name}"),
    "Undo": ("Annuler", "撤销"),
    "Redo": ("Rétablir", "重做"),
    "Undo the last change  (Ctrl+Z)": ("Annuler la dernière modification  (Ctrl+Z)", "撤销上一步操作  (Ctrl+Z)"),
    "Redo what was undone  (Ctrl+Y / Ctrl+Shift+Z)": ("Rétablir ce qui a été annulé  (Ctrl+Y / Ctrl+Maj+Z)",
                                                      "重做刚才撤销的操作  (Ctrl+Y / Ctrl+Shift+Z)"),
    "Scale set: {px} px = {v} {u}  →  1 px = {k} {u}": ("Échelle : {px} px = {v} {u}  →  1 px = {k} {u}", "比例已设置：{px} px = {v} {u}  →  1 px = {k} {u}"),
    "Copied {label} to clipboard ({w} × {h})": ("{label} copiée dans le presse-papiers ({w} × {h})", "已将{label}复制到剪贴板 ({w} × {h})"),
    "✓ Copied {label}": ("✓ {label} copiée", "✓ 已复制{label}"),
    "screenshot": ("capture", "截图"),
    "board ({n} screenshots)": ("planche ({n} captures)", "拼图（{n} 张）"),
    "⚠ Clipboard busy - try Copy again": ("⚠ Presse-papiers occupé - réessayez Copier", "⚠ 剪贴板被占用，请再点一次复制"),
    "⚠ Global hotkey Ctrl+Alt+S is used by another program - use the button or Ctrl+N":
        ("⚠ Le raccourci Ctrl+Alt+S est utilisé par un autre programme - utilisez le bouton ou Ctrl+N",
         "⚠ 全局快捷键 Ctrl+Alt+S 已被其他程序占用，请使用按钮或 Ctrl+N"),
    "Saved: {p}": ("Enregistré : {p}", "已保存：{p}"),
    "✓ Saved": ("✓ Enregistré", "✓ 已保存"),
    "Save failed": ("Échec de l'enregistrement", "保存失败"),
    "{n} screenshots saved to {d}": ("{n} captures enregistrées dans {d}", "已将 {n} 张截图保存到 {d}"),
    "PDF with {n} page(s) saved: {p}": ("PDF de {n} page(s) enregistré : {p}", "已保存 {n} 页 PDF：{p}"),
    "✓ PDF saved": ("✓ PDF enregistré", "✓ PDF 已保存"),
    "Folder for all screenshots": ("Dossier pour toutes les captures", "选择保存全部截图的文件夹"),
    "No screenshots yet": ("Aucune capture pour l'instant", "还没有截图"),
    "Click  ＋ New capture  or press  Ctrl+Alt+S  anywhere.":
        ("Cliquez  ＋ Nouvelle capture  ou appuyez sur  Ctrl+Alt+S  n'importe où.", "点击「＋ 新建截图」，或在任意位置按 Ctrl+Alt+S。"),
    "Every capture is kept in the history — nothing is overwritten.":
        ("Chaque capture est conservée dans l'historique — rien n'est écrasé.", "每次截图都会保留在历史记录中，不会被覆盖。"),
    "The current view (single or grid) is copied automatically —\njust paste it into Outlook, Word or Excel.":
        ("La vue actuelle (unique ou grille) est copiée automatiquement —\ncollez-la directement dans Outlook, Word ou Excel.",
         "当前视图（单张或拼图）会自动复制，\n直接粘贴到 Outlook、Word 或 Excel 即可。"),
    "Press F1 for the user guide": ("F1 : guide d'utilisation", "按 F1 查看使用说明"),

    # ---------------------------------------------------------------- menus
    "Open": ("Ouvrir", "打开"),
    "Copy this screenshot": ("Copier cette capture", "复制这张截图"),
    "Save this screenshot as…": ("Enregistrer cette capture sous…", "这张截图另存为…"),
    "Move to end of board (newest position)": ("Placer en fin de planche (position la plus récente)", "移到拼图最后（最新位置）"),
    "Edit text": ("Modifier le texte", "编辑文字"),
    "Copy current view": ("Copier la vue actuelle", "复制当前视图"),
    "Remove all annotations": ("Supprimer toutes les annotations", "删除全部标注"),
    "Clear": ("Effacer", "清除"),
    "Remove all annotations from this screenshot?": ("Supprimer toutes les annotations de cette capture ?", "删除这张截图上的全部标注？"),
    "Save current view as…": ("Enregistrer la vue actuelle sous…", "当前视图另存为…"),
    "Save selected screenshot as…": ("Enregistrer la capture sélectionnée sous…", "选中截图另存为…"),
    "Save all screenshots as PNG files…": ("Enregistrer toutes les captures en PNG…", "全部截图保存为 PNG 文件…"),
    "Export all screenshots to one PDF…": ("Exporter toutes les captures dans un PDF…", "全部截图导出为一个 PDF…"),
    "Export board screenshots to PDF…": ("Exporter la planche en PDF…", "拼图中的截图导出为 PDF…"),
    "Auto-copy current view to clipboard": ("Copier automatiquement la vue dans le presse-papiers", "自动复制当前视图到剪贴板"),
    "Auto-save PNG files to folder": ("Enregistrer automatiquement en PNG dans un dossier", "自动保存 PNG 到文件夹"),
    "Choose auto-save folder…": ("Choisir le dossier d'enregistrement…", "选择自动保存文件夹…"),
    "Open auto-save folder": ("Ouvrir le dossier d'enregistrement", "打开自动保存文件夹"),
    "Keep history between launches": ("Conserver l'historique entre les lancements", "关闭后保留历史记录"),
    "History limit": ("Limite de l'historique", "历史记录上限"),
    "Last {n} screenshots": ("{n} dernières captures", "最近 {n} 张"),
    "Unlimited": ("Illimité", "不限"),
    "Clear history…": ("Effacer l'historique…", "清空历史记录…"),
    "Remove all annotations on this screenshot": ("Supprimer toutes les annotations de cette capture", "删除本截图的全部标注"),
    "Reset default scale": ("Réinitialiser l'échelle par défaut", "重置默认比例"),
    "Keyboard shortcuts": ("Raccourcis clavier", "键盘快捷键"),
    "User guide": ("Guide d'utilisation", "使用说明"),
    "Language": ("Langue", "语言 / Language"),
    "About {app}": ("À propos de {app}", "关于 {app}"),
    "About": ("À propos", "关于"),
    "Multi-screenshot board with annotation, measurement and notes.\nHistory folder: {p}":
        ("Planche multi-captures avec annotations, mesures et notes.\nDossier d'historique : {p}",
         "多次截图拼图工具，支持标注、测量和备注。\n历史记录文件夹：{p}"),
    "The new language is applied after a restart.\nRestart now?":
        ("La nouvelle langue s'applique après redémarrage.\nRedémarrer maintenant ?", "新语言将在重启后生效。\n现在重启吗？"),
    "Clear history": ("Effacer l'historique", "清空历史记录"),
    # ---------------------------------------------------------------- themes
    "Themes":
        ("Thèmes", "主题"),
    "Theme":
        ("Thème", "主题"),
    "Theme manager…":
        ("Gestionnaire de thèmes…", "主题管理…"),
    "Choose a theme, get new themes online or import your own":
        ("Choisir un thème, en télécharger de nouveaux ou importer le vôtre", "选择主题、获取在线主题或导入自己的主题"),
    "A theme changes the colours, the icon of each function, the decorations, and can add a frame to the screenshots you copy or export.":
        ("Un thème change les couleurs, l'icône de chaque fonction, les décorations, et peut ajouter un cadre aux captures copiées ou exportées.", "主题可以改变界面配色、每个功能的图标和装饰图，还可以给复制或导出的截图加上边框。"),
    "Add the theme frame to copies and exports":
        ("Ajouter le cadre du thème aux copies et exports", "复制和导出时加上主题边框"),
    "The theme “{name}” is applied after a restart.\nRestart now?":
        ("Le thème « {name} » s'applique après redémarrage.\nRedémarrer maintenant ?", "主题「{name}」将在重启后生效。\n现在重启吗？"),
    "Theme frame skipped: {e}":
        ("Cadre du thème ignoré : {e}", "主题边框未能加上：{e}"),
    "Random theme now":
        ("Thème au hasard", "随机换一个主题"),
    "Picks one of your installed themes at random":
        ("Choisit au hasard un de vos thèmes installés", "从已安装的主题中随机挑一个"),
    "Use a random theme each time the app starts":
        ("Thème au hasard à chaque démarrage", "每次启动时随机使用一个主题"),
    "Install another theme first.":
        ("Installez d'abord un autre thème.", "请先安装其他主题。"),
    "Use this theme":
        ("Utiliser ce thème", "使用此主题"),
    "Download and install":
        ("Télécharger et installer", "下载并安装"),
    "Update":
        ("Mettre à jour", "更新"),
    "Make my own from this…":
        ("Créer le mien à partir de celui-ci…", "以此为模板自己做…"),
    "Copies this theme into your themes folder so you can change its pictures and colours":
        ("Copie ce thème dans votre dossier de thèmes pour modifier ses images et couleurs", "把这个主题复制到你的主题文件夹，方便修改图片和配色"),
    "Export .zip…":
        ("Exporter en .zip…", "导出为 .zip…"),
    "Pack this theme into one file to share it":
        ("Regroupe ce thème dans un seul fichier à partager", "把主题打包成一个文件，方便分享"),
    "Remove":
        ("Supprimer", "删除"),
    "Get online themes":
        ("Thèmes en ligne", "获取在线主题"),
    "Looks for new themes on GitHub. This is the only time the app goes online.":
        ("Cherche de nouveaux thèmes sur GitHub. C'est le seul moment où l'application se connecte.", "到 GitHub 查找新主题。只有点这个按钮时软件才会联网。"),
    "Import .zip…":
        ("Importer un .zip…", "导入 .zip…"),
    "Install a theme someone sent you":
        ("Installer un thème qu'on vous a envoyé", "安装别人发给你的主题"),
    "Open themes folder":
        ("Ouvrir le dossier des thèmes", "打开主题文件夹"),
    "How to make a theme":
        ("Créer un thème", "如何制作主题"),
    "{n} theme folder(s) could not be read: {names}":
        ("{n} dossier(s) de thème illisible(s) : {names}", "有 {n} 个主题文件夹无法读取：{names}"),
    "built in":
        ("intégré", "内置"),
    "mine":
        ("à moi", "我的"),
    "online":
        ("en ligne", "在线"),
    "update":
        ("mise à jour", "可更新"),
    "by {a}":
        ("par {a}", "作者：{a}"),
    "has a frame":
        ("avec cadre", "带边框"),
    "no frame":
        ("sans cadre", "无边框"),
    "in use":
        ("utilisé", "使用中"),
    "version {v} available online":
        ("version {v} disponible en ligne", "在线有新版本 {v}"),
    "Could not reach GitHub: {e}":
        ("Impossible de joindre GitHub : {e}", "无法连接 GitHub：{e}"),
    "{n} online theme(s), {k} new or updated":
        ("{n} thème(s) en ligne, {k} nouveau(x) ou mis à jour", "在线共 {n} 个主题，其中 {k} 个是新的或可更新"),
    "Downloading… {i}/{n}":
        ("Téléchargement… {i}/{n}", "正在下载… {i}/{n}"),
    "Installed “{name}”.":
        ("« {name} » installé.", "已安装「{name}」。"),
    "Looking for themes on GitHub…":
        ("Recherche de thèmes sur GitHub…", "正在 GitHub 上查找主题…"),
    "Import a theme":
        ("Importer un thème", "导入主题"),
    "Theme package":
        ("Paquet de thème", "主题包"),
    "Import failed":
        ("Échec de l'importation", "导入失败"),
    "Choose another theme first, then remove this one.":
        ("Choisissez d'abord un autre thème, puis supprimez celui-ci.", "请先换成别的主题，再删除这个。"),
    "Remove the theme “{name}”?":
        ("Supprimer le thème « {name} » ?", "删除主题「{name}」吗？"),
    "New theme":
        ("Nouveau thème", "新主题"),
    "Name of your theme:":
        ("Nom de votre thème :", "主题名称："),
    "My theme":
        ("Mon thème", "我的主题"),
    "Created “{name}”. Change its pictures and theme.json, then choose it.":
        ("« {name} » créé. Modifiez ses images et theme.json, puis choisissez-le.", "已创建「{name}」。修改里面的图片和 theme.json 后，选中它即可使用。"),
    "Delete all {n} screenshots from the history?\nFiles you saved yourself are not affected.":
        ("Supprimer les {n} captures de l'historique ?\nLes fichiers que vous avez enregistrés ne sont pas touchés.",
         "从历史记录中删除全部 {n} 张截图？\n你自己保存的文件不受影响。"),
    "Auto-save folder": ("Dossier d'enregistrement automatique", "自动保存文件夹"),

    # ---------------------------------------------------------------- dialogs
    "Set scale": ("Définir l'échelle", "设置比例"),
    "This line is {px} px long.\nWhat is its real length?": ("Cette ligne mesure {px} px.\nQuelle est sa longueur réelle ?", "这条线长 {px} px。\n它的实际长度是多少？"),
    "1 pixel equals:": ("1 pixel vaut :", "1 像素等于："),
    "Use as default scale for all screenshots without their own scale":
        ("Utiliser comme échelle par défaut pour les captures sans échelle", "作为所有未设比例截图的默认比例"),
    "Cancel": ("Annuler", "取消"),
    "OK": ("OK", "确定"),
    "Please enter a positive number.": ("Veuillez saisir un nombre positif.", "请输入一个正数。"),
    "Scale": ("Échelle", "比例"),
    "Annotation colour": ("Couleur d'annotation", "标注颜色"),
    "Fill colour": ("Couleur de remplissage", "填充颜色"),
    "Text background": ("Fond du texte", "文字背景色"),
    "Drag to select an area   ·   Esc / right-click to cancel":
        ("Glissez pour sélectionner une zone   ·   Échap / clic droit pour annuler", "拖动鼠标选择区域   ·   Esc / 右键取消"),
    "Close": ("Fermer", "关闭"),
    # close dialog
    "Save before closing?": ("Enregistrer avant de fermer ?", "关闭前保存吗？"),
    "{n} screenshot(s) have not been saved to a file yet.":
        ("{n} capture(s) n'ont pas encore été enregistrées dans un fichier.", "有 {n} 张截图还没有保存成文件。"),
    "WHAT TO SAVE": ("QUOI ENREGISTRER", "保存内容"),
    "Current view ({v})": ("Vue actuelle ({v})", "当前视图（{v}）"),
    "Only unsaved screenshots – one file each": ("Seulement les captures non enregistrées – un fichier chacune", "仅未保存的截图 – 每张一个文件"),
    "All screenshots – one file each": ("Toutes les captures – un fichier chacune", "全部截图 – 每张一个文件"),
    "All screenshots in one PDF": ("Toutes les captures dans un seul PDF", "全部截图合并为一个 PDF"),
    "FORMAT": ("FORMAT", "格式"),
    "FOLDER": ("DOSSIER", "保存路径"),
    "Browse…": ("Parcourir…", "浏览…"),
    "FILE NAME": ("NOM DU FICHIER", "文件名"),
    "Open the folder after saving": ("Ouvrir le dossier après l'enregistrement", "保存后打开文件夹"),
    "Ask every time I close the app": ("Demander à chaque fermeture", "每次关闭软件时都询问"),
    "Save and close": ("Enregistrer et fermer", "保存并关闭"),
    "Close without saving": ("Fermer sans enregistrer", "不保存直接关闭"),
    "Please choose a folder.": ("Veuillez choisir un dossier.", "请选择一个文件夹。"),
    "Ask to save when closing": ("Proposer d'enregistrer à la fermeture", "关闭时询问是否保存"),
    # delete menu
    "Delete screenshots": ("Supprimer des captures", "删除截图"),
    "Delete selected screenshot": ("Supprimer la capture sélectionnée", "删除选中的截图"),
    "Delete the {n} screenshots of this board…": ("Supprimer les {n} captures de cette planche…", "删除当前拼图中的 {n} 张截图…"),
    "Delete ALL screenshots…": ("Supprimer TOUTES les captures…", "删除全部截图…"),
    "Delete {n} screenshot(s) from the history?": ("Supprimer {n} capture(s) de l'historique ?", "从历史记录中删除 {n} 张截图？"),
    "⚠ {n} of them have not been saved to a file and will be lost.":
        ("⚠ {n} d'entre elles n'ont pas été enregistrées dans un fichier et seront perdues.", "⚠ 其中 {n} 张还没保存成文件，删除后将无法找回。"),
    "Files you saved yourself are not affected.": ("Les fichiers que vous avez enregistrés ne sont pas touchés.", "你自己保存的文件不受影响。"),
    "{n} screenshot(s) deleted": ("{n} capture(s) supprimée(s)", "已删除 {n} 张截图"),
    # ---------------------------------------------------------------- same spot + compare
    "Same spot": ("Même zone", "同位置"),
    "Capture the same area of the screen again as the selected screenshot  (Ctrl+Shift+R)\nGlobal hotkey from anywhere: Ctrl+Alt+R":
        ("Capturer à nouveau exactement la même zone de l'écran que la capture sélectionnée  (Ctrl+Maj+R)\n"
         "Raccourci global partout : Ctrl+Alt+R",
         "按选中截图的位置，重新截取屏幕上完全相同的区域  (Ctrl+Shift+R)\n任意位置全局快捷键：Ctrl+Alt+R"),
    "Compare": ("Comparer", "对比"),
    "Compare two screenshots with a slider and highlight the differences  (Ctrl+Shift+C)":
        ("Comparer deux captures avec un curseur et surligner les différences  (Ctrl+Maj+C)",
         "用滑块对比两张截图，并高亮显示不同之处  (Ctrl+Shift+C)"),
    "⚠ This screenshot has no saved screen position (taken with an older version, a scrolling capture or a blank canvas) - take a new capture first":
        ("⚠ Cette capture n'a pas de position d'écran enregistrée (ancienne version, capture défilante ou toile vierge) - faites d'abord une nouvelle capture",
         "⚠ 这张截图没有保存屏幕位置（旧版本截的、长截图或空白画布），请先新截一张"),
    "No screen position": ("Pas de position d'écran", "没有屏幕位置"),
    "⚠ That area is no longer on the screen (monitor layout changed)":
        ("⚠ Cette zone n'est plus à l'écran (disposition des moniteurs modifiée)", "⚠ 该区域已不在屏幕上（显示器布局已改变）"),
    "Screenshot #{n} re-captured the area of #{m}": ("Capture #{n} : même zone que #{m}", "截图 #{n}：已按 #{m} 的位置重新截取"),
    "Take at least two screenshots to compare them": ("Faites au moins deux captures pour les comparer", "至少需要两张截图才能对比"),
    "{n} difference(s) marked on #{m}": ("{n} différence(s) marquée(s) sur #{m}", "已在 #{m} 上标出 {n} 处不同"),
    "Capture the same spot again": ("Capturer à nouveau la même zone", "按同位置重新截图"),
    "Compare with #{n}": ("Comparer avec #{n}", "与 #{n} 对比"),
    "Compare…": ("Comparer…", "对比…"),
    "synced zoom - Ctrl+0 to reset": ("zoom synchronisé - Ctrl+0 pour revenir", "同步缩放 - Ctrl+0 恢复"),
    "Compare screenshots": ("Comparer des captures", "对比截图"),
    "Before": ("Avant", "之前"),
    "After": ("Après", "之后"),
    "Slider": ("Curseur", "滑块"),
    "Side by side": ("Côte à côte", "并排"),
    "Highlight differences": ("Surligner les différences", "高亮不同之处"),
    "Tolerance": ("Tolérance", "容差"),
    "Copy comparison": ("Copier la comparaison", "复制对比图"),
    "Mark differences on 'After'": ("Marquer les différences sur « Après »", "在「之后」图上标出不同"),
    "Open after each recapture": ("Ouvrir après chaque nouvelle capture de la zone", "每次同位置重截后自动打开"),
    "#{a} → #{b}": ("#{a} → #{b}", "#{a} → #{b}"),
    "No differences found": ("Aucune différence trouvée", "没有发现不同"),
    "{n} changed area(s), {p} pixels": ("{n} zone(s) modifiée(s), {p} pixels", "{n} 处不同，{p} 个像素"),
    "Sizes differ ({a} vs {b}) - only the overlapping top-left part is compared":
        ("Tailles différentes ({a} / {b}) - seule la partie commune en haut à gauche est comparée",
         "尺寸不同（{a} 与 {b}），只对比左上角重叠的部分"),
    "Wheel: zoom · middle/right-drag: pan · double-click: fit":
        ("Molette : zoom · glisser clic milieu/droit : déplacer · double-clic : ajuster",
         "滚轮：缩放 · 中键/右键拖动：平移 · 双击：适应窗口"),
    "comparison": ("comparaison", "对比图"),
    "SHORTCUTS": (
        "Ctrl+Alt+S   capture depuis n'importe où (global)\n"
        "Ctrl+N         nouvelle capture\n"
        "Ctrl+Maj+R    recapturer la même zone  ·  Ctrl+Alt+R  depuis n'importe où\n"
        "Ctrl+Maj+C    comparer deux captures\n"
        "Ctrl+C         copier la vue actuelle\n"
        "Ctrl+S         enregistrer la vue   ·   Ctrl+Maj+S  tout enregistrer\n"
        "Ctrl+Z / Y    annuler / rétablir\n"
        "Ctrl+D         dupliquer l'annotation\n"
        "Ctrl+A         tout sélectionner (sur la planche : toutes les captures)\n"
        "Ctrl / Maj + clic   sélection multiple (annotations ou cartes de l'historique)\n"
        "Maj + glisser  sélectionner des annotations avec un cadre\n"
        "Suppr           supprimer l'annotation (ou la capture)\n"
        "Ctrl+Maj+Suppr  supprimer toutes les captures\n"
        "Flèches        déplacer l'annotation (Maj = 10 px)\n"
        "Ctrl+molette  zoom   ·   Ctrl+0 ajuster   ·   Ctrl+1 100 %\n"
        "Clic molette  déplacer la vue\n"
        "1 – 5            Unique / 2×2 / 3×3 / 4×4 / Tout\n"
        "F1                guide d'utilisation\n\n"
        "Outils :  V sélection · P stylo · H surligneur · L ligne · A flèche\n"
        "R rectangle · E ellipse · T texte · C bulle · N numéro\n"
        "S tampon · W tableau · B flou · D distance · M périmètre\n"
        "G surface · Q angle · K échelle\n"
        "X gomme · F remplissage · I pipette   ·   Ctrl+Maj+N page blanche",
        "Ctrl+Alt+S   在任意位置截图（全局）\n"
        "Ctrl+N         新建截图\n"
        "Ctrl+Shift+R  同位置重新截图  ·  Ctrl+Alt+R  任意位置\n"
        "Ctrl+Shift+C  对比两张截图\n"
        "Ctrl+C         复制当前视图\n"
        "Ctrl+S         保存当前视图   ·   Ctrl+Shift+S  全部保存\n"
        "Ctrl+Z / Y    撤销 / 重做\n"
        "Ctrl+D         复制标注\n"
        "Ctrl+A         全选标注（拼图视图下：全选截图）\n"
        "Ctrl / Shift + 点击   多选（标注或历史记录卡片）\n"
        "Shift + 拖动   框选标注\n"
        "Delete          删除标注（或截图）\n"
        "Ctrl+Shift+Delete  删除全部截图\n"
        "方向键         微移标注（Shift = 10 px）\n"
        "Ctrl+滚轮     缩放   ·   Ctrl+0 适应   ·   Ctrl+1 100%\n"
        "中键拖动      平移\n"
        "1 – 5            单张 / 2×2 / 3×3 / 4×4 / 全部\n"
        "F1                使用说明\n\n"
        "工具：V 选择 · P 画笔 · H 荧光笔 · L 直线 · A 箭头\n"
        "R 矩形 · E 椭圆 · T 文字 · C 标注框 · N 编号\n"
        "S 符号 · W 表格 · B 马赛克 · D 距离 · M 周长\n"
        "G 面积 · Q 角度 · K 校准比例\n"
        "X 橡皮擦 · F 油漆桶 · I 取色器   ·   Ctrl+Shift+N 空白画布"),
    # ---------------------------------------------------------------- selecting several (Ctrl / Shift)
    "{n} annotations selected": ("{n} annotations sélectionnées", "已选中 {n} 个标注"),
    "{n} annotation(s) deleted": ("{n} annotation(s) supprimée(s)", "已删除 {n} 个标注"),
    "{n} annotations selected  ·  drag to move them together · Delete · Ctrl+D · colour and size apply to all  ·  Ctrl / Shift + click adds or removes one":
        ("{n} annotations sélectionnées  ·  glisser pour les déplacer ensemble · Suppr · Ctrl+D · couleur et taille s'appliquent à toutes  ·  Ctrl / Maj + clic ajoute ou retire",
         "已选中 {n} 个标注  ·  拖动可一起移动 · Delete 删除 · Ctrl+D 复制 · 颜色和大小同时修改  ·  Ctrl / Shift + 点击可加选或取消"),
    "Select all annotations": ("Sélectionner toutes les annotations", "全选标注"),
    "{n} screenshots selected  ·  right-click for what to do with them · Delete removes them":
        ("{n} captures sélectionnées  ·  clic droit pour les actions · Suppr les supprime",
         "已选中 {n} 张截图  ·  右键查看可用操作 · Delete 删除"),
    "{n} screenshots selected": ("{n} captures sélectionnées", "已选中 {n} 张截图"),
    "{n} screenshots": ("{n} captures", "{n} 张截图"),
    "Copy together as one picture": ("Copier ensemble en une seule image", "合成一张图复制"),
    "Compare these two": ("Comparer ces deux captures", "对比这两张"),
    "Put at the end of the board": ("Placer en fin de planche", "移到拼图最后"),
    "{n} screenshot(s) put at the end of the board": ("{n} capture(s) placée(s) en fin de planche", "已把 {n} 张截图移到拼图最后"),
    "Save as PNG files…": ("Enregistrer en fichiers PNG…", "保存为 PNG 文件…"),
    "Save in one PDF…": ("Enregistrer dans un seul PDF…", "保存为一个 PDF…"),
    "Delete {n} screenshots…": ("Supprimer {n} captures…", "删除这 {n} 张截图…"),
    # ---------------------------------------------------------------- Paint-style tools
    "Eraser": ("Gomme", "橡皮擦"),
    "Fill": ("Remplissage", "油漆桶"),
    "Colour picker": ("Pipette", "取色器"),
    "Crop": ("Rogner", "裁剪"),
    "Eraser  (X)  - rubs out annotations, never the screenshot itself":
        ("Gomme  (X)  - efface les annotations, jamais la capture elle-même", "橡皮擦  (X)  - 擦掉标注，不会擦掉截图本身"),
    "Fill with colour  (F)  - fills an area of the same colour, like Paint":
        ("Remplir de couleur  (F)  - remplit une zone de même couleur, comme Paint", "油漆桶  (F)  - 像“画图”一样填充颜色相同的区域"),
    "Colour picker  (I)  - takes a colour from the picture":
        ("Pipette  (I)  - prend une couleur dans l'image", "取色器  (I)  - 从图片上取颜色"),
    "Crop  - drag the part of the picture to keep": ("Rogner  - glissez la partie de l'image à garder", "裁剪  - 拖出要保留的部分"),
    "  ·  drag over annotations to rub them out (line width = eraser size)":
        ("  ·  glissez sur les annotations pour les effacer (épaisseur = taille de la gomme)",
         "  ·  在标注上拖动即可擦掉（线宽 = 橡皮擦大小）"),
    "  ·  click an area to fill it with the current colour":
        ("  ·  cliquez sur une zone pour la remplir avec la couleur actuelle", "  ·  点击区域，用当前颜色填充"),
    "  ·  click the picture to take its colour": ("  ·  cliquez sur l'image pour prendre sa couleur", "  ·  点击图片取色"),
    "  ·  drag the part to keep · Ctrl+Z undoes": ("  ·  glissez la partie à garder · Ctrl+Z annule", "  ·  拖出要保留的部分 · Ctrl+Z 撤销"),
    "Colour picked: {c}": ("Couleur prise : {c}", "已取色：{c}"),
    "IMAGE": ("IMAGE", "图像"),
    "Rotate left": ("Rotation à gauche", "向左旋转"),
    "Rotate right": ("Rotation à droite", "向右旋转"),
    "Flip horizontal": ("Miroir horizontal", "水平翻转"),
    "Flip vertical": ("Miroir vertical", "垂直翻转"),
    "Resize…": ("Redimensionner…", "调整大小…"),
    "Resize": ("Redimensionner", "调整大小"),
    "Turn 90° to the left": ("Tourner de 90° vers la gauche", "向左转 90°"),
    "Turn 90° to the right": ("Tourner de 90° vers la droite", "向右转 90°"),
    "Mirror left ↔ right": ("Miroir gauche ↔ droite", "左右镜像"),
    "Mirror top ↔ bottom": ("Miroir haut ↔ bas", "上下镜像"),
    "Drag the part of the picture to keep": ("Glissez la partie de l'image à garder", "拖出要保留的部分"),
    "Make the picture bigger or smaller": ("Agrandir ou réduire l'image", "放大或缩小图片"),
    "New size in % of {w} × {h} px:": ("Nouvelle taille en % de {w} × {h} px :", "新尺寸（{w} × {h} px 的百分比）："),
    "That picture would be too big.": ("Cette image serait trop grande.", "图片会太大。"),
    "Picture changed: {w} × {h} px  ·  Ctrl+Z undoes": ("Image modifiée : {w} × {h} px  ·  Ctrl+Z annule",
                                                        "图片已修改：{w} × {h} px  ·  Ctrl+Z 撤销"),
    "New blank canvas": ("Nouvelle page blanche", "新建空白画布"),
    "New blank canvas…": ("Nouvelle page blanche…", "新建空白画布…"),
    "An empty page to draw on, like Paint  (Ctrl+Shift+N)": ("Une page vide pour dessiner, comme Paint  (Ctrl+Maj+N)",
                                                            "像“画图”一样新建空白页来画画  (Ctrl+Shift+N)"),
    "Blank canvas #{n} added  ({w} × {h})": ("Page blanche n° {n} ajoutée  ({w} × {h})", "已新建空白画布 #{n}  ({w} × {h})"),
    "Ctrl+Shift+N opens a blank canvas to draw on.": ("Ctrl+Maj+N ouvre une page blanche pour dessiner.",
                                                     "按 Ctrl+Shift+N 新建空白画布来画画。"),
    "Width": ("Largeur", "宽度"),
    "Height": ("Hauteur", "高度"),
    "Width and height must be 16 to 8000 px.": ("La largeur et la hauteur doivent être entre 16 et 8000 px.",
                                                "宽度和高度必须在 16 到 8000 px 之间。"),
    # ---------------------------------------------------------------- table, symbols
    "Table  (W)  - drag to place it, double-click a cell to type":
        ("Tableau  (W)  - tracez-le, double-cliquez sur une case pour écrire", "表格  (W)  - 拖出表格，双击格子输入文字"),
    "Table": ("Tableau", "表格"),
    "TABLE": ("TABLEAU", "表格"),
    "Rows": ("Lignes", "行数"),
    "Columns": ("Colonnes", "列数"),
    "Header row": ("Ligne d'en-tête", "表头行"),
    "White background": ("Fond blanc", "白色底"),
    "Double-click a cell to type · Tab = next cell · Enter = cell below · Shift+Enter = new line · drag the white dots on the lines to resize columns and rows · right-click for more":
        ("Double-clic sur une case pour écrire · Tab = case suivante · Entrée = case du dessous · "
         "Maj+Entrée = nouvelle ligne · tirez les points blancs des traits pour changer la largeur des colonnes "
         "et la hauteur des lignes · clic droit pour plus",
         "双击格子输入文字 · Tab = 下一格 · Enter = 下面一格 · Shift+Enter = 格内换行 · "
         "拖动线上的白点可调列宽和行高 · 右键有更多操作"),
    "Text size, font, bold and alignment apply to the whole table":
        ("Taille, police, gras et alignement s'appliquent à tout le tableau", "字号、字体、加粗和对齐作用于整个表格"),
    "Typing in the table  ·  Tab = next cell  ·  Enter = cell below  ·  Esc = done":
        ("Saisie dans le tableau  ·  Tab = case suivante  ·  Entrée = case du dessous  ·  Échap = terminé",
         "正在表格中输入  ·  Tab = 下一格  ·  Enter = 下面一格  ·  Esc = 完成"),
    "Edit cell": ("Modifier la case", "编辑这一格"),
    "Insert row above": ("Insérer une ligne au-dessus", "在上方插入行"),
    "Insert row below": ("Insérer une ligne en dessous", "在下方插入行"),
    "Insert column left": ("Insérer une colonne à gauche", "在左侧插入列"),
    "Insert column right": ("Insérer une colonne à droite", "在右侧插入列"),
    "Delete row": ("Supprimer la ligne", "删除行"),
    "Delete column": ("Supprimer la colonne", "删除列"),
    "Symbols": ("Symboles", "特殊符号"),
    "Symbols…": ("Symboles…", "特殊符号…"),
    "More symbols…": ("Plus de symboles…", "更多符号…"),
    "Insert ✓ ✗ ★ → ⚠ ± ° Ø ≤ ≥ … into the text you are typing":
        ("Insérer ✓ ✗ ★ → ⚠ ± ° Ø ≤ ≥ … dans le texte en cours", "在正在输入的文字里插入 ✓ ✗ ★ → ⚠ ± ° Ø ≤ ≥ …"),
    "Any symbol of the symbol panel can be a stamp":
        ("Tout symbole du panneau peut servir de tampon", "符号面板里的任何符号都可以当印章用"),
    "Click a symbol: it goes into the text or table cell you are typing in,\notherwise it becomes the stamp (click on the screenshot to place it).":
        ("Cliquez sur un symbole : il va dans le texte ou la case en cours de saisie,\n"
         "sinon il devient le tampon (cliquez sur la capture pour le poser).",
         "点一下符号：正在输入文字或表格时插入到光标处，\n否则作为印章使用（再点截图放置）。"),
    "Click on the screenshot to place {sym}": ("Cliquez sur la capture pour poser {sym}", "点截图放置 {sym}"),
    "Marks": ("Marques", "标记"),
    "Arrows": ("Flèches", "箭头"),
    "Engineering": ("Technique", "工程"),
    "Maths": ("Maths", "数学"),
    "Greek": ("Grec", "希腊字母"),
    "Numbers": ("Numéros", "编号"),
    # ---------------------------------------------------------------- optional extra features
    "Extra features": ("Fonctions supplémentaires", "扩展功能"),
    "Pin to screen": ("Épingler à l'écran", "贴图置顶"),
    "Text recognition (OCR)": ("Reconnaissance de texte (OCR)", "文字识别 (OCR)"),
    "Scrolling capture": ("Capture défilante", "长截图 / 滚动截图"),
    "Screen recording (GIF / MP4)": ("Enregistrement d'écran (GIF / MP4)", "录屏 (GIF / MP4)"),
    "Scrolling": ("Défilante", "长截图"),
    "Pin": ("Épingler", "贴图"),
    "Text": ("Texte", "识字"),
    "Record": ("Filmer", "录屏"),
    "Pin the screenshot above all windows  (Ctrl+P)\nDrag to move · wheel to zoom · Ctrl+wheel opacity · double-click or Esc to close":
        ("Épingler la capture au-dessus de toutes les fenêtres  (Ctrl+P)\nGlisser = déplacer · molette = zoom · Ctrl+molette = opacité · double-clic ou Échap = fermer",
         "把截图钉在所有窗口最上层  (Ctrl+P)\n拖动移动 · 滚轮缩放 · Ctrl+滚轮调透明度 · 双击或 Esc 关闭"),
    "Extract the text of the screenshot  (Ctrl+T)\nWindows OCR, works offline":
        ("Extraire le texte de la capture  (Ctrl+T)\nOCR de Windows, hors ligne", "识别截图中的文字  (Ctrl+T)\n使用 Windows 自带 OCR，离线可用"),
    "Record part of the screen as a GIF or MP4 video  (Ctrl+R)\nEsc or Stop to finish":
        ("Filmer une partie de l'écran en GIF ou en vidéo MP4  (Ctrl+R)\nÉchap ou Arrêter pour terminer", "把屏幕的一部分录成 GIF 动图或 MP4 视频  (Ctrl+R)\n按 Esc 或「停止」结束"),
    "Extract text (OCR)": ("Extraire le texte (OCR)", "识别文字 (OCR)"),
    "Take or select a screenshot first": ("Faites ou sélectionnez d'abord une capture", "请先截图或选中一张截图"),
    "pinned image": ("image épinglée", "贴图"),
    "Pinned  ·  drag to move, wheel to zoom, Ctrl+wheel opacity, double-click or Esc to close":
        ("Épinglée  ·  glisser = déplacer, molette = zoom, Ctrl+molette = opacité, double-clic ou Échap = fermer",
         "已贴图  ·  拖动移动，滚轮缩放，Ctrl+滚轮调透明度，双击或 Esc 关闭"),
    "Actual size": ("Taille réelle", "原始大小"),
    "Save as…": ("Enregistrer sous…", "另存为…"),
    "Close all pinned images": ("Fermer toutes les images épinglées", "关闭所有贴图"),
    "Auto": ("Auto", "自动"),
    "Copy text": ("Copier le texte", "复制文字"),
    "Recognising text…": ("Reconnaissance du texte…", "正在识别文字…"),
    "OCR failed: {e}": ("Échec de l'OCR : {e}", "文字识别失败：{e}"),
    "Windows OCR is not available on this computer.": ("L'OCR de Windows n'est pas disponible sur cet ordinateur.",
                                                       "这台电脑上无法使用 Windows OCR。"),
    "No OCR language is installed. Add one in Windows Settings → Time & language → Language & region (a language with “Optical character recognition”).":
        ("Aucune langue OCR n'est installée. Ajoutez-en une dans Paramètres Windows → Heure et langue → Langue et région (langue avec « Reconnaissance optique de caractères »).",
         "没有安装 OCR 语言。请在 Windows 设置 → 时间和语言 → 语言和区域 中添加一种带「光学字符识别」的语言。"),
    "No text found.": ("Aucun texte trouvé.", "没有识别到文字。"),
    "{n} lines · language {lang} · copied to the clipboard": ("{n} ligne(s) · langue {lang} · copié dans le presse-papiers",
                                                              "{n} 行 · 语言 {lang} · 已复制到剪贴板"),
    "✓ Text copied": ("✓ Texte copié", "✓ 文字已复制"),
    "Starting…": ("Démarrage…", "正在开始…"),
    "Auto-scroll": ("Défilement auto", "自动滚动"),
    "Pause": ("Pause", "暂停"),
    "Done": ("Terminé", "完成"),
    "This window does not scroll by itself - scroll down by hand, then Done or Esc":
        ("Cette fenêtre ne défile pas toute seule - faites défiler à la main, puis Terminé ou Échap",
         "这个窗口无法自动滚动，请用鼠标滚轮手动往下滚，滚完点「完成」或按 Esc"),
    "{h} px  ·  scroll down (by hand or Auto-scroll)  ·  Esc = done":
        ("{h} px  ·  faites défiler vers le bas (à la main ou défilement auto)  ·  Échap = terminé",
         "{h} px  ·  向下滚动（手动或自动滚动）  ·  Esc = 完成"),
    "⚠ Lost track – scroll back up a little, then more slowly": ("⚠ Raccord perdu – remontez un peu, puis défilez plus lentement",
                                                                  "⚠ 拼接中断 —— 请往回滚一点，再慢一些向下滚"),
    "Stop": ("Arrêter", "停止"),
    "Esc or Stop to finish": ("Échap ou Arrêter pour terminer", "按 Esc 或「停止」结束"),
    "Recording cancelled": ("Enregistrement annulé", "已取消录屏"),
    "Recording discarded": ("Enregistrement abandonné", "录屏未保存"),
    "Save recording as": ("Enregistrer la vidéo sous", "录屏另存为"),
    "GIF animation": ("Animation GIF", "GIF 动图"),
    "MP4 video": ("Vidéo MP4", "MP4 视频"),
    "Saving {f}…": ("Enregistrement du {f}…", "正在保存 {f}…"),
    "MP4 recording failed ({e}) - recording a GIF instead": ("L'enregistrement MP4 a échoué ({e}) - enregistrement en GIF",
                                                             "MP4 录制失败（{e}），改为录 GIF"),
    "microphone": ("micro", "麦克风"),
    "system sound": ("son du système", "系统声音"),
    "no {what} recorded (device not available)": ("pas de {what} enregistré (appareil indisponible)", "没有录到{what}（设备不可用）"),
    "Recording format": ("Format d'enregistrement", "录屏格式"),
    "MP4 video (no length limit, sound)": ("Vidéo MP4 (sans limite de durée, avec son)", "MP4 视频（不限时长，可录声音）"),
    "MP4 video (needs ffmpeg)": ("Vidéo MP4 (nécessite ffmpeg)", "MP4 视频（需要 ffmpeg）"),
    "GIF animation (up to 60 s)": ("Animation GIF (60 s max.)", "GIF 动图（最长 60 秒）"),
    "Record microphone": ("Enregistrer le micro", "录制麦克风"),
    "Record system sound": ("Enregistrer le son du système", "录制系统声音"),
    "(needs PyAudioWPatch)": ("(nécessite PyAudioWPatch)", "（需要 PyAudioWPatch）"),
    "Saving {f}… {p}%": ("Enregistrement du {f}… {p} %", "正在保存 {f}… {p}%"),
    "{f} saved: {p}": ("{f} enregistré : {p}", "{f} 已保存：{p}"),
    "✓ {f} saved": ("✓ {f} enregistré", "✓ {f} 已保存"),
    "  ·  stopped at the length limit": ("  ·  arrêté à la durée maximale", "  ·  已达到最长时长，自动停止"),
    "Recording frame rate": ("Images par seconde (vidéo)", "录屏帧率"),
    "{n} frames / s": ("{n} images / s", "{n} 帧/秒"),
    "Ctrl+P         pin screenshot to the screen": ("Ctrl+P         épingler la capture à l'écran", "Ctrl+P         贴图置顶"),
    "Ctrl+T         extract text (OCR)": ("Ctrl+T         extraire le texte (OCR)", "Ctrl+T         识别文字 (OCR)"),
    # ---------------------------------------------------------------- board report
    "Export board as a report (PDF / Word)…": ("Exporter la planche en rapport (PDF / Word)…", "拼图导出为报告 (PDF / Word)…"),
    "Copy board measurements as a table (Excel)": ("Copier les mesures de la planche (Excel)", "复制拼图测量结果表 (Excel)"),
    "Board report": ("Rapport de la planche", "拼图报告"),
    "Report title:": ("Titre du rapport :", "报告标题："),
    "Screenshot report": ("Rapport de captures", "截图报告"),
    "Created {d}": ("Créé le {d}", "创建于 {d}"),
    "{n} screenshot(s)": ("{n} capture(s)", "{n} 张截图"),
    "Notes": ("Notes", "备注"),
    "Measurements": ("Mesures", "测量结果"),
    "Measurement summary": ("Récapitulatif des mesures", "测量汇总表"),
    "Page {i} / {n}": ("Page {i} / {n}", "第 {i} / {n} 页"),
    "Screenshot": ("Capture", "截图"),
    "No.": ("N°", "序号"),
    "Type": ("Type", "类型"),
    "Value": ("Valeur", "数值"),
    "Unit": ("Unité", "单位"),
    "The board is empty": ("La planche est vide", "拼图是空的"),
    "Report saved: {p}": ("Rapport enregistré : {p}", "报告已保存：{p}"),
    "✓ Report saved": ("✓ Rapport enregistré", "✓ 报告已保存"),
    "No measurements on the board": ("Aucune mesure sur la planche", "拼图上没有测量"),
    "Measurement table copied ({n} rows) - paste it into Excel":
        ("Tableau des mesures copié ({n} lignes) - collez-le dans Excel", "测量结果表已复制（{n} 行），可直接粘贴到 Excel"),
    "✓ Copied": ("✓ Copié", "✓ 已复制"),
    "Ctrl+R         record screen (GIF / MP4)  ·  Esc stop": ("Ctrl+R         filmer l'écran (GIF / MP4)  ·  Échap = arrêter",
                                                              "Ctrl+R         录屏 (GIF / MP4)  ·  Esc 停止"),
}

SHORTCUTS_EN = (
    "Ctrl+Alt+S   capture from anywhere (global)\n"
    "Ctrl+N         new capture\n"
    "Ctrl+Shift+R  capture the same spot again  ·  Ctrl+Alt+R  from anywhere\n"
    "Ctrl+Shift+C  compare two screenshots\n"
    "Ctrl+C         copy current view\n"
    "Ctrl+S         save current view    ·   Ctrl+Shift+S  save all\n"
    "Ctrl+Z / Y    undo / redo\n"
    "Ctrl+D         duplicate annotation\n"
    "Ctrl+A         select all annotations (on the board: all screenshots)\n"
    "Ctrl / Shift + click   select several (annotations or history cards)\n"
    "Shift + drag   select annotations with a box\n"
    "Delete          delete annotation (or screenshot)\n"
    "Ctrl+Shift+Delete  delete all screenshots\n"
    "Arrows         nudge annotation (Shift = 10 px)\n"
    "Ctrl+wheel    zoom   ·   Ctrl+0 fit   ·   Ctrl+1 100%\n"
    "Middle-drag   pan\n"
    "1 – 5            Single / 2×2 / 3×3 / 4×4 / All\n"
    "F1                user guide\n\n"
    "Tools:  V select · P pen · H highlighter · L line · A arrow\n"
    "R rectangle · E ellipse · T text · C callout · N number\n"
    "S stamp · W table · B blur · D distance · M perimeter\n"
    "G area · Q angle · K calibrate scale\n"
    "X eraser · F fill · I colour picker   ·   Ctrl+Shift+N blank canvas")


def shortcuts_text():
    return SHORTCUTS_EN if LANG[0] == "en" else tr("SHORTCUTS")


# =========================================================================== USER GUIDE
# Format: "# " = heading, "- " = bullet, "> " = tip, other = paragraph
GUIDE = {
    "en": """# MultiCapture – User guide
MultiCapture keeps every screenshot you take. Arrange several of them on one board (2×2, 3×3 …), mark them up, measure, add notes and paste the result straight into an e-mail, Word or Excel.

# 1. Take a screenshot
- Click ＋ New capture, press Ctrl+N in the app, or press Ctrl+Alt+S anywhere in Windows (the app can stay minimised).
- Drag a rectangle on the screen. Esc or right-click cancels.
- Capture mode: Region, Full screen (all monitors) or Last region (repeats the previous rectangle – ideal for a series of the same area).
- Delay: 3, 5 or 10 s to open a menu or tooltip before the capture.
> Every capture is added to the HISTORY on the left. Nothing is ever overwritten.

# 2. Single view and board views
- View buttons at the top (or keys 1–5): Single, 2×2, 3×3, 4×4, All.
- A board shows the most recent screenshots of the board order in one frame.
- Drag a cell onto another cell to swap their positions.
- Double-click a cell to open that screenshot in Single view for editing.
- Right-click a history card → "Move to end of board" to bring an older screenshot back into the board.
- Several screenshots at once: Ctrl + click history cards (or board cells) to add or remove them, Shift + click to take every card between the last one clicked and this one, Ctrl+A on the board to take all. Then right-click one of them: Copy together as one picture, Compare these two, Put at the end of the board, Save as PNG files, Save in one PDF or Delete. The Delete key deletes them all (after one confirmation), Esc ends the selection.
- Drag pictures in from Explorer or a web browser (onto the image or the history). A dialog asks what to do: Merge with the other screenshots (added to the board), Open on its own (kept out of the board – right-click its card → "Add to board" later), or Float on top of the current screenshot.
- Float on top: the picture lies over the screenshot like an annotation. With Select, drag it to move, drag a corner to resize (proportions kept), set a border and the opacity in the PICTURE section, Delete removes it. It is merged into the screenshot when copying or saving. Right-click another history card → "Float on top of the current screenshot" does the same with one of your screenshots.
- Delete ▾: delete the selected screenshot (Delete key), the screenshots of the current board, or ALL screenshots at once (Ctrl+Shift+Delete). You are asked to confirm, with a warning if some were never saved to a file.

# 3. Automatic copy – paste anywhere
- Right after a capture, and after every change, the CURRENT VIEW is copied to the clipboard: one image in Single view, the whole grid in 2×2 / 3×3 / …
- Just press Ctrl+V in Outlook, Teams, Word, Excel, PowerPoint …
- Copy (Ctrl+C) copies it again manually. Turn auto-copy off in Options.

# 4. Annotations (tool bar on the left of the image)
- Pen, Highlighter, Line, Arrow, Rectangle, Ellipse – hold Shift for 45° lines, squares and circles.
- Numbered marker: each click places 1, 2, 3 …
- Stamp: ✔ ✘ ★ ! ? ⚠ … choose the symbol in the right panel.
- Blur: drag over confidential information to pixelate it.
- Colour, line width, fill and opacity are set in the right panel.
> Every annotation stays editable: choose Select (V), click an object, then drag it, pull its white handles, change its colour / size in the right panel, or press Delete. Ctrl+Z / Ctrl+Y = undo / redo (also the ↶ Undo / ↷ Redo buttons in the top bar), Ctrl+D = duplicate, arrow keys = nudge.
- Several annotations at once: with Select, Ctrl + click or Shift + click adds an annotation to the selection (click it again to take it out), Shift + drag on an empty spot draws a box that selects every annotation fully inside it, Ctrl+A selects them all. Drag any of them (or the blue ✥ handle) to move them together; Delete, Ctrl+D, arrow keys, Bring to front / Send to back and the colour, width and font settings on the right apply to all of them, in one undo step. Esc ends the selection. A plain drag on an empty spot still pans the view.

# 5. Text boxes and callouts (like Word)
- Text (T): click where the text should go and type. Enter = new line; click outside, Esc or Ctrl+Enter = finish.
- Callout (C): press on the point to highlight, drag to where the text box goes, release and type – a leader line is drawn automatically.
- Formatting in the TEXT section: font, size, Bold, Italic, Underline, alignment, background colour, border, text colour (COLOUR palette).
- Double-click a text with the Select tool to edit it again; drag it to move it.
- Move handle ✥: a blue round handle with a cross of arrows appears at the top-left corner of the text box while you type and whenever the text (or any annotation) is selected. Drag it to move the object – it works with every tool. The cursor turns into a four-way arrow over anything that can be moved.
- Table (W): choose the number of rows and columns in the TABLE section, then drag on the image (or just click). Double-click a cell to type; Tab = next cell (in the last cell it adds a row), Enter = cell below, Shift+Enter = new line. Drag the white dots on the lines to change column widths and row heights; right-click a cell to insert or delete rows and columns. Line colour, width, font and size are set in the right panel.
- Ω Symbols…: one click inserts ✓ ✗ ★ → ⚠ ± ° Ø ⌀ ≤ ≥ ① … into the text box or table cell you are typing in. When nothing is being typed, the symbol becomes the stamp.

# 6. Measurement (like a PDF reader)
- Distance (D): drag a line – the length is shown.
- Perimeter (M) and Area (G): click the points one by one; double-click, Enter or right-click finishes, Esc cancels. Area also shows the perimeter.
- Angle (Q): click 3 points, the vertex being the second one.
- Set the real scale: Calibrate (K) – draw a line over a known dimension and enter its real length (mm, cm, m, in …). All measurements of that screenshot are then shown in real units.
- "Set scale…" lets you type the value of 1 pixel directly. Tick "Use as default…" to apply it to all screenshots without their own scale (same zoom level).
- The status bar shows the cursor position in pixels and in real units.

# 7. Notes
- The NOTES box on the right belongs to the selected screenshot – write remarks, part numbers, actions …
- With "Include notes when copying / exporting" ticked, the notes are printed under the image when copying, saving or exporting to PDF.

# 8. Save and export
- Save ▾ → current view, selected screenshot (PNG, JPG, BMP or PDF), all screenshots as PNG files, all screenshots or the board as a multi-page PDF.
- Options → Auto-save PNG files to a folder of your choice.
- When you close the app while some screenshots were never saved to a file, a dialog asks what to save (current view, only the unsaved screenshots, all screenshots, or everything in one PDF), the format (PNG, JPG, BMP, TIFF, WEBP, PDF), the folder (Browse…) and the file name. "Close without saving" still keeps the history; "Cancel" keeps the app open. Untick "Ask every time…" (or Options → Ask to save when closing) to stop the question.
- The history (images, annotations, notes) is kept between launches. Options → Clear history removes it.

# 9. Zoom and navigation
- Ctrl+mouse wheel = zoom, mouse wheel = scroll, middle button drag = pan.
- Fit / 100 % / − / + at the bottom right. Ctrl+0 = fit, Ctrl+1 = 100 %.

# 10. Language
- Options → Language: English, Français, 中文 (restart of the app).

# 11. Extra features (optional, off by default)
Options → Extra features switches each of these on or off. While a feature is off it adds nothing to the window.
- Pin to screen: the 📌 Pin button (or Ctrl+P, or right-click a history card) floats the screenshot above all windows. Drag to move, wheel to zoom, Ctrl+wheel to change opacity, double-click or Esc to close, right-click for Copy / Save / Close all.
- Text recognition (OCR): the 🔤 Text button (or Ctrl+T) reads the text of the screenshot with the OCR engine built into Windows 10/11. It works offline. The text is copied to the clipboard and can be edited in the window. Pick the language in the window; Windows only offers the languages installed with "Optical character recognition" (Settings → Time & language → Language & region).
- Scrolling capture: adds "Scrolling" to the capture mode list. Drag a rectangle over the part of the window that scrolls. It then scrolls down by itself and joins the frames into one long image. Click Pause to scroll by hand instead (slowly), and Done or Esc to finish. It stops by itself at the end of the page. If the window does not react to automatic scrolling, it switches to scrolling by hand.
- Screen recording (GIF / MP4): the ⏺ Record button (or Ctrl+R) records a rectangle (or the full screen in Full screen mode). Esc or Stop ends it, then you choose where to save. Options → Extra features → Recording format: MP4 video (default: small files, no length limit, can record the microphone and/or the system sound - switch them on in the same menu) or animated GIF (no sound, up to 60 s). MP4 and sound are included in the .exe; when running from source, install them with pip install imageio-ffmpeg pyaudiowpatch. The frame rate (5, 10 or 15 per second) is in Options → Extra features.
> The control bar and the coloured frame around the region are not part of the capture or the recording.

# 12. Themes
- Click 🎨 Themes to change the colours, the icon of each function and the decorations (restart of the app).
- A theme can also put a frame around the screenshots you copy and export. Turn it on or off with "Add the theme frame to copies and exports". Auto-saved PNG files never get a frame.
- 🎲 "Random theme now" switches to one of your installed themes at random. Tick "Use a random theme each time the app starts" to get a different theme at every start.
- "Get online themes" looks for new themes on GitHub. This is the only time the app goes online.
- "Import .zip…" installs a theme someone sent you. "Make my own from this…" copies a theme into your themes folder so you can change its pictures and colours.
> How to make a theme: see docs/THEMES.md on the project's GitHub page ("How to make a theme" button).

# 13. Paint tools
- Eraser (X): drag over annotations to rub them out. Pen and highlighter strokes and fills lose only the part under the eraser; other annotations it touches are removed. The screenshot itself is never erased. LINE WIDTH sets the eraser size.
- Fill (F): click an area to fill it with the current colour – the area of the same colour around the click, as you see it with the annotations. The fill stays an annotation: select it to change its colour, move it or delete it.
- Colour picker (I): click the picture to take its colour; the previous tool comes back.
- IMAGE section of the right panel (Select tool, nothing selected), also in the right-click menu: Rotate left / right, Flip horizontal / vertical, Crop (drag the part to keep) and Resize… (in %). Annotations follow the picture. Ctrl+Z undoes.
- New blank canvas… (Ctrl+Shift+N): an empty page in the history, with the size and background colour you choose, to draw on like in Paint with the pen, shapes and text.
> The tool bar uses two columns when the window is too low for one.

# 14. Same spot and compare
- ⟳ Same spot (Ctrl+Shift+R, or Ctrl+Alt+R anywhere in Windows) captures exactly the same screen area as the selected screenshot again – ideal for "before / after" or to follow a change. Right-click a history card → "Capture the same spot again" works for any screenshot.
- After a same-spot capture the Compare window opens: drag the divider to reveal the before or the after image, or choose "Side by side". Both images always share the same zoom and position (wheel = zoom, middle/right-drag = pan, double-click = fit).
- "Highlight differences" tints every changed pixel red and draws a red box around each changed area. "Tolerance" ignores small colour changes. "Mark differences on 'After'" adds the red boxes to the newer screenshot as normal (editable) rectangles; "Copy comparison" copies both images side by side.
- ◧ Compare (Ctrl+Shift+C) compares the selected screenshot with the one it re-captured (or the previous one); pick any two in the Before / After lists. Screenshots of different sizes are aligned at the top-left corner.
- Synced zoom on a board: Ctrl+wheel over a cell zooms ALL cells to the same place, the wheel / middle-drag pans them together, Ctrl+0 or Fit goes back.
""",
    "fr": """# MultiCapture – Guide d'utilisation
MultiCapture conserve toutes vos captures d'écran. Disposez-en plusieurs sur une même planche (2×2, 3×3 …), annotez-les, mesurez, ajoutez des notes et collez le résultat directement dans un e-mail, Word ou Excel.

# 1. Faire une capture
- Cliquez sur ＋ Nouvelle capture, appuyez sur Ctrl+N dans l'application, ou sur Ctrl+Alt+S n'importe où dans Windows (l'application peut rester réduite).
- Tracez un rectangle à l'écran. Échap ou clic droit pour annuler.
- Mode de capture : Zone, Plein écran (tous les écrans) ou Dernière zone (répète le rectangle précédent – idéal pour une série sur la même zone).
- Délai : 3, 5 ou 10 s pour ouvrir un menu ou une info-bulle avant la capture.
> Chaque capture est ajoutée à l'HISTORIQUE à gauche. Rien n'est jamais écrasé.

# 2. Vue unique et planches
- Boutons Vue en haut (ou touches 1–5) : Unique, 2×2, 3×3, 4×4, Tout.
- Une planche affiche les captures les plus récentes dans un seul cadre.
- Faites glisser une case sur une autre pour échanger leurs positions.
- Double-cliquez sur une case pour ouvrir la capture en vue Unique et la modifier.
- Clic droit sur une carte de l'historique → « Placer en fin de planche » pour remettre une ancienne capture dans la planche.
- Plusieurs captures à la fois : Ctrl + clic sur les cartes de l'historique (ou les cases de la planche) pour les ajouter ou les retirer, Maj + clic pour prendre toutes les cartes entre la dernière cliquée et celle-ci, Ctrl+A sur la planche pour tout prendre. Puis clic droit sur l'une d'elles : Copier ensemble en une seule image, Comparer ces deux captures, Placer en fin de planche, Enregistrer en fichiers PNG, Enregistrer dans un seul PDF ou Supprimer. La touche Suppr les supprime toutes (après une confirmation), Échap annule la sélection.
- Glissez des images depuis l'Explorateur ou un navigateur web (sur l'image ou sur l'historique). Une fenêtre demande quoi faire : Fusionner avec les autres captures (ajoutées à la planche), Ouvrir à part (hors de la planche – clic droit sur sa carte → « Ajouter à la planche » plus tard), ou Superposer sur la capture actuelle.
- Superposer : l'image est posée sur la capture comme une annotation. Avec Sélection, faites-la glisser pour la déplacer, tirez un coin pour la redimensionner (proportions conservées), réglez bordure et opacité dans la section IMAGE ; Suppr l'enlève. Elle est fusionnée avec la capture à la copie ou à l'enregistrement. Clic droit sur une autre carte de l'historique → « Superposer sur la capture actuelle » fait de même avec une de vos captures.
- Supprimer ▾ : supprimer la capture sélectionnée (touche Suppr), les captures de la planche actuelle, ou TOUTES les captures d'un coup (Ctrl+Maj+Suppr). Une confirmation est demandée, avec un avertissement si certaines n'ont jamais été enregistrées.

# 3. Copie automatique – collez partout
- Juste après une capture, et après chaque modification, la VUE ACTUELLE est copiée dans le presse-papiers : une image en vue Unique, la grille complète en 2×2 / 3×3 / …
- Il suffit de faire Ctrl+V dans Outlook, Teams, Word, Excel, PowerPoint …
- Copier (Ctrl+C) recopie manuellement. Désactivez la copie automatique dans Options.

# 4. Annotations (barre d'outils à gauche de l'image)
- Stylo, Surligneur, Ligne, Flèche, Rectangle, Ellipse – Maj pour des lignes à 45°, des carrés et des cercles.
- Repère numéroté : chaque clic place 1, 2, 3 …
- Tampon : ✔ ✘ ★ ! ? ⚠ … choisissez le symbole dans le panneau de droite.
- Flou : glissez sur une information confidentielle pour la pixeliser.
- Couleur, épaisseur, remplissage et opacité se règlent dans le panneau de droite.
> Toutes les annotations restent modifiables : outil Sélection (V), cliquez un objet puis déplacez-le, tirez ses poignées blanches, changez sa couleur / taille à droite, ou appuyez sur Suppr. Ctrl+Z / Ctrl+Y = annuler / rétablir (aussi les boutons ↶ Annuler / ↷ Rétablir de la barre du haut), Ctrl+D = dupliquer, flèches = déplacement fin.
- Plusieurs annotations à la fois : avec Sélection, Ctrl + clic ou Maj + clic ajoute une annotation à la sélection (recliquez pour la retirer), Maj + glisser sur un endroit vide trace un cadre qui sélectionne toutes les annotations entièrement dedans, Ctrl+A les sélectionne toutes. Faites glisser l'une d'elles (ou la poignée bleue ✥) pour les déplacer ensemble ; Suppr, Ctrl+D, les flèches, Premier plan / Arrière-plan et les réglages de couleur, d'épaisseur et de police à droite s'appliquent à toutes, en une seule étape d'annulation. Échap annule la sélection. Glisser sans touche sur un endroit vide déplace toujours la vue.

# 5. Zones de texte et bulles (comme Word)
- Texte (T) : cliquez à l'endroit voulu et tapez. Entrée = nouvelle ligne ; clic à l'extérieur, Échap ou Ctrl+Entrée = terminer.
- Bulle (C) : appuyez sur le point à signaler, glissez jusqu'à l'emplacement du texte, relâchez et tapez – la ligne de rappel est tracée automatiquement.
- Mise en forme dans la section TEXTE : police, taille, Gras, Italique, Souligné, alignement, couleur de fond, bordure, couleur du texte (palette COULEUR).
- Double-cliquez sur un texte avec l'outil Sélection pour le modifier ; glissez-le pour le déplacer.
- Poignée de déplacement ✥ : une poignée ronde bleue avec une croix de flèches apparaît au coin supérieur gauche de la zone de texte pendant la saisie et dès que le texte (ou toute annotation) est sélectionné. Faites-la glisser pour déplacer l'objet – fonctionne avec tous les outils. Le curseur devient une flèche à quatre directions sur tout ce qui peut être déplacé.
- Tableau (W) : choisissez le nombre de lignes et de colonnes dans la section TABLEAU, puis tracez sur l'image (ou cliquez). Double-cliquez sur une case pour écrire ; Tab = case suivante (dans la dernière case, ajoute une ligne), Entrée = case du dessous, Maj+Entrée = nouvelle ligne. Tirez les points blancs des traits pour changer la largeur des colonnes et la hauteur des lignes ; clic droit sur une case pour insérer ou supprimer des lignes et colonnes. Couleur, épaisseur, police et taille dans le panneau de droite.
- Ω Symboles… : un clic insère ✓ ✗ ★ → ⚠ ± ° Ø ⌀ ≤ ≥ ① … dans la zone de texte ou la case en cours de saisie. Si rien n'est en cours de saisie, le symbole devient le tampon.

# 6. Mesure (comme un lecteur PDF)
- Distance (D) : tracez une ligne – la longueur s'affiche.
- Périmètre (M) et Surface (G) : cliquez les points un par un ; double-clic, Entrée ou clic droit pour terminer, Échap pour annuler. La surface affiche aussi le périmètre.
- Angle (Q) : cliquez 3 points, le sommet étant le deuxième.
- Échelle réelle : Calibrer (K) – tracez une ligne sur une cote connue et saisissez sa longueur réelle (mm, cm, m, in …). Toutes les mesures de la capture s'affichent alors en unités réelles.
- « Échelle… » permet de saisir directement la valeur d'un pixel. Cochez « Utiliser comme échelle par défaut… » pour l'appliquer à toutes les captures sans échelle propre (même niveau de zoom).
- La barre d'état affiche la position du curseur en pixels et en unités réelles.

# 7. Notes
- La zone NOTES à droite appartient à la capture sélectionnée – remarques, références, actions …
- Si « Inclure les notes (copie / export) » est coché, les notes sont imprimées sous l'image lors de la copie, de l'enregistrement ou de l'export PDF.

# 8. Enregistrer et exporter
- Enregistrer ▾ → vue actuelle, capture sélectionnée (PNG, JPG, BMP ou PDF), toutes les captures en PNG, toutes les captures ou la planche en PDF multipage.
- Options → Enregistrer automatiquement en PNG dans le dossier de votre choix.
- À la fermeture, si des captures n'ont jamais été enregistrées dans un fichier, une fenêtre demande quoi enregistrer (vue actuelle, seulement les captures non enregistrées, toutes les captures, ou tout dans un PDF), le format (PNG, JPG, BMP, TIFF, WEBP, PDF), le dossier (Parcourir…) et le nom du fichier. « Fermer sans enregistrer » conserve quand même l'historique ; « Annuler » garde l'application ouverte. Décochez « Demander à chaque fermeture » (ou Options) pour ne plus être sollicité.
- L'historique (images, annotations, notes) est conservé entre les lancements. Options → Effacer l'historique pour le supprimer.

# 9. Zoom et navigation
- Ctrl+molette = zoom, molette = défilement, glisser avec le bouton du milieu = déplacer la vue.
- Ajuster / 100 % / − / + en bas à droite. Ctrl+0 = ajuster, Ctrl+1 = 100 %.

# 10. Langue
- Options → Langue : English, Français, 中文 (redémarrage de l'application).

# 11. Fonctions supplémentaires (facultatives, désactivées par défaut)
Options → Fonctions supplémentaires active ou désactive chacune d'elles. Une fonction désactivée n'ajoute rien à la fenêtre.
- Épingler à l'écran : le bouton 📌 Épingler (ou Ctrl+P, ou clic droit sur une carte de l'historique) fait flotter la capture au-dessus de toutes les fenêtres. Glisser = déplacer, molette = zoom, Ctrl+molette = opacité, double-clic ou Échap = fermer, clic droit = Copier / Enregistrer / Tout fermer.
- Reconnaissance de texte (OCR) : le bouton 🔤 Texte (ou Ctrl+T) lit le texte de la capture avec le moteur OCR intégré à Windows 10/11, hors ligne. Le texte est copié dans le presse-papiers et reste modifiable dans la fenêtre. Choisissez la langue dans la fenêtre ; Windows ne propose que les langues installées avec « Reconnaissance optique de caractères » (Paramètres → Heure et langue → Langue et région).
- Capture défilante : ajoute « Défilante » aux modes de capture. Tracez un rectangle sur la partie de la fenêtre qui défile. La page défile ensuite toute seule et les images sont assemblées en une longue capture. Cliquez Pause pour faire défiler à la main (lentement), puis Terminé ou Échap. Elle s'arrête seule en bas de la page. Si la fenêtre ne réagit pas au défilement automatique, elle passe au défilement à la main.
- Enregistrement d'écran (GIF / MP4) : le bouton ⏺ Filmer (ou Ctrl+R) enregistre un rectangle (ou tout l'écran en mode Plein écran). Échap ou Arrêter pour terminer, puis choisissez où l'enregistrer. Options → Fonctions supplémentaires → Format d'enregistrement : vidéo MP4 (par défaut : fichiers légers, sans limite de durée, avec le micro et/ou le son du système - à activer dans le même menu) ou GIF animé (sans son, 60 s max.). Le MP4 et le son sont inclus dans le .exe ; depuis le code source, installez-les avec pip install imageio-ffmpeg pyaudiowpatch. La cadence (5, 10 ou 15 images/s) se règle dans Options → Fonctions supplémentaires.
> La barre de commande et le cadre coloré autour de la zone ne figurent pas dans la capture ni dans la vidéo.

# 12. Thèmes
- Cliquez sur 🎨 Thèmes pour changer les couleurs, l'icône de chaque fonction et les décorations (redémarrage de l'application).
- Un thème peut aussi encadrer les captures que vous copiez et exportez. Activez ou désactivez « Ajouter le cadre du thème aux copies et exports ». Les PNG enregistrés automatiquement n'ont jamais de cadre.
- 🎲 « Thème au hasard » passe à un de vos thèmes installés, choisi au hasard. Cochez « Thème au hasard à chaque démarrage » pour changer de thème à chaque lancement.
- « Thèmes en ligne » cherche de nouveaux thèmes sur GitHub. C'est le seul moment où l'application se connecte.
- « Importer un .zip… » installe un thème qu'on vous a envoyé. « Créer le mien à partir de celui-ci… » copie un thème dans votre dossier pour modifier ses images et couleurs.
> Pour créer un thème : voir docs/THEMES.md sur la page GitHub du projet (bouton « Créer un thème »).

# 13. Outils façon Paint
- Gomme (X) : glissez sur les annotations pour les effacer. Les traits de stylo, de surligneur et les remplissages ne perdent que la partie sous la gomme ; les autres annotations touchées sont supprimées. La capture elle-même n'est jamais effacée. ÉPAISSEUR règle la taille de la gomme.
- Remplissage (F) : cliquez sur une zone pour la remplir avec la couleur actuelle – la zone de même couleur autour du clic, telle que vous la voyez avec les annotations. Le remplissage reste une annotation : sélectionnez-le pour changer sa couleur, le déplacer ou le supprimer.
- Pipette (I) : cliquez sur l'image pour prendre sa couleur ; l'outil précédent revient.
- Section IMAGE du panneau de droite (outil Sélection, rien de sélectionné), aussi dans le menu du clic droit : Rotation gauche / droite, Miroir horizontal / vertical, Rogner (glissez la partie à garder) et Redimensionner… (en %). Les annotations suivent l'image. Ctrl+Z annule.
- Nouvelle page blanche… (Ctrl+Maj+N) : une page vide dans l'historique, de la taille et de la couleur de fond choisies, pour dessiner comme dans Paint.
> La barre d'outils passe sur deux colonnes quand la fenêtre est trop basse.

# 14. Même zone et comparaison
- ⟳ Même zone (Ctrl+Maj+R, ou Ctrl+Alt+R partout dans Windows) capture à nouveau exactement la même zone de l'écran que la capture sélectionnée – idéal pour un « avant / après » ou pour suivre une évolution. Clic droit sur une carte de l'historique → « Capturer à nouveau la même zone » fonctionne pour n'importe quelle capture.
- Ensuite la fenêtre Comparer s'ouvre : faites glisser le séparateur pour voir l'image avant ou après, ou choisissez « Côte à côte ». Les deux images ont toujours le même zoom et la même position (molette = zoom, glisser clic milieu/droit = déplacer, double-clic = ajuster).
- « Surligner les différences » colore en rouge chaque pixel modifié et encadre chaque zone modifiée. « Tolérance » ignore les petits changements de couleur. « Marquer les différences sur « Après » » ajoute les cadres rouges à la capture la plus récente comme des rectangles normaux (modifiables) ; « Copier la comparaison » copie les deux images côte à côte.
- ◧ Comparer (Ctrl+Maj+C) compare la capture sélectionnée avec celle qu'elle reprend (ou la précédente) ; choisissez n'importe quelles captures dans les listes Avant / Après. Des captures de tailles différentes sont alignées en haut à gauche.
- Zoom synchronisé sur une planche : Ctrl+molette sur une case zoome TOUTES les cases au même endroit, la molette / le clic milieu les déplacent ensemble, Ctrl+0 ou Ajuster revient à la vue entière.
""",
    "zh": """# MultiCapture 使用说明
MultiCapture 会保留你截的每一张图。可以把多张截图放在同一个拼图里（2×2、3×3 …），进行标注、测量、写备注，然后直接粘贴到邮件、Word 或 Excel 中。

# 1. 截图
- 点击「＋ 新建截图」，或在软件中按 Ctrl+N，或在 Windows 任意位置按 Ctrl+Alt+S（软件最小化也可以）。
- 在屏幕上拖出一个矩形。按 Esc 或右键取消。
- 截图模式：矩形区域、全屏（所有显示器）、上次区域（重复上一次的矩形，适合连续截同一位置）。
- 延迟：3、5 或 10 秒，方便先打开菜单或提示再截图。
> 每次截图都会添加到左侧的「历史记录」中，永远不会覆盖之前的截图。

# 2. 单张视图和拼图视图
- 顶部的视图按钮（或数字键 1–5）：单张、2×2、3×3、4×4、全部。
- 拼图会把最近的几张截图放在同一个框里显示。
- 把一个格子拖到另一个格子上，即可交换两张截图的位置。
- 双击格子，可切换到单张视图进行编辑。
- 在历史记录卡片上右键 →「移到拼图最后」，可以把较早的截图重新放进拼图。
- 一次选多张截图：按住 Ctrl 点击历史记录卡片（或拼图里的格子）可以加选或取消，按住 Shift 点击会选中上次点击的卡片到这张之间的全部卡片，在拼图视图按 Ctrl+A 全选。然后在其中一张上右键：合成一张图复制、对比这两张、移到拼图最后、保存为 PNG 文件、保存为一个 PDF 或删除。按 Delete 键会把选中的全部删除（确认一次），按 Esc 取消多选。
- 可以从资源管理器或浏览器把图片直接拖进来（拖到图片区或历史记录上）。会弹出选择框：「和现有其他图片合并」（加入拼图）、「单独打开」（不放进拼图，之后可在卡片上右键 →「加入拼图」），或「悬浮到当前图片上」。
- 悬浮：图片像标注一样放在截图上面。用「选择」工具拖动可移动，拖角可缩放（保持比例），在右侧「图片」栏可设置边框和不透明度，按 Delete 删除。复制或保存时会和截图合并成一张图。在另一张历史卡片上右键 →「悬浮到当前图片上」，也可以把自己的截图叠加上去。
- 「删除 ▾」菜单：可以删除选中的截图（Delete 键）、删除当前拼图里的截图，或一次删除全部截图（Ctrl+Shift+Delete）。删除前会让你确认，如果有截图还没保存成文件，也会提醒你。

# 3. 自动复制 —— 随处粘贴
- 截图后以及每次修改后，「当前视图」都会自动复制到剪贴板：单张视图复制单张图片，2×2 / 3×3 … 视图复制整个拼图。
- 在 Outlook、Teams、Word、Excel、PowerPoint 中直接按 Ctrl+V 即可。
- 「复制」按钮（Ctrl+C）可手动再复制一次。可在「选项」中关闭自动复制。

# 4. 标注（图片左侧的工具栏）
- 画笔、荧光笔、直线、箭头、矩形、椭圆 —— 按住 Shift 可画 45° 线、正方形和圆。
- 编号标记：每点一下依次放置 1、2、3 …
- 符号：✔ ✘ ★ ! ? ⚠ …，在右侧面板中选择符号。
- 马赛克：在敏感信息上拖动即可打码。
- 颜色、线宽、填充和不透明度在右侧面板中设置。
> 所有标注都可以随时修改：选择「选择」工具（V），点击对象后可拖动、拉动白色控制点调整大小、在右侧修改颜色 / 大小，或按 Delete 删除。Ctrl+Z / Ctrl+Y 撤销 / 重做（顶部栏也有 ↶ 撤销 / ↷ 重做 按钮），Ctrl+D 复制，方向键微移。
- 一次选多个标注：用「选择」工具，按住 Ctrl 或 Shift 点击标注可以加选（再点一次取消），按住 Shift 在空白处拖动会拉出一个框，框内完整包住的标注都会被选中，Ctrl+A 全选。拖动其中任意一个（或蓝色 ✥ 手柄）就能一起移动；Delete、Ctrl+D、方向键、置于顶层 / 置于底层，以及右侧的颜色、线宽、字体设置都会同时作用于所有选中的标注，并且一步就能撤销。按 Esc 取消多选。不按键直接在空白处拖动仍然是平移视图。

# 5. 文本框和标注框（类似 Word）
- 文字（T）：在需要的位置点击并输入。回车换行；点击外部、按 Esc 或 Ctrl+回车 完成。
- 标注框（C）：在要指出的位置按下，拖到文字框要放的位置，松开后输入文字，引线会自动画出。
- 「文字」区域可设置格式：字体、字号、粗体、斜体、下划线、对齐方式、背景色、边框；文字颜色在「颜色」调色板中选择。
- 用「选择」工具双击文字可再次编辑；拖动即可移动位置。
- 移动手柄 ✥：输入文字时，以及选中文字（或任何标注）后，文本框左上角会出现一个带十字箭头的蓝色圆形手柄。拖动它即可移动对象，任何工具下都可以用。鼠标移到可移动的对象上时，光标会变成四向箭头。
- 表格（W）：在右侧「表格」区选好行数和列数，然后在图上拖出表格（或直接点一下）。双击格子输入文字；Tab = 下一格（在最后一格按 Tab 会自动加一行），Enter = 下面一格，Shift+Enter = 格内换行。拖动线上的白点可调整列宽和行高；右键格子可插入或删除行和列。线条颜色、粗细、字体和字号在右侧面板设置。
- Ω 特殊符号…：点一下就把 ✓ ✗ ★ → ⚠ ± ° Ø ⌀ ≤ ≥ ① … 插入到正在输入的文本框或表格格子里。没有在输入时，点的符号会变成印章。

# 6. 测量（类似 PDF 阅读器）
- 距离（D）：拖出一条线，显示长度。
- 周长（M）和面积（G）：依次点击各点；双击、回车或右键结束，Esc 取消。面积同时显示周长。
- 角度（Q）：点击 3 个点，第 2 个点为顶点。
- 设置实际比例：「校准」（K）—— 在一个已知尺寸上画一条线，输入实际长度（mm、cm、m、in …），这张截图的所有测量值都会换算成实际单位。
- 「设置比例…」可直接输入 1 像素代表的长度。勾选「作为所有未设比例截图的默认比例」后，会应用到所有没有单独比例的截图（适用于相同缩放倍率的截图）。
- 底部状态栏会显示鼠标位置的像素坐标和实际坐标。

# 7. 备注
- 右侧的「备注」框属于当前选中的截图，可以写说明、零件号、待办事项等。
- 勾选「复制 / 导出时包含备注」后，复制、保存或导出 PDF 时，备注会附在图片下方。

# 8. 保存和导出
- 「保存 ▾」→ 当前视图、选中截图（PNG、JPG、BMP 或 PDF），全部截图保存为 PNG，全部截图或拼图导出为多页 PDF。
- 「选项」→「自动保存 PNG 到文件夹」，可自选文件夹。
- 关闭软件时，如果有截图还没保存成文件，会弹出对话框让你选择：保存内容（当前视图 / 仅未保存的截图 / 全部截图 / 全部合并为一个 PDF）、格式（PNG、JPG、BMP、TIFF、WEBP、PDF）、保存路径（可点「浏览…」）和文件名。「不保存直接关闭」仍会保留历史记录；「取消」则不关闭软件。取消勾选「每次关闭软件时都询问」（或在「选项」中关闭）即可不再询问。
- 历史记录（图片、标注、备注）在关闭软件后会保留。「选项」→「清空历史记录」可删除。

# 9. 缩放和浏览
- Ctrl+滚轮缩放，滚轮滚动，按住中键拖动平移。
- 右下角的「适应」/「100%」/「−」/「+」。Ctrl+0 适应窗口，Ctrl+1 实际大小。

# 10. 语言
- 「选项」→「语言 / Language」：English、Français、中文（重启软件后生效）。

# 11. 扩展功能（可选，默认关闭）
在「选项」→「扩展功能」里可以单独打开或关闭下面每一项。关闭时，界面上不会多出任何按钮。
- 贴图置顶：点「📌 贴图」（或 Ctrl+P，或在历史记录卡片上右键），截图会钉在所有窗口的最上层。拖动移动，滚轮缩放，Ctrl+滚轮调透明度，双击或 Esc 关闭，右键可复制 / 保存 / 关闭所有贴图。
- 文字识别 (OCR)：点「🔤 识字」（或 Ctrl+T），用 Windows 10/11 自带的 OCR 引擎识别截图里的文字，完全离线。识别结果会自动复制到剪贴板，也可以在窗口里修改。可在窗口里选择语言；Windows 只提供已安装「光学字符识别」的语言（设置 → 时间和语言 → 语言和区域）。
- 长截图 / 滚动截图：截图模式里会多出「长截图」。在需要滚动的窗口区域拖出一个矩形，软件会自动向下滚动，并把每一屏拼接成一张长图。点「暂停」可改为自己慢慢滚动，点「完成」或按 Esc 结束。滚到页面底部时会自动结束。如果这个窗口不接受自动滚动，会自动改为手动滚动。
- 录屏 (GIF / MP4)：点「⏺ 录屏」（或 Ctrl+R），录制一个矩形区域（「全屏」模式下录制整个屏幕）。按 Esc 或「停止」结束，然后选择保存位置。「选项」→「扩展功能」→「录屏格式」：MP4 视频（默认：文件小，不限时长，可以同时录麦克风和/或系统声音，在同一个菜单里打开）或 GIF 动图（没有声音，最长 60 秒）。.exe 已自带 MP4 和录音功能；从源码运行时请用 pip install imageio-ffmpeg pyaudiowpatch 安装。帧率（每秒 5、10 或 15 帧）在「选项」→「扩展功能」里设置。
> 控制条和区域外的彩色边框不会被截进图片或录进视频。

# 12. 主题
- 点顶栏的「🎨 主题」可以更换界面配色、每个功能的图标和装饰图（重启软件后生效）。
- 主题还可以给复制和导出的截图加上边框，用「复制和导出时加上主题边框」开关。自动保存的 PNG 不加边框。
- 🎲「随机换一个主题」会从已安装的主题中随机挑一个。勾选「每次启动时随机使用一个主题」后，每次打开软件都会换一个主题。
- 「获取在线主题」会到 GitHub 查找新主题。只有点这个按钮时软件才会联网。
- 「导入 .zip…」安装别人发给你的主题；「以此为模板自己做…」会把主题复制到你的主题文件夹，方便你改图片和配色。
> 如何制作主题：见项目 GitHub 页面上的 docs/THEMES.md（点「如何制作主题」按钮即可打开）。

# 13. 画图工具（类似 Windows“画图”）
- 橡皮擦 (X)：在标注上拖动即可擦掉。画笔、荧光笔和填充只擦掉橡皮擦经过的部分；其他标注碰到就整个删除。截图本身永远不会被擦掉。橡皮擦大小由「线宽」决定。
- 油漆桶 (F)：点一个区域，用当前颜色填充点击处周围颜色相同的区域（按你看到的画面，包括标注）。填充仍是一个标注：选中后可以改颜色、移动或删除。
- 取色器 (I)：在图片上点一下就取到那里的颜色，然后自动回到之前的工具。
- 右侧面板的「图像」区（选择工具且没有选中标注时显示），右键菜单里也有：向左 / 向右旋转、水平 / 垂直翻转、裁剪（拖出要保留的部分）、调整大小…（按百分比）。标注会跟着图片一起变。Ctrl+Z 可撤销。
- 新建空白画布…（Ctrl+Shift+N）：在历史记录里新建一张空白图，可选尺寸和背景色，像在“画图”里一样画画。
> 窗口太矮时，左侧工具栏会自动变成两列。

# 14. 同位置重截和对比
- 「⟳ 同位置」（Ctrl+Shift+R，或在 Windows 任意位置按 Ctrl+Alt+R）会按选中截图的位置，重新截取屏幕上完全相同的区域，适合做「改动前 / 改动后」对比或观察变化。在历史记录卡片上右键 →「按同位置重新截图」，可以对任意一张截图使用。
- 同位置截图后会自动打开「对比」窗口：拖动中间的分割线查看之前或之后的图片，也可以选「并排」。两张图始终保持相同的缩放和位置（滚轮缩放，中键 / 右键拖动平移，双击适应窗口）。
- 「高亮不同之处」会把每个变化的像素染成红色，并用红框圈出每一处不同。「容差」可忽略细微的颜色变化。「在「之后」图上标出不同」会把红框作为普通（可编辑的）矩形标注加到较新的截图上；「复制对比图」会把两张图并排复制到剪贴板。
- 「◧ 对比」（Ctrl+Shift+C）把选中的截图和它重截的原图（或上一张）对比；也可以在「之前 / 之后」列表里任选两张。尺寸不同的截图按左上角对齐。
- 拼图同步缩放：在任意格子上 Ctrl+滚轮，所有格子会一起放大到同一位置；滚轮 / 中键拖动一起平移；Ctrl+0 或「适应」恢复。
""",
}


def guide_text():
    return GUIDE.get(LANG[0], GUIDE["en"])
