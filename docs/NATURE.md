# Nature preset

FigureLint's `nature` preset is the project's first source-verified publisher profile.

It is intentionally conservative: the preset only enables numeric thresholds that are explicitly supported by Nature's official figure guidance and that FigureLint can currently check deterministically.

## Official sources

Primary source:

- Nature, **Final submission**  
  https://www.nature.com/nature/for-authors/final-submission

Supporting source:

- Nature Research Figure Guide, **Preparing figures — our specifications**  
  https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/

Verified on: **2026-09-18**

## Automated rules in the first version

| FigureLint rule | Nature guidance used | FigureLint behavior |
| --- | --- | --- |
| Raster / embedded-image minimum DPI | Photographic images must be at least 300 dpi | Warn below 300 dpi |
| Minimum editable SVG text size | Minimum ordinary figure text size is 5 pt | Warn below 5 pt |
| Minimum SVG stroke width | Nature advises 0.25–1 pt line weights at final size | Warn below 0.25 pt |
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

## Why some Nature rules are not yet automated

Nature's current guidance also includes requirements or recommendations that FigureLint does not yet fully encode in the first preset, including:

- ordinary text should generally remain within 5–7 pt
- line weights should generally remain within 0.25–1 pt
- standard figure widths include approximately 89 mm and 183 mm, with intermediate widths also used
- Arial or Helvetica are preferred standard fonts
- text should remain editable and should not be converted to outlines
- fonts should be embedded
- RGB is recommended for supplied artwork
- accessible colour choices are requested
- vector artwork is preferred for line art, graphs, text, arrows and scale bars

Some of these are already partly detectable by FigureLint's general PDF/SVG checks — for example editable text and PDF font embedding — but they are not yet represented as Nature-specific pass/fail rules.

## Important interpretation notes

### 300 dpi is a minimum, not the whole image-resolution story

Nature's final-submission guidance describes photographic images in the 300–600 dpi range and states that photographic images must be at least 300 dpi. The Nature Research Figure Guide also states a 300 dpi minimum and discusses 450 dpi for maximum online-proof resolution.

FigureLint therefore uses **300 dpi as the minimum warning threshold**. It does not claim that every Nature image should be exactly 300 dpi.

### 247 mm is a page-depth guide

Nature describes 247 mm as the full depth of a Nature page. FigureLint maps that to a PDF long-side warning because it is a useful structural guardrail.

That warning should not be interpreted as a universal rejection rule for every possible Nature production workflow.

### No hidden FigureLint thresholds

The `nature` preset deliberately disables two unsourced convenience checks:

- raster minimum pixel short side
- PDF minimum physical short side

This prevents FigureLint's own defaults from being presented as Nature requirements.

Users can still add their own explicit override:

~~~bash
figurelint check figure.png \
  --preset nature \
  --min-short-side 1200
~~~

In that case the 1200 px value is the user's override, not a Nature rule.

## Provenance model

The `nature` preset stores:

- the official source name
- the official source URL
- a verification flag
- the exact threshold fields that are source-backed

This lets FigureLint distinguish source-verified publisher rules from convenience presets.
