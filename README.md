# Eval Agent Skills Catalog

[![CI](https://img.shields.io/github/actions/workflow/status/gyanesh-m/skills/validate.yml?branch=master&label=CI)](https://github.com/gyanesh-m/skills/actions/workflows/validate.yml)
[![Install via skills.sh](https://img.shields.io/badge/skills.sh-install-blue)](https://skills.sh/gyanesh-m/skills)
[![Release](https://img.shields.io/github/v/release/gyanesh-m/skills?display_name=tag&sort=semver)](https://github.com/gyanesh-m/skills/releases/latest)
[![Skills](https://img.shields.io/badge/skills-2-blue.svg)](#available-skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-agentskills.io-blue)](https://agentskills.io)

Curated, multi-vendor evaluation and observability skills for AI coding agents.

**Compatible with:** Claude Code, Codex, Cursor, OpenCode, and more via `skills` CLI.

This repository is designed to be installed with the open `skills` CLI and discovered through the `skills.sh` ecosystem.

## Why developers use this catalog

- Centralized eval-focused skills with practical SDK guidance
- Compatible with the open Agent Skills format (`SKILL.md`)
- Installable with standard `skills` CLI commands
- Structured for curated growth across vendors and tracks

## Install in 10 seconds

```bash
npx skills add gyanesh-m/skills
```

## Quick Start

Install this catalog (interactive):

```bash
npx skills add gyanesh-m/skills
```

List available skills:

```bash
npx skills add gyanesh-m/skills --list
```

Install specific skills:

```bash
npx skills add gyanesh-m/skills --skill galileo-python-sdk
npx skills add gyanesh-m/skills --skill galileo-typescript-sdk
```

Install to specific agents:

```bash
npx skills add gyanesh-m/skills -a claude-code -a cursor -a codex
```

## Catalog Layout

The official `skills` CLI discovers skills in these locations:

- `skills/`
- `skills/.curated/`
- `skills/.experimental/`
- `skills/.system/`

This repository currently keeps stable skills in `skills/` and supports curated and experimental tracks for future multi-vendor contributions.

## Available Skills

| Skill | Vendor | Track | Focus | Install |
|---|---|---|---|---|
| [`galileo-python-sdk`](skills/galileo-python-sdk/SKILL.md) | Galileo | stable | Evaluate, observe, protect (Python) | `npx skills add gyanesh-m/skills --skill galileo-python-sdk` |
| [`galileo-typescript-sdk`](skills/galileo-typescript-sdk/SKILL.md) | Galileo | stable | Evaluate + observe (TypeScript/JS) | `npx skills add gyanesh-m/skills --skill galileo-typescript-sdk` |

### Highlights

- **`galileo-python-sdk`**: end-to-end guidance for tracing, evaluation runs, guardrails, and Python framework integrations.
- **`galileo-typescript-sdk`**: workflow-based guidance for JS/TS observability and evaluation scoring patterns.

## Popular prompts / use-cases

- "Add Galileo observability and tracing to my Python agent workflow."
- "Evaluate this RAG pipeline with guardrail metrics and score quality regressions."
- "Instrument my TypeScript workflow with Galileo observe/evaluate steps."

## Submission Model

This project is evolving into a curated multi-vendor index for eval skills:

- `skills/.curated/` for reviewed, production-ready skills
- `skills/.experimental/` for in-progress vendor submissions
- `skills/.system/` for maintainer-only internal skills (optional)

See [CONTRIBUTING.md](CONTRIBUTING.md) for submission rules and naming conventions.

## Developer Workflow

```bash
# Validate skill metadata/frontmatter
npm run lint

# Discover this catalog exactly as users do
npx skills add gyanesh-m/skills --list

# Install one skill into your current project
npx skills add gyanesh-m/skills --skill galileo-python-sdk
```

## Resources

- Agent Skills specification: https://agentskills.io
- Open `skills` CLI: https://github.com/vercel-labs/skills
- Skills directory: https://skills.sh
- Galileo docs: https://docs.galileo.ai

## License

[MIT](LICENSE)
