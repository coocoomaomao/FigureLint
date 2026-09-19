# Publishing FigureLint

FigureLint uses **PyPI Trusted Publishing** through GitHub Actions. No long-lived PyPI API token needs to be stored in GitHub.

## One-time PyPI setup

Before the first release, configure a GitHub Actions trusted publisher on PyPI for:

- Owner: `coocoomaomao`
- Repository: `FigureLint`
- Workflow: `release.yml`
- Environment: `pypi`

The workflow file is:

`.github/workflows/release.yml`

PyPI supports a pending trusted publisher for a project that has not been created yet, so the first successful publication can create the project.

Official PyPI documentation:
https://docs.pypi.org/trusted-publishers/

## GitHub environment

Create a GitHub Actions environment named `pypi`.

For stronger release protection, add a required reviewer to that environment. The publishing job uses only the OIDC `id-token: write` permission and does not need a stored PyPI password or token.

## Release checklist

Before publishing a release:

1. Confirm CI is green on `main`.
2. Confirm the version in `pyproject.toml`.
3. Confirm `CHANGELOG.md` and the release notes are up to date.
4. Create a GitHub Release with a matching tag such as `v0.1.0`.
5. Publishing the GitHub Release triggers `.github/workflows/release.yml`.
6. The workflow builds the wheel and source distribution, then publishes them to PyPI through Trusted Publishing.
7. Verify:

~~~bash
python -m pip install --upgrade figurelint
figurelint --help
figurelint presets
~~~

## Security model

The release workflow separates building from publishing. Only the publish job receives the OIDC permission required for PyPI.

Do not add untrusted build steps to the publish job. Review changes to `.github/workflows/release.yml` carefully because PyPI trusts that exact workflow identity.

## Version rule

PyPI versions are immutable. Once `0.1.0` is uploaded, that version cannot be replaced with different files. Fixes must use a new version such as `0.1.1`.
