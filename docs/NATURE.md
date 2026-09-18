# Nature preset

FigureLint's `nature` preset is the project's first source-verified publisher profile.

It is intentionally conservative: the preset only enables numeric thresholds that are explicitly supported by Nature's official figure guidance and that FigureLint can currently check deterministically.

## Official sources

Primary source:

- Nature, **Final submission**  
  https://www.nature.com/nature/for-authors/final-submission

Supporting sources:

- Nature, **Initial submission**  
  https://www.nature.com/nature/for-authors/initial-submission
- Nature Research Figure Guide, **Preparing figures — our specifications**  
  https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/

Verified on: **2026-09-18**

## Automated rules

| FigureLint rule | Nature guidance used | FigureLint behavior |
| --- | --- | --- |
| Raster / embedded-image minimum DPI | Photographic images must be at least 300 dpi | Warn below 300 dpi |
| SVG text size range | Ordinary figure text: minimum 5 pt, maximum 7 pt | Warn below 5 pt or above 7 pt |
| SVG stroke-width range | Line weights and strokes: 0.25–1 pt at final size | Warn below 0.25 pt or above 1 pt |
| PDF long-side page guardrail | Nature lists full page depth as 247 mm | Warn when PDF long side exceeds 247 mm |

Run:

~~~bash
figurelint check figure.svg --preset nature
~~~

or:

~~~bash
figurelint check figures/ --preset nature
~~~

The CLI prints the official source URL whenever a source-verified preset is active.

## Nature 3.0 semantic SVG checks

Nature 3.0 keeps the 2.0 range checks and adds conservative recognition of multi-panel labels plus font-family guidance.

### Panel labels

Nature specifies multi-part panel labels as **8 pt, bold, upright lower-case letters**. FigureLint only treats standalone lowercase letters as panel labels when it sees a contiguous sequence beginning with at least `a` and `b` (for example `a,b` or `a,b,c`). This deliberately avoids assuming that every isolated one-letter annotation is a panel label.

Recognized panel labels are exempt from the ordinary 7 pt maximum and are checked separately:

- wrong size → `SVG_PANEL_LABEL_SIZE`
- not bold → `SVG_PANEL_LABEL_WEIGHT`
- italic/oblique → `SVG_PANEL_LABEL_STYLE`

### Font family

Nature asks for one sans-serif typeface throughout the figures and prefers Helvetica or Arial. When font-family declarations can be resolved, FigureLint reports:

- mixed explicit primary families → `SVG_FONT_INCONSISTENT` (warning)
- explicit families outside the preferred Arial/Helvetica set → `SVG_FONT_NOT_PREFERRED` (informational)
- text whose font family cannot be resolved → `SVG_FONT_FAMILY_UNKNOWN` (informational)

The preferred-family finding is informational because Nature's final guidance says Helvetica or Arial are preferred, while the broader sans-serif requirement is the more fundamental rule.

### Editable text / outlines

Nature says not to rasterize or convert figure text to outlines. FigureLint already reports `SVG_NO_EDITABLE_TEXT` when an SVG has no editable `<text>` elements.

FigureLint does **not** claim that arbitrary vector paths are definitely outlined letters. Distinguishing outlined text from legitimate line art requires stronger semantic evidence, so this remains a conservative informational check rather than a fabricated pass/fail decision.

## Nature 2.0 range checks

Nature 2.0 added upper-bound validation to the existing lower-bound rules.

Examples:

- 4.5 pt text → `SVG_FONT_SMALL`
- 8 pt ordinary text → `SVG_FONT_LARGE`
- 0.2 pt stroke → `SVG_STROKE_THIN`
- 1.2 pt stroke → `SVG_STROKE_THICK`

Boundary values are accepted:

- 5 pt and 7 pt text are within range
- 0.25 pt and 1 pt strokes are within range

Nature 3.0 now handles the common panel-label case conservatively. It still will not guess when labels do not form a clear `a,b,c...` sequence.

## Why some Nature rules are still not automated

Nature's current guidance also includes requirements or recommendations that FigureLint does not yet fully encode as Nature-specific rules, including:

- standard figure widths include approximately 89 mm and 183 mm, with intermediate widths also used
- fully proving whether vector paths represent outlined text
- verifying the physical position of every panel label within each panel
- fonts should be embedded
- RGB is recommended for supplied artwork
- accessible colour choices are requested
- vector artwork is preferred for line art, graphs, text, arrows and scale bars
- panel labels are 8 pt bold, upright lowercase letters

Some of these are already partly detectable by FigureLint's general PDF/SVG checks — for example editable text and PDF font embedding — but are not yet represented as fully semantic Nature-specific pass/fail rules.

## Important interpretation notes

### 300 dpi is a minimum, not the whole image-resolution story

Nature's final-submission guidance describes photographic images in the 300–600 dpi range and states that photographic images must be at least 300 dpi.

FigureLint therefore uses **300 dpi as the minimum warning threshold**. It does not claim that every Nature image should be exactly 300 dpi.

### 247 mm is a page-depth guide

Nature describes 247 mm as the full depth of a Nature page. FigureLint maps that to a PDF long-side warning because it is a useful structural guardrail.

That warning should not be interpreted as a universal rejection rule for every possible Nature production workflow.

### No hidden FigureLint thresholds

The `nature` preset deliberately disables two unsourced convenience checks:

- raster minimum pixel short side
- PDF minimum physical short side

This prevents FigureLint's own defaults from being presented as Nature requirements.

Users can still add explicit overrides:

~~~bash
figurelint check figure.svg \
  --preset nature \
  --max-font-size-pt 8
~~~

In that case the 8 pt value is the user's override, not a Nature rule.

## Provenance model

The `nature` preset stores:

- the official source name
- the official source URL
- a verification flag
- the exact threshold fields that are source-backed

This lets FigureLint distinguish source-verified publisher rules from convenience presets.
