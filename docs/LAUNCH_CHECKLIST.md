# FigureLint Launch Checklist

This checklist tracks the non-code launch tasks for v0.1.0.

## Already complete

- [x] v0.1.0 published on GitHub
- [x] v0.1.0 published through PyPI Trusted Publishing
- [x] `pip install figurelint` documented
- [x] reusable GitHub Action available
- [x] native GitHub workflow annotations
- [x] README demo and brand system
- [x] launch copy prepared in `docs/PROMOTION.md`

## GitHub About panel

These repository-level fields require editing in the GitHub UI.

Recommended Homepage:

~~~text
https://pypi.org/project/figurelint/
~~~

Recommended Topics:

~~~text
academic-figures
scientific-visualization
research-tools
publication
python
svg
pdf
linter
academic-writing
reproducible-research
~~~

Keep the current repository description:

~~~text
A linter for academic figures — check publication-quality issues before submission.
~~~

## Social preview

Use the existing artwork:

~~~text
assets/figurelint-social-preview.svg
~~~

GitHub's Social preview setting may require a raster upload/export. Keep issue #5 open until the final PNG asset and repository social preview are configured.

## GitHub Release page

The release is live. Optional polish:

- edit the v0.1.0 release description so Markdown headings, bullets, and code blocks render cleanly
- keep the release title `FigureLint v0.1.0`
- keep tag `v0.1.0`

## GitHub Marketplace

The repository now has a root `action.yml`.

Next UI step:

1. edit / create a compatible release for the Action
2. choose **Publish this Action to the GitHub Marketplace** when GitHub offers the option
3. choose appropriate categories such as code quality / continuous integration if available
4. verify the Marketplace page shows the v0.1.0 usage example

## First launch sequence

- [ ] GitHub About topics + homepage
- [ ] social preview PNG configured
- [ ] 小红书 launch post
- [ ] Show HN
- [ ] GitHub Marketplace listing
- [ ] Product Hunt preparation / launch when ready
- [ ] collect first real-user issue reports
- [ ] summarize feedback before adding major new rules

## What success looks like for the first wave

Do not optimize only for stars.

The most useful early signals are:

- researchers successfully installing from PyPI
- real figures checked outside the maintainer's own examples
- concrete bug reports / false positives
- requests for specific publisher workflows
- external repositories adopting the GitHub Action
- contributors submitting reproducible fixtures or PRs

The first milestone should be **real usage evidence**, not vanity metrics.
