# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2026-03-27

### Changed

- Bumped package release version in `package.json` to `1.2.0` to align with the current catalog release.
- Added this changelog entry to document the `1.2.0` release metadata update.

## [1.1.0] - 2026-03-27

### Changed

- Repositioned repository as an eval-focused, multi-vendor skills catalog for `skills.sh` and the official `skills` CLI.
- Updated docs to use `npx skills add gyanesh-m/skills` as the primary installation and discovery flow.
- Added explicit catalog track conventions for `skills/.curated/`, `skills/.experimental/`, and `skills/.system/`.

## [1.0.0] - 2026-03-15

### Added

- `galileo-python-sdk` skill — Complete Python SDK reference covering observability, evaluation, guardrails, and framework integrations
- `galileo-typescript-sdk` skill — Complete TypeScript/JS SDK reference covering evaluate and observe workflows
- CLI installer (`npx add-skill gyanesh-m/skills`) supporting Claude Code, Cursor, GitHub Copilot, Codex, Gemini CLI, Amp, Roo Code, and OpenCode
- CI validation workflow for skill files and manifest
