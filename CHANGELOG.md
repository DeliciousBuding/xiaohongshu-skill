# Changelog

All notable changes to this project are documented here. This project uses
[Conventional Commits](https://www.conventionalcommits.org/) and keeps one
version source of truth in `pyproject.toml`.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.5.1] - 2026-08-24

### Changed

- Relicensed the project from MIT to Apache-2.0. The copyright holder is now
  `DeliciousBuding`. Module docstrings use neutral Apache-2.0 attribution and
  point to `THIRD_PARTY_NOTICES.md`.

## [1.5.0] - 2026-08-24

### Added

- `creator-login` and `check-creator-login` commands for Creator Center session
  detection, adapted from a community contribution.
- Reproducible dependency lockfile and `uv`-based local, CI, and Docker builds.
- Agent Skills frontmatter validation gate.
- Package build, wheel install smoke test, and container build checks in CI.
- Release version consistency and build provenance attestation.
- Session metadata with a stable, seed-derived fingerprint for each account
  profile.
- Architecture, releasing, and third-party attribution documentation.

### Changed

- Publish submission now reports `confirmed`, `submitted_unconfirmed`, `failed`,
  or `ready`. A button click is no longer reported as a successful publish.
- Publish inputs are validated before browser navigation; invalid schedules and
  missing or unreadable media are rejected up front.
- Browser selectors are now a single source of truth derived by runtime modules.
- Chromium sandbox is enabled by default; `XHS_ALLOW_NO_SANDBOX=true` is opt-in
  only for isolated environments that require it.
- Docker image runs as a non-root user and excludes local state from its build
  context.
- Public documentation now uses a neutral product voice and generic paths.

### Fixed

- Corrected the v1.4.0 release whose package artifacts were labeled `1.3.0`.
- Pinned `ruff` so the repository quality gate no longer fails when a new ruff
  version expands its default rule set.
- Removed the cookie-only login heuristic so login state follows the actual
  authenticated page.

## [1.4.0] - 2026-05-27

- Anti-detection upgrade and publishing enhancements.
- Note: this release's uploaded wheel and source archive were mislabeled as
  `1.3.0`; see [1.5.0] for the corrected packaging pipeline.

## [1.3.0] - 2026-05-27

- Productized packaging, documentation, and CI.

[1.5.0]: https://github.com/DeliciousBuding/xiaohongshu-skill/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/DeliciousBuding/xiaohongshu-skill/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/DeliciousBuding/xiaohongshu-skill/releases/tag/v1.3.0
