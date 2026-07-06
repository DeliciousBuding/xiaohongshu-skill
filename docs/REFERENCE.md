# Reference Project Map

Last updated: 2026-07-06

This file records what the project borrows from nearby Xiaohongshu and RedNote automation projects. It uses public repository facts only.

## Repositories Checked

| Project | Public signal checked on 2026-07-06 | What to borrow |
| --- | ---: | --- |
| `xpzouying/xiaohongshu-mcp` | 14.5k stars, 2.1k forks | Clear install choices, client setup examples, Docker path, FAQ, public demos, contributor credit |
| `iFurySt/RedNote-MCP` | 1.1k stars, 173 forks | NPM-style quick start, MCP Inspector workflow, simple Cursor config |
| `autoclaw-cc/xiaohongshu-mcp-skills` | 231 stars, 43 forks | Skill split by task area and OpenClaw install notes |
| `DeliciousBuding/xiaohongshu-skill` | 32 stars, 8 forks | Skill-first Python CLI with publish, interaction, templates, strategy, and SOP commands |

## Adopted Here

- Four entry paths in README: ClawHub, global CLI, local Skill folder, Docker.
- Public Pages site with demo JSON, `robots.txt`, `sitemap.xml`, and `llms.txt`.
- Selector and output contracts for agent integrations.
- Profile isolation for machines that operate more than one account.
- Small examples for Cursor, n8n, and OpenClaw.
- Live tests gated by `XHS_LIVE_TEST=1`.
- Public documentation checks for private paths, tokens, cookies, and writing patterns.
- GitHub Actions for CI and Pages deployment.

## Next Candidates

| Candidate | Why it helps | Safe first step |
| --- | --- | --- |
| Client setup snippets | Users copy config faster when examples match their agent | Add or extend examples for Cline and more agent shells |
| Demo media | Mature projects show real workflows in one glance | Add synthetic or redacted GIFs only after privacy review |
| Release artifacts | Binary and package releases reduce setup friction | Add a release checklist before adding publishing automation |
| Community examples | More examples make the repo easier to trust | Add a `showcases` section that accepts PRs without private screenshots |
| HTTP/MCP wrapper | Some clients cannot use local Skills directly | Design it as a separate optional layer, not a rewrite of the CLI |

## Not Copied

- Real account screenshots, QR codes, group QR codes, and local user paths.
- Claims about account safety that cannot be verified for every user.
- Bulk scraping examples or prompts that encourage abuse.
- A hard dependency on MCP. The current project remains a Skill and CLI first.
