# Changelog

All notable changes to FigureLint will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows Semantic Versioning.

## [Unreleased]

### Added
- Nature preset 3.0 conservative multi-panel label recognition and 8 pt bold/upright validation
- Nature SVG font-family consistency and Arial/Helvetica preference checks
- reusable opt-in SVG semantic policy support for publisher presets
- Nature preset 2.0 upper-bound checks for 5–7 pt ordinary SVG text and 0.25–1 pt SVG strokes
- generic `SVG_FONT_LARGE` and `SVG_STROKE_THICK` findings
- CLI overrides: `--max-font-size-pt` and `--max-stroke-width-pt`
- source-verified `nature` preset based on official Nature final-submission guidance
- publisher-preset provenance fields identifying which thresholds are source-backed
- support for disabling unsourced thresholds in verified publisher profiles
- Nature preset tests and provenance documentation
- preset engine with shared raster, SVG, and PDF thresholds
- `--preset` support for figure checks
- `figurelint presets` command for profile discovery
- explicit CLI threshold overrides on top of presets
- built-in convenience profiles: `default`, `high-resolution`, `presentation`, and `journal-generic`
- provenance fields for future source-verified publisher presets
- preset tests and documentation
- PDF file discovery and inspection
- malformed, encrypted, and empty-PDF detection
- multi-page and page-size PDF warnings
- editable-text detection for PDF figures
- PDF font embedding checks
- effective DPI checks for embedded PDF raster images
- PDF raster soft-mask / alpha detection
- PDF inspection tests and documentation
- SVG file discovery and inspection
- malformed SVG detection
- editable `<text>` detection
- configurable small-font warnings for resolvable SVG text
- configurable thin-stroke warnings
- simple embedded CSS resolution for tag, class, id, and `tag.class` selectors
- SVG CLI options: `--min-font-size-pt` and `--min-stroke-width-pt`
- SVG inspection tests and documentation

### Planned
- PDF font-size and vector stroke checks
- color accessibility checks
- additional source-verified publisher presets
- GitHub Action annotations

## [0.1.0] - 2026-09-18

### Added
- initial FigureLint command-line interface
- PNG and JPEG inspection
- unreadable image detection
- missing DPI warning
- low DPI warning
- small raster-dimension warning
- transparency detection
- JPEG lossy-format notice
- recursive folder scanning
- strict mode and CI-friendly exit codes
- automated tests
- GitHub Actions CI
- official black-cat visual identity
- README banner, logo, icon, dark-mode logo, and social-preview artwork

[Unreleased]: https://github.com/coocoomaomao/FigureLint/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/coocoomaomao/FigureLint/releases/tag/v0.1.0
