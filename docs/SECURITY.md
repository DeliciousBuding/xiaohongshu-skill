# Security

This project controls a real browser session and stores authentication state locally. Use a dedicated test account before enabling write operations.

## Local state

Each profile may contain:

- Playwright persistent browser state.
- A backward-compatible Cookie backup.
- Versioned session metadata with a fingerprint seed and timestamp.
- QR images and local command output under `data/`.
- Strategy state created by strategy commands.

Do not commit, upload, or attach these files. The repository ignore rules and Docker build exclusions cover the known local paths, but users remain responsible for files copied elsewhere.

Session metadata and Cookie backups use atomic replacement to reduce partial writes. Invalid session metadata is replaced with a new seed without printing the previous value.

## Browser sandbox

Chromium sandbox remains enabled by default. `XHS_ALLOW_NO_SANDBOX=true` is available only for isolated environments that explicitly require it. Do not set this variable for normal desktop use.

The Docker image runs as a non-root user and keeps account state in mounted host directories.

## Agent write boundary

The following commands change account state:

- `publish`, `publish-video`, `publish-md`, `publish-longform`
- `comment`, `reply`, `reply-notification`
- `like`, `collect`, `unlike`, `uncollect`
- `logout`

An agent must show the target account and planned change, then obtain explicit user confirmation before execution.

A `submitted_unconfirmed` publish result means the site may have accepted the submission. Do not retry automatically because that can create duplicate posts.

## Captcha and verification

Stop automation when the browser reaches a captcha, login, or security-verification page. Use headed mode and let the user complete the step. This project does not provide captcha bypass.

## Public issue rules

Remove the following before opening a public issue:

- Account names, phone numbers, email addresses, and profile links.
- Authentication values and local browser profile files.
- Full `xsec_token` values.
- QR codes and screenshots of account, notification, or private-message pages.
- Local machine paths containing user names or private workspace names.

Use generic placeholders such as:

```text
/path/to/image.jpg
C:\path\to\image.jpg
~/.xiaohongshu/
note-id
xsec_token-prefix...
```

## Maintainer checks

```bash
uv run python -m scripts.quality check
docker build -t xiaohongshu-skill:check .
```

Live tests are separate and opt-in:

```bash
XHS_LIVE_TEST=1 uv run pytest tests/live -q -m live
```

Use only a dedicated test account and keep live tests read-only unless a specific write test has been reviewed and approved.
