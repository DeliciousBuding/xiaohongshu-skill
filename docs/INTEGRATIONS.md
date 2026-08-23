# Integrations

xiaohongshu-skill exposes one JSON CLI contract to agent hosts, editors, and workflow tools.

## Command contract

Run commands from the repository or installed Skill directory:

```bash
uv run python -m scripts <command>
```

When installed globally:

```bash
xiaohongshu-skill <command>
```

Standard output contains JSON. Progress and diagnostics use standard error. Integrations should parse `status` and the published output contracts instead of matching human-readable messages.

## Claude Code

Install with the Agent Skills CLI or clone into the Claude Skills directory:

```bash
npx skills add DeliciousBuding/xiaohongshu-skill
```

Manual location:

```text
~/.claude/skills/xiaohongshu-skill
```

The agent must request explicit confirmation before write commands.

## Codex and Cursor

Install into the shared Agent Skills view:

```text
~/.agents/skills/xiaohongshu-skill
```

The Skill frontmatter is validated against the Agent Skills reference implementation. Runtime commands remain the same across supported hosts.

## OpenClaw and ClawHub

```bash
clawhub install xiaohongshu-skill
```

The OpenClaw metadata declares supported operating systems and a Python runtime requirement. Python dependencies and Playwright Chromium still need to be installed in the Skill directory.

## skills.sh

```bash
npx skills add DeliciousBuding/xiaohongshu-skill
```

The repository root is the Skill root. `SKILL.md` contains the thin agent entry point; detailed command and safety material is kept under `docs/`.

## Workflow tools

Any tool that can execute a process and parse JSON can use the CLI. A typical read-only flow is:

1. Run `check-login`.
2. Run `search`.
3. Select a result and retain its current-session identifiers.
4. Run `feed` or `user`.
5. Store structured output after removing account-sensitive fields.

A write flow must pause for user confirmation before starting the mutation command.

## Publish integration rule

Treat publish states as follows:

- `confirmed`: success.
- `ready`: prepared, not submitted.
- `submitted_unconfirmed`: indeterminate; review manually and do not retry automatically.
- `failed`: failure.

Exit code `2` is used for an indeterminate submission or another incomplete interactive outcome. Consumers must inspect JSON instead of treating every nonzero code as safely retryable.

## Contract discovery

```bash
uv run python -m scripts contracts
uv run python -m scripts selectors
```

The contract output is intended for discovery and diagnostics. Stable required fields are defined in `scripts/output_contracts.py`; named browser targets are defined in `scripts/selectors.py`.
