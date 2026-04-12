# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-vendor agent skills catalog for the Galileo AI platform. Skills are static Markdown reference documents with YAML frontmatter, installable via the `skills` CLI (`npx skills add gyanesh-m/skills`). Targets 8 AI coding agents (Claude Code, Cursor, Copilot, Codex, Amp, Roo, OpenCode, Gemini).

## Commands

- **Validate/lint:** `npm run lint` or `node scripts/validate.js`
- **List skills:** `npx skills add gyanesh-m/skills --list`
- **Install a skill:** `npx skills add gyanesh-m/skills --skill <name>`
- **CI:** `.github/workflows/validate.yml` runs on push/PR to `master`

There is no build step, test framework, or external dependencies. Validation is a single zero-dependency Node.js script.

## Architecture

### Skill Structure

Each skill lives in `skills/<skill-name>/` and must contain:
- `SKILL.md` — main reference document with YAML frontmatter (`name`, `description` required; `name` must match directory name)
- `references/` — optional supplemental docs (e.g., INTEGRATIONS.md, METRICS.md, EVALUATION.md)

### Key Files

- `skills.json` — registry manifest listing all skills (name, path, description). Must be updated when adding/removing skills.
- `scripts/validate.js` — validates skills.json structure, checks SKILL.md existence and frontmatter, counts reference files. Exit 0/1.
- `src/index.js` — legacy installer (pre-`skills` CLI). Maps 8 agent types to their skill directory paths.

### Catalog Tracks

- `skills/` — stable entries
- `skills/.curated/` — reviewed multi-vendor entries
- `skills/.experimental/` — drafts/in-progress
- `skills/.system/` — maintainer-only internal entries

## Conventions

- Skill directory names: kebab-case, vendor-prefixed (e.g., `galileo-python-sdk`)
- SKILL.md frontmatter must be valid YAML between `---` delimiters
- Primary branch is `master`
- When adding a skill: create directory, write SKILL.md, optionally add references/, register in skills.json, update README.md

## Web Research

`WebSearch` and `WebFetch` are **blocked in the main thread** by a pre-tool hook. Never call them directly — always spawn a subagent:

```bash
claude -p "Research X. Return a 5-line summary: finding, URL, confidence." 2>&1 | head -60
```

For N platforms, dispatch N parallel Bash tool calls in one message — do not do them sequentially. If subagents also cannot reach the live web, return training-data findings with a clear caveat rather than retrying. Do not re-ask the user to research something already attempted this session.
