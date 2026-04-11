# Eval Agent Skills Catalog

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-agentskills.io-blue)](https://agentskills.io)

Curated, multi-vendor evaluation and observability skills for AI coding agents.

This repository is designed to be installed with the open `skills` CLI and discovered through the `skills.sh` ecosystem.

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

### `galileo-python-sdk`

Galileo Python SDK guide for evaluate, observe, and protect workflows:

- Observability and tracing with `galileo_context` and `@log`
- Wrapped OpenAI client instrumentation
- Evaluation experiments with `promptquality`
- Runtime guardrails with Galileo Protect
- Integrations across common Python agent frameworks

### `galileo-typescript-sdk`

Galileo TypeScript/JS SDK guide for evaluation and production monitoring:

- `GalileoEvaluateWorkflow` and scoring configuration
- `GalileoObserveWorkflow` for production traces
- LLM, retriever, and tool step logging patterns
- Integration guidance for JS/TS agent stacks

## Submission Model

This project is evolving into a curated multi-vendor index for eval skills:

- `skills/.curated/` for reviewed, production-ready skills
- `skills/.experimental/` for in-progress vendor submissions
- `skills/.system/` for maintainer-only internal skills (optional)

See [CONTRIBUTING.md](CONTRIBUTING.md) for submission rules and naming conventions.

## Resources

- Agent Skills specification: https://agentskills.io
- Open `skills` CLI: https://github.com/vercel-labs/skills
- Skills directory: https://skills.sh
- Galileo docs: https://docs.galileo.ai

## License

[MIT](LICENSE)
