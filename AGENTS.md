# AGENTS.md

## Cursor Cloud specific instructions

This repository (`gyanesh-m/skills`) provides Agent Skills for the Galileo AI platform following the [agentskills.io](https://agentskills.io) specification.

### Repository structure

- `skills/galileo-python-sdk/` — Python SDK skill (SKILL.md + references/)
- `skills/galileo-typescript-sdk/` — TypeScript SDK skill (SKILL.md + references/)
- `skills.json` — Skill registry manifest
- `src/index.js` — CLI installer for `npx add-skill gyanesh-m/skills`
- `scripts/validate.js` — Validation script for skill files and manifest

### Key commands

- **Lint/validate:** `npm run lint` or `node scripts/validate.js`
- **Test:** `npm test` (runs the same validation)
- **Run CLI installer:** `node src/index.js --list` to list skills, `node src/index.js --skill <name> --agent <agent>` to install
- **CI:** `.github/workflows/validate.yml` runs validation on push/PR to master

### Notes

- No runtime dependencies — the project is pure Node.js with no `node_modules` needed.
- The CLI installer uses `curl` to fetch files from GitHub when run via `npx`; locally it reads from the filesystem.
- When adding a new skill, update three places: the skill directory, `skills.json`, and `SKILLS_MANIFEST` in `src/index.js`.
