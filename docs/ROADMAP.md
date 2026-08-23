# Roadmap

The project prioritizes correctness and account safety over protocol count or automation volume.

## Current priorities

1. Keep login, selector, and publish behavior resilient to page changes.
2. Preserve reproducible Python, package, and Docker builds.
3. Maintain stable JSON and selector contracts for agent integrations.
4. Keep session data private, backward-compatible, and recoverable.
5. Require explicit confirmation before account-mutating operations.

## Planned improvements

### Browser fixtures

Add sanitized HTML and state fixtures for extraction logic so more browser behavior can be tested without live network access.

### Mutation safety

Evaluate a structured preview and explicit execution flag for account-mutating CLI commands in the next major version. Existing 1.x command behavior remains compatible.

### Package layout

Move from the generic `scripts` package to `src/xiaohongshu_skill` only in a major release with import compatibility shims.

### Optional integrations

Add service protocols such as MCP or REST only when a concrete integration cannot use the current JSON CLI contract.

## Non-goals

- Bulk scraping or high-volume account automation.
- Automatic captcha bypass.
- Silent publish success after an unconfirmed submission.
- Copying large-project release or community automation without a local need.
