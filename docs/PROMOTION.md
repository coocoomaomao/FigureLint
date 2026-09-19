# FigureLint Promotion Kit

This file contains ready-to-use launch copy for FigureLint v0.1.0.

> Core positioning: **ESLint for academic figures.**
>
> FigureLint helps researchers catch reproducible technical figure problems before submission with one command.

## Links

- GitHub: https://github.com/coocoomaomao/FigureLint
- PyPI: https://pypi.org/project/figurelint/
- Release: https://github.com/coocoomaomao/FigureLint/releases/tag/v0.1.0

## One-line pitches

### English

**FigureLint is an open-source linter for academic figures that checks PNG/JPEG, SVG, and PDF files before submission.**

Shorter:

**Catch publication-quality figure problems before submission.**

Developer-oriented:

**ESLint for academic figures — now with a source-backed Nature preset and GitHub Actions support.**

### 中文

**FigureLint 是一个开源的“论文图片体检器”，投稿前自动检查 DPI、字号、线宽、字体嵌入等技术问题。**

更短版：

**投稿前，先给论文图跑一次 FigureLint。**

## 小红书首发

### 标题候选

1. 我做了一个“论文图片体检器”，投稿前一行命令自查
2. 论文图看起来很清楚，为什么投稿还是会被打回来？
3. 投稿 Nature 前，我让黑猫先帮我检查一遍论文图 🐈‍⬛
4. 免费开源｜自动检查论文图 DPI、字号、线宽和 PDF
5. 做了个科研小工具：ESLint for academic figures

### 推荐正文

最近做论文图的时候，我一直觉得有件事很麻烦：

图片在电脑上看着明明很清楚，但真正投稿时，还要重新检查 DPI、字号、线宽、字体有没有嵌入、PDF 里有没有低分辨率图片……

所以我干脆做了一个开源小工具：**FigureLint 🐈‍⬛**

它有点像代码里的 ESLint，只不过检查的不是代码，而是论文 Figure。

现在支持：

- PNG / JPEG：DPI、尺寸、透明通道等
- SVG：字号、线宽、可编辑文字、字体等
- PDF：字体嵌入、页面尺寸、内部栅格图有效 DPI 等
- 整个 figures 文件夹批量检查
- GitHub Actions 自动标注
- 一个有官方来源记录的 Nature preset

安装只需要：

~~~bash
pip install figurelint
~~~

然后：

~~~bash
figurelint check Figure1.svg
~~~

或者：

~~~bash
figurelint check figures/ --preset nature
~~~

这里特别说明一下：**Nature preset 不是“保证投稿合规”的认证工具。** FigureLint 只自动检查官方指南中能够可靠、确定性检测的那部分规则，并把官方要求和工具自己的建议分开。

项目完全开源，目前是 v0.1.0 Alpha。很想找第一批真正做论文图的人来试。

如果你平时会做 SCI / 数学建模 / 科研绘图，欢迎拿自己的 Figure 跑一下，遇到误报、漏报或者希望支持的期刊规范，都可以直接提 Issue。

GitHub：coocoomaomao/FigureLint  
PyPI：figurelint

### 建议标签

#科研工具 #论文写作 #SCI论文 #学术绘图 #科研绘图 #Python #开源项目 #研究生 #Nature #数据可视化

## 知乎 / 技术社区

### 标题

**我做了一个“ESLint for academic figures”：投稿前自动检查论文图**

### 开头

写论文时，很多 Figure 问题不是“好不好看”，而是非常具体的技术问题：DPI 是否足够、SVG 字号和线宽是否过小、PDF 是否嵌入字体、内部栅格图的有效分辨率是多少。

这些问题往往散落在期刊投稿指南、绘图软件导出设置和人工检查流程里。

FigureLint 想做的事情很简单：把其中能够确定性验证的部分，变成一个可重复执行的命令。

~~~bash
pip install figurelint
figurelint check figures/
~~~

文章后续建议展开：

1. 为什么“屏幕上清楚”不等于“投稿技术上没问题”
2. FigureLint 的 PNG / SVG / PDF 检查方式
3. 为什么 publisher preset 必须记录来源
4. Nature preset 如何区分官方规则和 FigureLint 建议
5. 为什么工具宁可报告 unknown，也不应该乱猜
6. GitHub Actions 如何把 Figure QA 放进 CI
7. v0.1.0 的局限和 Roadmap

结尾 CTA：

> 如果你有真实论文 Figure，欢迎拿来测试。最希望收到的不是 Star，而是误报、漏报和真实投稿场景。

## Show HN

### Title

**Show HN: FigureLint – ESLint for academic figures**

### Body

I built FigureLint because figure QA before submission is surprisingly fragmented.

A plot can look perfectly fine on screen while still having technical problems: low effective DPI, missing image metadata, tiny SVG labels, thin strokes, unembedded PDF fonts, or raster images placed at a much lower effective resolution than expected.

FigureLint turns the checks that can be verified deterministically into a CLI:

~~~bash
pip install figurelint
figurelint check figures/
~~~

It currently inspects PNG/JPEG, SVG, and PDF files, supports recursive folder checks, and can emit native GitHub Actions annotations.

There is also a `nature` preset. I was careful not to turn common internet advice into fake publisher rules: the preset stores source provenance and only labels thresholds as Nature-backed when they come from official guidance. If a property cannot be resolved reliably, the tool generally reports it as unknown/informational rather than guessing.

Example:

~~~bash
figurelint check Figure1.svg --preset nature
~~~

The project is MIT licensed and at v0.1.0 alpha. I'd especially appreciate feedback from researchers who have real-world figure export/submission edge cases.

GitHub: https://github.com/coocoomaomao/FigureLint  
PyPI: https://pypi.org/project/figurelint/

## Product Hunt

### Product name

**FigureLint**

### Tagline

**Catch publication-quality figure problems before submission**

### Short description

FigureLint is an open-source linter for academic figures. It checks PNG/JPEG, SVG, and PDF files for reproducible technical issues such as low DPI, problematic font/stroke sizes, missing PDF font embedding, and more — from the command line or GitHub Actions.

### Maker comment

Hi Product Hunt 👋

I built FigureLint around a simple frustration: academic figures often fail technical checks that are easy to miss by eye.

Instead of another plotting library, FigureLint sits after plotting and before submission. You give it the exported figures, and it checks properties that can be verified deterministically.

~~~bash
pip install figurelint
figurelint check figures/
~~~

v0.1.0 supports PNG/JPEG, SVG, and PDF, plus GitHub Actions and named presets.

One design principle matters a lot to me: publisher-specific presets should be traceable. The current Nature preset records its official source and separates source-backed rules from FigureLint's own convenience defaults.

This is an alpha release, so I'm looking for real-world figures that break assumptions, trigger false positives, or expose missing checks.

I'd love feedback from researchers, students, scientific-visualization folks, and maintainers of reproducible research workflows.

## X / LinkedIn short launch

I just released **FigureLint v0.1.0** — an open-source linter for academic figures.

🐈‍⬛ PNG/JPEG, SVG & PDF checks  
📐 DPI, font size, stroke width, font embedding & more  
📚 source-backed Nature preset  
⚙️ GitHub Actions annotations  
📦 `pip install figurelint`

GitHub: https://github.com/coocoomaomao/FigureLint  
PyPI: https://pypi.org/project/figurelint/

Feedback from researchers with real submission workflows is very welcome.

## README / repository badge for users

Users can show that a repository checks figures with FigureLint:

~~~markdown
[![Figures checked with FigureLint](https://img.shields.io/badge/figures-checked%20with%20FigureLint-2CB1A1)](https://github.com/coocoomaomao/FigureLint)
~~~

Rendered badge:

[![Figures checked with FigureLint](https://img.shields.io/badge/figures-checked%20with%20FigureLint-2CB1A1)](https://github.com/coocoomaomao/FigureLint)

## First visual campaign

Recommended three launch graphics:

### 1. Problem / solution cover

Format: 3:4 or 4:5.

Headline:

> 论文图看起来很清楚  
> ≠  
> 投稿技术上没问题

Subhead:

> DPI / 字号 / 线宽 / 字体嵌入 / PDF  
> 一条命令先体检

Footer:

> FigureLint · open source · pip install figurelint

### 2. Terminal demo

Format: 16:9.

Left: a simple scientific SVG figure.  
Right: terminal output showing `SVG_FONT_SMALL`, `SVG_STROKE_THIN`, and a clean re-check after fixes.

Headline:

> ESLint for academic figures.

### 3. Nature preset card

Format: 1:1.

Headline:

> `--preset nature`

Supporting text:

> Source-backed rules, not guessed standards.

Small-print clarification:

> Checks a documented, automatable subset of Nature figure guidance. Not a submission certification.

## Launch principles

- Lead with the researcher problem, not "please star my repo."
- Show a real command within the first screen/post.
- Ask for real-world edge cases and bug reports.
- Never claim FigureLint guarantees journal acceptance or full compliance.
- For publisher presets, say "source-backed subset" rather than "official validator."
- Prefer one memorable phrase consistently: **ESLint for academic figures.**
