# MultiCapture 主题制作说明

[中文](#中文) · [English](#english)

---

## 中文

主题可以改变 MultiCapture 的样子：

- **界面配色**：按钮、面板、文字、画布等颜色；
- **功能图标**：每个功能可以换成自己的图片，比如鲜花主题里每个按钮都是一朵花；
- **装饰图**：顶栏右侧、画布角落的图片，比如夜晚主题里的月亮和星星；
- **截图边框**：复制和导出截图时，在外面套一个边框，四角还可以贴小图。

做主题**不需要写代码**。一个主题就是一个文件夹，里面放一个 `theme.json` 文字文件和几张 PNG 图片。

### 最快的做法

1. 打开软件，点顶栏的「🎨 主题」。
2. 选一个你喜欢的主题（比如「鲜花」），点「以此为模板自己做…」，输入名字。
3. 软件会把它复制到你的主题文件夹，并自动打开这个文件夹。
4. 用任意画图软件替换里面的图片，用记事本修改 `theme.json` 里的颜色和文字。
5. 回到「主题」窗口，选中你的主题，点「使用此主题」，重启软件后生效。

主题文件夹在 `%APPDATA%\MultiCapture\themes\`（主题窗口里的「打开主题文件夹」可以直接打开）。

### 文件夹结构

```
my-theme/                 文件夹名就是主题 id：只能用小写英文字母、数字、- 和 _
├── theme.json            必须有：名称、作者、版本、配色、装饰、边框
├── preview.png           可选：主题窗口里的预览图（520 × 330）。没有的话软件会自动画一张
├── icons/                可选：功能图标，文件名见下表，缺的继续用默认图标
│   ├── pen.png
│   └── capture.png
├── header.png            可选：顶栏装饰图
├── canvas.png            可选：画布装饰图
├── frame.png             可选：图片边框（九宫格）
└── deco/rose.png         可选：边框上的贴纸，文件夹和文件名随意
```

只允许 `.json`、`.png`、`.jpg`、`.gif`、`.webp`、`.bmp`、`.txt`、`.md` 文件。单个文件最大 8 MB，单张图片最大 4096 × 4096。

### theme.json

一个最小的主题只要一行：

```json
{ "name": "我的主题" }
```

完整的例子见 [themes/flowers/theme.json](../themes/flowers/theme.json) 和 [themes/night/theme.json](../themes/night/theme.json)。

| 字段 | 说明 |
|---|---|
| `format` | 固定写 `1` |
| `name` | 主题名。可以写一个名字，也可以分语言写：`{"zh": "鲜花", "en": "Flowers", "fr": "Fleurs"}` |
| `author` | 作者 |
| `version` | 版本号，比如 `"1.0"`。**更新主题时要改大**，用户那边才会显示「可更新」 |
| `description` | 一句话介绍，写法和 `name` 一样 |
| `colors` | 界面配色，见下表。没写的颜色保持默认 |
| `icons` | 可选。图标不放在 `icons/<名称>.png` 时，用它指定路径：`{"pen": "pics/my-pen.png"}` |
| `decorations` | 装饰图，见下文 |
| `frame` | 截图边框，见下文 |

#### 颜色（colors）

颜色写成 `#RRGGBB`，比如 `"#D94F7C"`。

| 名称 | 用在哪里 | 默认 |
|---|---|---|
| `accent` | 主按钮、选中框、链接 | `#2563EB` |
| `accent_dark` | 鼠标放在主按钮上时 | `#1D4ED8` |
| `accent_light` | 选中的工具、选中的文字 | `#E8EFFE` |
| `bg` | 窗口背景 | `#F3F4F6` |
| `panel` | 顶栏、左右面板、对话框 | `#FFFFFF` |
| `border` | 分隔线 | `#E5E7EB` |
| `text` | 文字 | `#111827` |
| `muted` | 次要文字 | `#6B7280` |
| `canvas` | 截图后面的画布 | `#E7EAEE` |
| `button` | 小按钮 | `#F3F4F6` |
| `button_hover` | 鼠标放在小按钮上时 | `#E5E7EB` |
| `hover` | 鼠标放在顶栏按钮上时 | `#EEF2F7` |
| `icon` | 默认工具图标的颜色（深色主题请改成浅色） | `#374151` |
| `icon_accent` | 默认工具图标的第二种颜色 | `#2563EB` |
| `shadow` | 画布上截图的阴影 | `#C8CDD5` |
| `notes_bg` | 备注框 | `#FBFBFC` |
| `field` | 下拉框、数字框 | `#FFFFFF` |
| `tooltip_bg` / `tooltip_text` | 鼠标提示的背景 / 文字 | `#111827` / `#FFFFFF` |
| `success` | 「✓ 已复制」提示 | `#15803D` |

#### 功能图标（icons/）

正方形、透明背景的 PNG，建议 96 × 96 像素或更大，软件会自动缩小。

| 文件名 | 功能 | 文件名 | 功能 |
|---|---|---|---|
| `select.png` | 选择 | `marker.png` | 编号 |
| `pen.png` | 画笔 | `stamp.png` | 符号 |
| `highlight.png` | 荧光笔 | `mosaic.png` | 马赛克 |
| `line.png` | 直线 | `dist.png` | 测距离 |
| `arrow.png` | 箭头 | `perim.png` | 测周长 |
| `rect.png` | 矩形 | `area.png` | 测面积 |
| `ellipse.png` | 椭圆 | `angle.png` | 测角度 |
| `text.png` | 文本框 | `calib.png` | 校准比例 |
| `callout.png` | 标注框 | | |

顶栏按钮：`capture.png`（新建截图）、`copy.png`（复制）、`save.png`（保存）、`delete.png`（删除）、`options.png`（选项）、`themes.png`（主题）、`help.png`（帮助）。

> 如果图标只是一朵花、看不出是什么功能也没关系：鼠标放上去会显示功能名称。

#### 装饰图（decorations）

```json
"decorations": {
  "header": { "image": "header.png" },
  "canvas": { "image": "canvas.png", "anchor": "ne" }
}
```

- `header`：放在顶栏最右边，高度会缩放到顶栏高度（可用 `"height": 44` 调整）。透明背景的横长图最好看，比如 320 × 88。窗口太窄时会被挤掉。
- `canvas`：放在截图后面的画布上。`anchor` 决定位置：`nw` 左上、`n` 上、`ne` 右上、`w` 左、`center` 中间、`e` 右、`sw` 左下、`s` 下、`se` 右下，或者 `tile` 平铺整个画布。`margin` 是离边缘的距离（像素）。图片最多占画布宽高的 45%，不会挡住太多截图。

#### 截图边框（frame）

打开「复制和导出时加上主题边框」后，复制到剪贴板、保存、导出 PNG / PDF 的截图都会套上边框。屏幕上编辑时看到的是原图，自动保存的 PNG 也不加边框。

边框有两种做法，可以混用：

**做法一：样式边框**（只写数字和颜色，不用画图）

```json
"frame": {
  "margin": 34,
  "canvas": "#0B1226",
  "padding": 14,
  "background": "#16213F",
  "radius": 16,
  "border": { "color": "#33427A", "width": 2 },
  "shadow": { "color": "#00000099", "blur": 22, "offset": [0, 8] },
  "titlebar": { "height": 34, "color": "#F3F4F6", "dots": true, "text": "{title}" },
  "caption": { "height": 46, "text": "{date}  ·  {time}", "color": "#C9D2F0", "size": 18 }
}
```

| 字段 | 说明 |
|---|---|
| `margin` | 边框外面留白的宽度 |
| `canvas` | 留白的颜色 |
| `padding` | 截图和卡片边缘之间的距离 |
| `background` | 卡片颜色 |
| `radius` | 圆角大小 |
| `border` | 卡片外框：`color` 颜色，`width` 粗细 |
| `shadow` | 阴影：`color`（可带透明度，如 `#00000099`），`blur` 模糊程度，`offset` 偏移 `[横, 竖]` |
| `titlebar` | 卡片顶部的标题栏：`height` 高度，`color` 颜色，`dots` 是否画三个小圆点，`text` 文字，`text_color` 文字颜色 |
| `caption` | 截图下方的文字：`height` 高度，`text` 文字，`color` 颜色，`size` 字号，`bold` 粗体，`align` 对齐（`left` / `center` / `right`） |

`text` 里可以用这些占位符：`{date}` 日期、`{time}` 时间、`{num}` 截图编号、`{title}` 标题（如「MultiCapture · #3」）、`{count}` 拼图里的截图数量、`{theme}` 主题名。

**做法二：图片边框（九宫格）**

画一张边框图 `frame.png`，中间留透明。软件把它切成九块：四个角保持原样，四条边拉伸或重复，中间放截图。

```json
"frame": {
  "image": "frame.png",
  "slice": [36, 36, 36, 36],
  "edges": "tile",
  "margin": 56,
  "canvas": "#FFF5F8"
}
```

| 字段 | 说明 |
|---|---|
| `image` | 边框图片 |
| `slice` | 四条切线离图片 左、上、右、下 边缘的像素数，也就是边框有多粗 |
| `inset` | 可选。截图放在离外边缘多远的地方，默认等于 `slice` |
| `edges` | `stretch` 拉伸四条边（默认），`tile` 重复花纹（花纹边框请用这个） |

**贴纸（ornaments）**：两种做法都可以在卡片的角上和边上贴小图，比如玫瑰、月亮、星星。

```json
"ornaments": [
  { "image": "deco/rose.png", "anchor": "nw", "size": 150, "offset": [-14, -14] },
  { "image": "deco/moon.png", "anchor": "ne", "size": 130, "offset": [18, -18], "layer": "back" }
]
```

- `anchor`：贴纸的中心对准卡片的哪个点（`nw` 左上角、`n` 上边中点、`ne` 右上角 …… `center` 中心）；
- `size`：贴纸宽度；`offset`：再往 `[右, 下]` 移动多少（负数是往左 / 往上）；
- `layer`：默认贴在最上面；写 `"back"` 则放在卡片后面，只从边缘露出来。

> 贴纸太大会挡住截图内容。可以加大 `margin` 并用 `offset` 把贴纸往外移。

**大小会跟着截图缩放**：上面所有像素值都是按 1200 像素宽的截图来写的，截图更大或更小时会按比例缩放（0.5 到 2.5 倍）。想固定不缩放，写 `"scale": 1`；想换参考宽度，写 `"ref_size": 1600`。

### 检查主题

装了 Python 的话，可以运行下面的命令检查主题有没有写错（图片找不到、颜色格式不对、拼错字段名等）：

```
python tools/check_themes.py 你的主题文件夹路径
```

不运行也没关系：软件读不了的主题不会出现在列表里，主题窗口底部会提示哪个文件夹有问题。

### 分享主题

在「主题」窗口选中主题，点「导出为 .zip…」，把 zip 文件发给别人。对方点「导入 .zip…」就能装上。

### 发布到 GitHub（项目作者用）

用户点「获取在线主题」时，软件会读取 GitHub 仓库 `themes/` 文件夹里的主题。所以发布新主题只需要：

1. 打开仓库的 [themes](../themes) 文件夹，点 **Add file → Upload files**；
2. 把整个主题文件夹拖进去（网页会保留文件夹结构），提交到 `main` 分支；
3. 更新已有主题时，记得把 `theme.json` 里的 `version` 改大。

GitHub 的自动构建会运行 `tools/check_themes.py`，主题有错时构建会变红。`themes/` 里的主题也会在下一次发布时打包进 exe，成为内置主题。

### 安全

主题里只有图片和 `theme.json` 文字，软件不会运行主题里的任何程序。导入和下载时会拒绝其他类型的文件、超大文件和指向主题文件夹外的路径。

---

## English

A theme changes the colours, the icon of each function and the decorations of MultiCapture, and can add a
frame to the screenshots you copy and export. It is a folder with a `theme.json` file and some PNG images.
No code is needed and the app never runs code from a theme.

**Quick start:** click 🎨 **Themes**, pick a theme, click **Make my own from this…**, then edit the pictures and
`theme.json` in the folder that opens (`%APPDATA%\MultiCapture\themes\<id>`). Choose it in the Themes window and
restart.

**Files:** `theme.json` (required), `preview.png` (520 × 330, optional), `icons/<key>.png` (one per function,
square, transparent, 96 px or larger; missing icons keep the default), and any images referenced from
`theme.json`. The folder name is the theme id (`a-z`, `0-9`, `-`, `_`). Allowed file types: json, png, jpg, gif,
webp, bmp, txt, md; at most 8 MB per file and 4096 × 4096 per image.

**theme.json keys:** `format` (1), `name`, `description` (a string or `{"en", "zh", "fr"}`), `author`, `version`
(raise it when you update a theme so users are offered the update), `colors`, `icons`, `decorations`, `frame`.
The colour names, icon names and every frame option are listed in the tables of the Chinese section above.

- **Icon keys:** tools `select pen highlight line arrow rect ellipse text callout marker stamp mosaic dist perim
  area angle calib`; header `capture copy save delete options themes help`.
- **Decorations:** `header` (right end of the header bar) and `canvas` (behind the screenshot; `anchor` is one of
  `nw n ne w center e sw s se tile`, plus `margin`).
- **Frame, style:** `margin`, `canvas`, `padding`, `background`, `radius`, `border {color, width}`,
  `shadow {color, blur, offset}`, `titlebar {height, color, dots, text, text_color}`,
  `caption {height, text, color, size, bold, align}`. Texts can use `{date} {time} {num} {title} {count} {theme}`.
- **Frame, 9-slice image:** `image`, `slice [l, t, r, b]`, optional `inset`, `edges` (`stretch` or `tile`).
- **Ornaments:** `[{image, anchor, size, offset [x, y], layer: "back"?}]`, stickers centred on a point of the card.
- Pixel values are written for a 1200 px screenshot and scale with the screenshot (0.5× to 2.5×). Use
  `"scale": 1` to turn scaling off, or `"ref_size"` to change the reference width.

**Check a theme:** `python tools/check_themes.py path/to/theme`. **Share:** Themes → Export .zip… / Import .zip….

**Publish (project owner):** upload the theme folder into [`themes/`](../themes) on the `main` branch (GitHub web:
Add file → Upload files, drag the folder). "Get online themes" in the app lists it right away; CI checks it; the
next release bundles it into the exe.
