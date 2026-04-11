# AGENTS.md

## Cursor Cloud specific instructions

This repository (`gyanesh-m/skills`) is an eval-focused Agent Skills catalog intended for discovery and installation through the open `skills` CLI and `skills.sh`.

### Repository structure

- `skills/` — stable skill entries
- `skills/.curated/` — reviewed multi-vendor catalog entries
- `skills/.experimental/` — in-progress or draft entries
- `skills/.system/` — optional maintainer-only internal entries
- `skills.json` — optional registry manifest used by local validation
- `scripts/validate.js` — validation script for manifest + SKILL frontmatter

### Key commands

- **List catalog skills with official CLI:** `npx skills add gyanesh-m/skills --list`
- **Install catalog skills with official CLI:** `npx skills add gyanesh-m/skills --skill <name>`
- **Lint/validate metadata:** `npm run lint` or `node scripts/validate.js`
- **CI:** `.github/workflows/validate.yml` runs validation on push/PR to master

### Notes

- Primary compatibility target is the `skills` CLI repository model (`npx skills add <owner/repo>`).
- Keep skill names kebab-case and globally unique (prefer vendor-prefix naming).
- Each skill requires `SKILL.md` frontmatter with `name` and `description`.
