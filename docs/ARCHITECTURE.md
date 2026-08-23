# Architecture

xiaohongshu-skill ships one browser automation core through four product surfaces:

1. **Agent Skill** — `SKILL.md` selects the capability and defines safety rules.
2. **CLI** — `python -m scripts` and the installed `xiaohongshu-skill` command.
3. **Python package** — reusable action classes and workflow helpers.
4. **Docker image** — an isolated CLI runtime with persistent account data mounted from the host.

## Runtime boundaries

```text
CLI adapter
  parses arguments, selects a profile, prints JSON, maps errors to exit codes
       |
Domain actions
  login, search, feed, user, publish, comment, and interaction behavior
       |
Browser session
  Playwright lifecycle, throttling, captcha detection, profiles, cookies, fingerprint seed
       |
Xiaohongshu web interfaces
```

Supporting layers:

- **Contracts** — named browser selectors and agent-facing JSON output shapes.
- **Workflows** — templates, strategy state, and SOP orchestration.
- **Quality gates** — documentation checks, lint, tests, contract smoke tests, and Skill validation.

The CLI is an adapter, not the owner of business validation. Rules that must also apply to the Python API or SOP workflows belong in the action or domain layer.

## Session storage

Each account profile has three independent state surfaces:

- Playwright persistent browser data: the primary web session.
- `cookies.json`: a backward-compatible cookie backup stored as a JSON array.
- `session.json`: versioned metadata containing the stable fingerprint seed and save timestamp.

`XHS_FP_SEED` can override the stored seed for one process. The override is not written back. Metadata and cookie backups use atomic file replacement to reduce partial-write corruption.

## Selector contracts

`scripts/selectors.py` is the source of truth for named selectors. Runtime compatibility constants are derived from contract objects instead of copying selector strings. The contract validator fails when a runtime binding drifts.

Not every page locator needs to be centralized. A selector becomes a named contract when it is shared, agent-facing, safety-critical, or known to change across page versions.

## Publish result model

A publish submission distinguishes three states:

- `confirmed` — a trusted success signal was observed.
- `submitted_unconfirmed` — the publish control was activated, but success was not observed before timeout.
- `failed` — submission was not completed or a failure signal was observed.

Only `confirmed` is reported as success. This avoids treating a button click as proof that content was published.

## Safety model

Read operations and account-mutating operations remain separate. An agent must obtain explicit user confirmation before publish, comment, reply, like, collect, unlike, or uncollect commands.

The browser stops on captcha and security-verification pages. Default tests never contact Xiaohongshu. Live tests are opt-in and should use a dedicated test account.

Standard output is reserved for JSON results. Diagnostics and progress messages use standard error.

## Test layers

- **Unit tests** cover pure parsing, validation, state storage, and workflow behavior.
- **Contract tests** verify selector and JSON output stability.
- **Browser orchestration tests** use bounded Playwright fakes without network access.
- **Live tests** are manual, read-only by default, and gated by `XHS_LIVE_TEST=1`.
- **Packaging tests** build and install the wheel before exercising the CLI.
- **Container tests** build the image and verify that ignored local state is absent.

## Compatibility policy

The 1.x series keeps `scripts` as the import package and preserves existing command names. Larger source-layout changes belong in a future major version and require compatibility shims.

MCP or REST servers are not part of the current architecture. They should be added only when a concrete integration requires a long-running service rather than the existing CLI contract.
