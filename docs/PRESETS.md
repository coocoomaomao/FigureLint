# Preset engine

FigureLint presets are named collections of thresholds used across raster, SVG, and PDF checks.

The preset system is designed so that future publisher-specific profiles can include provenance metadata such as an official guideline name, source URL, and verification status.

## Built-in convenience presets

These profiles are maintained by FigureLint. They are **not publisher policies**.

| Preset | Raster / PDF image DPI | Raster short side | SVG font size | SVG stroke | PDF page range |
| --- | ---: | ---: | ---: | ---: | --- |
| `default` | 300 | 600 px | 7 pt | 0.5 pt | 1–20 in |
| `high-resolution` | 600 | 1200 px | 7 pt | 0.5 pt | 1–20 in |
| `presentation` | 150 | 960 px | 12 pt | 0.75 pt | 1–40 in |
| `journal-generic` | 300 | 900 px | 8 pt | 0.5 pt | 1–20 in |

`journal` is accepted as an alias for `journal-generic`.

## Source-verified publisher presets

### Nature

`nature` is the first source-verified publisher preset.

It currently maps official Nature guidance to the checks FigureLint can deterministically enforce:

- 300 dpi minimum for photographic/raster imagery
- 5–7 pt ordinary text range
- 8 pt bold upright `a,b,c...` panel-label policy with conservative sequence detection
- one explicit font family throughout, with Arial/Helvetica preference guidance
- 0.25–1 pt line/stroke range
- 247 mm page-depth guardrail for PDF long-side checks

It deliberately leaves unsourced FigureLint convenience thresholds disabled.

See [Nature preset provenance and interpretation](NATURE.md).

## List presets

~~~bash
figurelint presets
~~~

## Select a preset

~~~bash
figurelint check figure.svg --preset high-resolution
~~~

~~~bash
figurelint check figures/ --preset journal-generic
~~~

## Override one value

Explicit CLI thresholds always override the selected preset.

For example:

~~~bash
figurelint check figure.svg \
  --preset journal-generic \
  --min-font-size-pt 9
~~~

This uses every `journal-generic` value except the SVG minimum font size, which becomes 9 pt.

The same rule applies to:

- `--min-dpi`
- `--min-short-side`
- `--min-font-size-pt`
- `--max-font-size-pt`
- `--min-stroke-width-pt`
- `--max-stroke-width-pt`
- `--min-pdf-short-side-in`
- `--max-pdf-long-side-in`

## Why convenience presets exist

They make common workflows easier to express without turning every command into a long list of thresholds.

For example, a user reviewing slide graphics can choose a profile that emphasizes large labels, while a raster-heavy export review can choose a stricter DPI profile.

These profiles are product defaults, not statements about what a publisher requires.

## Adding more verified publisher presets

A publisher-specific preset should not be added merely because a threshold is common on the internet.

FigureLint's preset model already contains provenance fields for:

- source name
- source URL
- source verification status

A future verified preset should:

1. be grounded in an official or otherwise authoritative guideline,
2. document which rules are directly sourced,
3. distinguish publisher requirements from FigureLint recommendations,
4. record the source URL in the preset metadata,
5. remain explicit about rules that FigureLint cannot check deterministically.

This is the mechanism used by the Nature profile and intended for future Science, IEEE, or other publisher profiles.
