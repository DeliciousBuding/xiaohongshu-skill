# AGENTS.md

xiaohongshu-skill is a Xiaohongshu browser toolkit and Agent Skill. `SKILL.md` is the agent entry point; public product and technical documentation lives in `README.md` and `docs/`.

## Safety

- Read-only commands: `search`, `feed`, `user`, `me`, `explore`, `check-login`, `profiles`, `selectors`, `contracts`.
- Account-changing commands require explicit user confirmation before execution.
- Stop on captcha, login, or security-verification pages.
- Never expose local account state, authentication values, QR codes, or complete security parameters.
- `submitted_unconfirmed` is not success and must not be retried automatically.

## Execution

Use the JSON CLI instead of importing action modules directly:

```bash
uv run python -m scripts <command>
```

Use `--profile <name>` for account isolation. Identifiers and `xsec_token` values should come from the current browser session.

## Development

- Python 3.10 to 3.12.
- Dependencies: `pyproject.toml` and committed `uv.lock`.
- Default gate: `uv run python -m scripts.quality check`.
- Live tests are opt-in with `XHS_LIVE_TEST=1` and should use a dedicated account.
- New public behavior requires tests.
- Use Conventional Commits.

When changing selectors, use `scripts/selectors.py` as the source of truth and run `tests/test_selectors.py`. When changing JSON fields or statuses, update `scripts/output_contracts.py` and its tests.

## Architecture

- CLI adapter: `scripts/__main__.py`
- Browser session and local state: `scripts/client.py`, `scripts/profiles.py`, `scripts/session_store.py`
- Actions: login, search, feed, user, publish, comment, interact, explore
- Contracts: `scripts/selectors.py`, `scripts/output_contracts.py`
- Workflows: templates, strategy, SOP

See `docs/ARCHITECTURE.md` for boundaries and compatibility policy.

## Public repository boundary

Public files must contain only product behavior, public APIs, generic examples, and source attribution. Do not add private infrastructure, local workspace paths, internal operator notes, or credentials.
