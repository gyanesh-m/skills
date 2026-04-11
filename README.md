# Eval Agent Skills Catalog

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-agentskills.io-blue)](https://agentskills.io)

Curated, multi-vendor evaluation and observability skills for AI coding agents.

This repository is designed to be installed with the open `skills` CLI and discovered through the `skills.sh` ecosystem.

## Why developers use this catalog

- Centralized eval-focused skills with practical SDK guidance
- Compatible with the open Agent Skills format (`SKILL.md`)
- Installable with standard `skills` CLI commands
- Structured for curated growth across vendors and tracks

## Quick Start

Install this catalog:

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
| `galileo-python-sdk` | Galileo | stable | Evaluate, observe, protect (Python) | `npx skills add gyanesh-m/skills --skill galileo-python-sdk` |
| `galileo-typescript-sdk` | Galileo | stable | Evaluate + observe (TypeScript/JS) | `npx skills add gyanesh-m/skills --skill galileo-typescript-sdk` |

### Highlights

- **`galileo-python-sdk`**: end-to-end guidance for tracing, evaluation runs, guardrails, and Python framework integrations.
- **`galileo-typescript-sdk`**: workflow-based guidance for JS/TS observability and evaluation scoring patterns.

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
