---
title: "Semantic-Release Guide"
name: "semantic_release.md"
description: "Guide for using semantic versioning with conventional commits"
category: docs
usage: "Reference for developers to understand how commit messages affect version numbers"
behavior: "Explains how different types of commits trigger version bumps"
inputs: "Developer commit messages"
outputs: "Semantic version numbers"
dependencies: "semantic-release, conventional commits"
author: "LedgerBase Team"
last_modified: "2023-11-15"
changelog: "Initial version"
tags: [docs, versioning]
---

## Semantic‑Release Guide

### Commit conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: …` → **minor** bump (1.2.0 → 1.3.0)
- `fix: …`  → **patch** bump (1.2.0 → 1.2.1)
- **BREAKING CHANGE** in footer → **major** bump (1.2.0 → 2.0.0)
- `docs: …`, `chore: …`, `refactor: …` → no version bump

#### Examples

```bash
git commit -m "feat(parser): handle nested expressions"
git commit -m "fix(ui): correct color contrast"
git commit -m "perf: optimize ledger‑reconciliation speed"
git commit -m "feat!: switch to new encryption protocol

BREAKING CHANGE: old key‑format is no longer supported"
```
