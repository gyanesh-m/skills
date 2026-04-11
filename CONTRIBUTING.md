# Contributing to the Agent Skills Catalog

Thank you for your interest in contributing! This guide explains how to add new skills or improve existing ones in this curated multi-vendor eval catalog.

## How Skills Are Structured

Each skill lives in its own directory under one of the catalog tracks:

- `skills/` for stable top-level entries
- `skills/.curated/` for reviewed multi-vendor entries
- `skills/.experimental/` for draft/in-progress entries

```
skills/
└── .curated/
    └── vendor-skill-name/
    ├── SKILL.md              # Main skill file (required)
    └── references/           # Additional reference files (optional)
        ├── INTEGRATIONS.md
        ├── METRICS.md
        └── EVALUATION.md
```

### SKILL.md Format

Every skill must have a `SKILL.md` file with YAML frontmatter following the [agentskills.io specification](https://agentskills.io/specification):

```yaml
---
name: my-skill-name          # Required — must match directory name
description: >-              # Required — what this skill does and when to use it
  Description of the skill.
license: MIT                  # Optional
compatibility: >-             # Optional — environment requirements
  Requires Python 3.9+.
metadata:                     # Optional — additional metadata
  author: your-github-username
  version: "1.0.0"
---
```

The body of `SKILL.md` is Markdown containing instructions, code examples, and best practices that teach an AI coding assistant how to use the relevant SDK or tool.

### Reference Files

Place additional reference files in a `references/` subdirectory. These are linked from the main `SKILL.md` and provide deeper coverage of specific topics.

## Adding a New Skill

1. **Create a directory** under `skills/.experimental/` (or `skills/.curated/` if already reviewed) with a lowercase, hyphenated, vendor-prefixed name (for example: `galileo-rag-eval`).
2. **Write `SKILL.md`** with the required YAML frontmatter and comprehensive Markdown body.
3. **Add reference files** in `references/` if the skill covers multiple topics.
4. **Register the skill** in `skills.json` at the repository root.
5. **Update `README.md`** to list the new skill under "Available Skills" if it is curated/stable.

## Testing Skills Locally

Run the validation script to check your skill files:

```bash
npm run lint
```

This validates:
- All skills referenced in `skills.json` have a valid `SKILL.md` with required frontmatter
- Skill names match their directory names
- Referenced paths exist

To test catalog discovery locally with the official CLI:

```bash
npx skills add gyanesh-m/skills --list
npx skills add gyanesh-m/skills --skill your-skill-name
```

## Pull Request Process

1. Fork the repository and create a feature branch.
2. Add or modify your skill files.
3. Run `npm run lint` to validate.
4. Submit a pull request with a clear description of your changes.
5. Ensure CI checks pass.

## Code of Conduct

Be respectful and constructive in all interactions. We follow the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

## Questions?

Open an issue on the [GitHub repository](https://github.com/gyanesh-m/skills/issues).
