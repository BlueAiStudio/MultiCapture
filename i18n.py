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
    "Nothing selected  ·  click an annotation": ("Aucune sélection  ·  cliquez une annotation", "未选中  ·  点击一个标注"),
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
    "Select / move / resize  (V)": ("Sélection / déplacer / redimensionner  (V)", "选择 / 移动 / 调整大小  (V)"),
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
    "SHORTCUTS": (
        "Ctrl+Alt+S   capture depuis n'importe où (global)\n"
        "Ctrl+N         nouvelle capture\n"
        "Ctrl+C         copier la vue actuelle\n"
        "Ctrl+S         enregistrer la vue   ·   Ctrl+Maj+S  tout enregistrer\n"
        "Ctrl+Z / Y    annuler / rétablir\n"
        "Ctrl+D         dupliquer l'annotation\n"
        "Suppr           supprimer l'annotation (ou la capture)\n"
        "Ctrl+Maj+Suppr  supprimer toutes les captures\n"
        "Flèches        déplacer l'annotation (Maj = 10 px)\n"
        "Ctrl+molette  zoom   ·   Ctrl+0 ajuster   ·   Ctrl+1 100 %\n"
        "Clic molette  déplacer la vue\n"
        "1 – 5            Unique / 2×2 / 3×3 / 4×4 / Tout\n"
        "F1                guide d'utilisation\n\n"
        "Outils :  V sélection · P stylo · H surligneur · L ligne · A flèche\n"
        "R rectangle · E ellipse · T texte · C bulle · N numéro\n"
        "S tampon · B flou · D distance · M périmètre · G surface\n"
        "Q angle · K échelle\n"
        "X gomme · F remplissage · I pipette   ·   Ctrl+Maj+N page blanche",
        "Ctrl+Alt+S   在任意位置截图（全局）\n"
        "Ctrl+N         新建截图\n"
        "Ctrl+C         复制当前视图\n"
        "Ctrl+S         保存当前视图   ·   Ctrl+Shift+S  全部保存\n"
        "Ctrl+Z / Y    撤销 / 重做\n"
        "Ctrl+D         复制标注\n"
        "Delete          删除标注（或截图）\n"
        "Ctrl+Shift+Delete  删除全部截图\n"
        "方向键         微移标注（Shift = 10 px）\n"
        "Ctrl+滚轮     缩放   ·   Ctrl+0 适应   ·   Ctrl+1 100%\n"
        "中键拖动      平移\n"
        "1 – 5            单张 / 2×2 / 3×3 / 4×4 / 全部\n"
        "F1                使用说明\n\n"
        "工具：V 选择 · P 画笔 · H 荧光笔 · L 直线 · A 箭头\n"
        "R 矩形 · E 椭圆 · T 文字 · C 标注框 · N 编号\n"
        "S 符号 · B 马赛克 · D 距离 · M 周长 · G 面积\n"
        "Q 角度 · K 校准比例\n"
        "X 橡皮擦 · F 油漆桶 · I 取色器   ·   Ctrl+Shift+N 空白画布"),
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
    # ---------------------------------------------------------------- optional extra features
    "Extra features": ("Fonctions supplémentaires", "扩展功能"),
    "Pin to screen": ("Épingler à l'écran", "贴图置顶"),
    "Text recognition (OCR)": ("Reconnaissance de texte (OCR)", "文字识别 (OCR)"),
    "Scrolling capture": ("Capture défilante", "长截图 / 滚动截图"),
    "Screen recording (GIF)": ("Enregistrement d'écran (GIF)", "录屏 (GIF)"),
    "Scrolling": ("Défilante", "长截图"),
    "Pin": ("Épingler", "贴图"),
    "Text": ("Texte", "识字"),
    "Record": ("Filmer", "录屏"),
    "Pin the screenshot above all windows  (Ctrl+P)\nDrag to move · wheel to zoom · Ctrl+wheel opacity · double-click or Esc to close":
        ("Épingler la capture au-dessus de toutes les fenêtres  (Ctrl+P)\nGlisser = déplacer · molette = zoom · Ctrl+molette = opacité · double-clic ou Échap = fermer",
         "把截图钉在所有窗口最上层  (Ctrl+P)\n拖动移动 · 滚轮缩放 · Ctrl+滚轮调透明度 · 双击或 Esc 关闭"),
    "Extract the text of the screenshot  (Ctrl+T)\nWindows OCR, works offline":
        ("Extraire le texte de la capture  (Ctrl+T)\nOCR de Windows, hors ligne", "识别截图中的文字  (Ctrl+T)\n使用 Windows 自带 OCR，离线可用"),
    "Record part of the screen as an animated GIF  (Ctrl+R)\nEsc or Stop to finish":
        ("Filmer une partie de l'écran en GIF animé  (Ctrl+R)\nÉchap ou Arrêter pour terminer", "把屏幕的一部分录成 GIF 动图  (Ctrl+R)\n按 Esc 或「停止」结束"),
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
    "Saving GIF… {p}%": ("Enregistrement du GIF… {p} %", "正在保存 GIF… {p}%"),
    "GIF saved: {p}": ("GIF enregistré : {p}", "GIF 已保存：{p}"),
    "✓ GIF saved": ("✓ GIF enregistré", "✓ GIF 已保存"),
    "  ·  stopped at the length limit": ("  ·  arrêté à la durée maximale", "  ·  已达到最长时长，自动停止"),
    "Recording frame rate": ("Images par seconde (vidéo)", "录屏帧率"),
    "{n} frames / s": ("{n} images / s", "{n} 帧/秒"),
    "Ctrl+P         pin screenshot to the screen": ("Ctrl+P         épingler la capture à l'écran", "Ctrl+P         贴图置顶"),
    "Ctrl+T         extract text (OCR)": ("Ctrl+T         extraire le texte (OCR)", "Ctrl+T         识别文字 (OCR)"),
    "Ctrl+R         record screen to GIF  ·  Esc stop": ("Ctrl+R         filmer l'écran en GIF  ·  Échap = arrêter",
                                                         "Ctrl+R         录屏为 GIF  ·  Esc 停止"),
}

SHORTCUTS_EN = (
    "Ctrl+Alt+S   capture from anywhere (global)\n"
    "Ctrl+N         new capture\n"
    "Ctrl+C         copy current view\n"
    "Ctrl+S         save current view    ·   Ctrl+Shift+S  save all\n"
    "Ctrl+Z / Y    undo / redo\n"
    "Ctrl+D         duplicate annotation\n"
    "Delete          delete annotation (or screenshot)\n"
    "Ctrl+Shift+Delete  delete all screenshots\n"
    "Arrows         nudge annotation (Shift = 10 px)\n"
    "Ctrl+wheel    zoom   ·   Ctrl+0 fit   ·   Ctrl+1 100%\n"
    "Middle-drag   pan\n"
    "1 – 5            Single / 2×2 / 3×3 / 4×4 / All\n"
    "F1                user guide\n\n"
    "Tools:  V select · P pen · H highlighter · L line · A arrow\n"
    "R rectangle · E ellipse · T text · C callout · N number\n"
    "S stamp · B blur · D distance · M perimeter · G area\n"
    "Q angle · K calibrate scale\n"
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
> Every annotation stays editable: choose Select (V), click an object, then drag it, pull its white handles, change its colour / size in the right panel, or press Delete. Ctrl+Z / Ctrl+Y = undo / redo, Ctrl+D = duplicate, arrow keys = nudge.

# 5. Text boxes and callouts (like Word)
- Text (T): click where the text should go and type. Enter = new line; click outside, Esc or Ctrl+Enter = finish.
- Callout (C): press on the point to highlight, drag to where the text box goes, release and type – a leader line is drawn automatically.
- Formatting in the TEXT section: font, size, Bold, Italic, Underline, alignment, background colour, border, text colour (COLOUR palette).
- Double-click a text with the Select tool to edit it again; drag it to move it.
- Move handle ✥: a blue round handle with a cross of arrows appears at the top-left corner of the text box while you type and whenever the text (or any annotation) is selected. Drag it to move the object – it works with every tool. The cursor turns into a four-way arrow over anything that can be moved.

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
- Scrolling capture: adds "Scrolling" to the capture mode list. Drag a rectangle over the part of the window that scrolls. It then scrolls down by itself and joins the frames into one long image. Click Pause to scroll by hand instead (slowly), and Done or Esc to finish. It stops by itself at the end of the page.
- Screen recording (GIF): the ⏺ Record button (or Ctrl+R) records a rectangle (or the full screen in Full screen mode) to an animated GIF. Esc or Stop ends it, then you choose where to save. The frame rate (5, 10 or 15 per second) is in Options → Extra features. A recording stops by itself after 60 s.
> The control bar and the coloured frame around the region are not part of the capture or the recording.

# 12. Themes
- Click 🎨 Themes to change the colours, the icon of each function and the decorations (restart of the app).
- A theme can also put a frame around the screenshots you copy and export. Turn it on or off with "Add the theme frame to copies and exports". Auto-saved PNG files never get a frame.
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
> Toutes les annotations restent modifiables : outil Sélection (V), cliquez un objet puis déplacez-le, tirez ses poignées blanches, changez sa couleur / taille à droite, ou appuyez sur Suppr. Ctrl+Z / Ctrl+Y = annuler / rétablir, Ctrl+D = dupliquer, flèches = déplacement fin.

# 5. Zones de texte et bulles (comme Word)
- Texte (T) : cliquez à l'endroit voulu et tapez. Entrée = nouvelle ligne ; clic à l'extérieur, Échap ou Ctrl+Entrée = terminer.
- Bulle (C) : appuyez sur le point à signaler, glissez jusqu'à l'emplacement du texte, relâchez et tapez – la ligne de rappel est tracée automatiquement.
- Mise en forme dans la section TEXTE : police, taille, Gras, Italique, Souligné, alignement, couleur de fond, bordure, couleur du texte (palette COULEUR).
- Double-cliquez sur un texte avec l'outil Sélection pour le modifier ; glissez-le pour le déplacer.
- Poignée de déplacement ✥ : une poignée ronde bleue avec une croix de flèches apparaît au coin supérieur gauche de la zone de texte pendant la saisie et dès que le texte (ou toute annotation) est sélectionné. Faites-la glisser pour déplacer l'objet – fonctionne avec tous les outils. Le curseur devient une flèche à quatre directions sur tout ce qui peut être déplacé.

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
- Capture défilante : ajoute « Défilante » aux modes de capture. Tracez un rectangle sur la partie de la fenêtre qui défile. La page défile ensuite toute seule et les images sont assemblées en une longue capture. Cliquez Pause pour faire défiler à la main (lentement), puis Terminé ou Échap. Elle s'arrête seule en bas de la page.
- Enregistrement d'écran (GIF) : le bouton ⏺ Filmer (ou Ctrl+R) enregistre un rectangle (ou tout l'écran en mode Plein écran) en GIF animé. Échap ou Arrêter pour terminer, puis choisissez où l'enregistrer. La cadence (5, 10 ou 15 images/s) se règle dans Options → Fonctions supplémentaires. L'enregistrement s'arrête seul après 60 s.
> La barre de commande et le cadre coloré autour de la zone ne figurent pas dans la capture ni dans la vidéo.

# 12. Thèmes
- Cliquez sur 🎨 Thèmes pour changer les couleurs, l'icône de chaque fonction et les décorations (redémarrage de l'application).
- Un thème peut aussi encadrer les captures que vous copiez et exportez. Activez ou désactivez « Ajouter le cadre du thème aux copies et exports ». Les PNG enregistrés automatiquement n'ont jamais de cadre.
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
> 所有标注都可以随时修改：选择「选择」工具（V），点击对象后可拖动、拉动白色控制点调整大小、在右侧修改颜色 / 大小，或按 Delete 删除。Ctrl+Z / Ctrl+Y 撤销 / 重做，Ctrl+D 复制，方向键微移。

# 5. 文本框和标注框（类似 Word）
- 文字（T）：在需要的位置点击并输入。回车换行；点击外部、按 Esc 或 Ctrl+回车 完成。
- 标注框（C）：在要指出的位置按下，拖到文字框要放的位置，松开后输入文字，引线会自动画出。
- 「文字」区域可设置格式：字体、字号、粗体、斜体、下划线、对齐方式、背景色、边框；文字颜色在「颜色」调色板中选择。
- 用「选择」工具双击文字可再次编辑；拖动即可移动位置。
- 移动手柄 ✥：输入文字时，以及选中文字（或任何标注）后，文本框左上角会出现一个带十字箭头的蓝色圆形手柄。拖动它即可移动对象，任何工具下都可以用。鼠标移到可移动的对象上时，光标会变成四向箭头。

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
- 长截图 / 滚动截图：截图模式里会多出「长截图」。在需要滚动的窗口区域拖出一个矩形，软件会自动向下滚动，并把每一屏拼接成一张长图。点「暂停」可改为自己慢慢滚动，点「完成」或按 Esc 结束。滚到页面底部时会自动结束。
- 录屏 (GIF)：点「⏺ 录屏」（或 Ctrl+R），录制一个矩形区域（「全屏」模式下录制整个屏幕）为 GIF 动图。按 Esc 或「停止」结束，然后选择保存位置。帧率（每秒 5、10 或 15 帧）在「选项」→「扩展功能」里设置。录制 60 秒后会自动停止。
> 控制条和区域外的彩色边框不会被截进图片或录进视频。

# 12. 主题
- 点顶栏的「🎨 主题」可以更换界面配色、每个功能的图标和装饰图（重启软件后生效）。
- 主题还可以给复制和导出的截图加上边框，用「复制和导出时加上主题边框」开关。自动保存的 PNG 不加边框。
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
""",
}


def guide_text():
    return GUIDE.get(LANG[0], GUIDE["en"])
