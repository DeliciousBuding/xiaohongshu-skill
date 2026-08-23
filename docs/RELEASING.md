# Releasing

Releases are produced from a semantic version tag after all required CI checks pass.

## Version source

`pyproject.toml` is the version source of truth. Runtime `--version` output is read from installed package metadata.

A release tag must equal `v` plus the project version. For example:

```text
pyproject version: 1.5.0
tag: v1.5.0
```

`scripts.release_check` rejects mismatched tag, project, and runtime versions.

## Release procedure

1. Create a release pull request that updates the version and public release notes.
2. Run the complete quality, Python matrix, package, and container checks.
3. Merge the release pull request into `main`.
4. Create the matching protected semantic version tag.
5. Let the Release workflow rebuild and verify the distributions from the tagged source.
6. Confirm the GitHub Release contains the wheel, source archive, checksums, and provenance attestation.
7. Publish the same version to ClawHub and inspect the published metadata and files.

Do not reuse or move a published tag. Corrections after publication require a new patch version.

## Local preflight

```bash
uv sync --frozen --group dev
uv run python -m scripts.quality check
uv build
uvx --from twine==7.0.0 twine check dist/*
```

The release workflow repeats these checks in a clean environment. A local pass is not a substitute for the tagged build.

## Rollback

Code rollback uses a normal revert commit. Persistent session files are versioned and corruption-tolerant, but a release that changes their schema must include explicit downgrade tests and recovery notes.

If a GitHub or ClawHub release contains incorrect metadata or artifacts, publish a corrected patch version and add a visible note to the affected release rather than silently replacing source tags.
