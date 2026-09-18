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

## Nature 2.0 range checks

Nature 2.0 adds upper-bound validation to the existing lower-bound rules.

Examples:

- 4.5 pt text → `SVG_FONT_SMALL`
- 8 pt ordinary text → `SVG_FONT_LARGE`
- 0.2 pt stroke → `SVG_STROKE_THIN`
- 1.2 pt stroke → `SVG_STROKE_THICK`

Boundary values are accepted:

- 5 pt and 7 pt text are within range
- 0.25 pt and 1 pt strokes are within range

Panel labels are a special case in Nature's guidance: multi-part figure labels are specified as 8 pt bold. FigureLint does **not** yet distinguish semantic panel labels from ordinary figure text, so an 8 pt SVG label will currently be reported by the generic Nature text-range rule. This limitation is documented rather than silently guessed around.

## Why some Nature rules are still not automated

Nature's current guidance also includes requirements or recommendations that FigureLint does not yet fully encode as Nature-specific rules, including:

- standard figure widths include approximately 89 mm and 183 mm, with intermediate widths also used
- Arial or Helvetica are preferred standard fonts
- text should remain editable and should not be converted to outlines
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
