# Security

Last updated: 2026-07-06

This project controls a real browser session. Treat local browser state as sensitive.

## What Is Stored Locally

- Browser profile data under the user's Xiaohongshu profile directory.
- Cookie backup data when the CLI saves cookies.
- QR code images under `data/` during login.
- Strategy state created by the strategy commands.

Named account profiles created with `--profile` use separate cookie and browser profile directories. Use them when one machine operates multiple accounts.

`profiles` is read-only. It reports local profile names and whether local state files exist.

Do not commit runtime data. The repository `.gitignore` excludes the known local files.

## Public Issue Rules

When opening an issue, remove:

- Account names, phone numbers, email addresses, and profile links.
- Cookie values and browser profile files.
- Full `xsec_token` values. Keep only a short prefix if needed.
- Screenshots that show private messages, account pages, notifications, or QR codes.
- Local machine paths that include a user name or private workspace name.

Use placeholders:

```text
/path/to/image.jpg
C:\path\to\image.jpg
~/.xiaohongshu/
note-id
xsec_token-prefix...
```

## Agent Safety Rules

- Ask before write commands.
- Keep `auto_publish` off unless the user explicitly asks to publish.
- Use separate `--profile` values for separate accounts.
- Stop on captcha or verification pages.
- Use headed mode when the site asks for manual action.
- Do not run bulk scraping loops from public examples.

## Maintainer Checks

Run these before release:

```bash
python -m scripts.quality check
python -m scripts.quality contracts
```

`scripts.docs_check` scans public Markdown for private paths, common secret shapes, and writing patterns that should not ship.

Live and e2e tests are separate from release checks. Run them only with a test account:

```bash
python -m scripts.quality live
```
