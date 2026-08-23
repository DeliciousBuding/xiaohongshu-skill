# Reference implementations

This project studies mature Xiaohongshu automation projects for domain behavior and failure modes. It does not copy their product scope or operational complexity by default.

## Adoption rule

A reference is adopted only when all of the following are recorded:

1. The local problem it solves.
2. The upstream symbol, tag, or commit used for comparison.
3. The local adaptation and intentional differences.
4. An automated test that protects the adopted behavior.
5. The applicable license and attribution.

Repository popularity is not an architectural requirement and is intentionally not recorded here.

## Primary domain reference

`xpzouying/xiaohongshu-mcp` is the primary behavioral reference for browser session, login, publishing, and interaction edge cases.

Adapted behaviors include:

- Loading and saving cookies across the browser context.
- Stable per-session browser fingerprint input.
- New and legacy publish control handling.
- Confirmation after publish submission instead of trusting the click alone.
- Bounded validation for publish inputs and schedules.
- Captcha and security-verification detection.

The Python implementation keeps a CLI-first product shape and Playwright persistent contexts. It does not currently adopt the upstream MCP server, REST server, binary release matrix, registry publishing pipeline, or browser auto-update workflow.

## Skill standards

The root `SKILL.md` follows the Agent Skills specification and carries a compatible OpenClaw metadata extension. CI validates the standard frontmatter using the official reference package.

## License attribution

Some modules were adapted from Apache-2.0-licensed reference code. See `THIRD_PARTY_NOTICES.md` and `licenses/Apache-2.0.txt`. Original project contributions remain under the repository `LICENSE` unless a file states otherwise.
