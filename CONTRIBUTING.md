# Contributing

Contributions are welcome. Search existing issues before starting a change that affects public behavior or command contracts.

## Development environment

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git
cd xiaohongshu-skill
uv sync --frozen --group dev
uv run playwright install chromium
uv run python -m scripts.quality check
```

The lockfile is committed. Dependency updates must update `pyproject.toml` and `uv.lock` in the same pull request.

## Branches and commits

Create a focused branch from `main`:

```text
feat/<topic>
fix/<topic>
docs/<topic>
chore/<topic>
```

Use Conventional Commits such as `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, and `chore:`. Keep commits reviewable and squash temporary work before merge.

## Required checks

```bash
uv run python -m scripts.quality check
```

This command covers public documentation, Pages content, ruff, pytest, contract smoke tests, and Agent Skills frontmatter validation.

Useful targeted checks:

```bash
uv run pytest tests/test_publish.py -q
uv run pytest tests/test_selectors.py -q
uv run ruff check scripts tests
uv build
```

Default tests must not access Xiaohongshu. Do not add skip markers to hide failures. Live tests require `XHS_LIVE_TEST=1` and a dedicated account.

## Change rules

### Browser selectors

Update or add a named `SelectorContract` when the selector is shared, safety-critical, agent-facing, or expected to change across page versions. Runtime constants must derive from the contract rather than duplicate its string value.

### JSON output

Update `scripts/output_contracts.py` and tests when an agent-facing field or status changes. New fields should be backward-compatible within the 1.x series.

### Publishing

Do not treat a click as proof of publication. New publish paths must return `confirmed`, `submitted_unconfirmed`, `failed`, or `ready` with the documented semantics.

### Session storage

Use temporary directories in tests. Never read a contributor's real account profile. Persistent-state changes require corruption, compatibility, and rollback tests.

### Documentation

Public files must use generic paths and neutral product language. Do not include private infrastructure, local workspace names, credentials, account data, or internal execution notes.

## Pull requests

A pull request should include:

- The user-visible problem and chosen behavior.
- Tests for the changed behavior.
- Output or selector contract changes when applicable.
- Documentation changes when installation, safety, or public behavior changed.
- A note when upstream code or behavior influenced the implementation.

Repository rules require CI before merge. Write operations against a real account are never required for a contributor pull request.
