# Changelog

All notable changes to FigureLint will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows Semantic Versioning.

## [Unreleased]

### Added
- SVG file discovery and inspection
- malformed SVG detection
- editable `<text>` detection
- configurable small-font warnings for resolvable SVG text
- configurable thin-stroke warnings
- simple embedded CSS resolution for tag, class, id, and `tag.class` selectors
- SVG CLI options: `--min-font-size-pt` and `--min-stroke-width-pt`
- SVG inspection tests and documentation

### Planned
- PDF inspection
- embedded-font checks
- color accessibility checks
- journal presets
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
