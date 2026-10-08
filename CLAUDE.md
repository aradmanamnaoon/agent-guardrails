# Agent Guardrails — Project Context

## What this repo is

Three portable Agent Skills (`recon`, `preflight`, `hold`) that compose into a lifecycle for AI coding agents:

recon ──▶ preflight ──▶ execute ──▶ hold


The skills are pure Markdown (`SKILL.md`) plus one Python validator. No runtime, no dependencies, no network calls.

## Repository layout

- `LICENSE` — MIT License
- `README.md` — full project documentation with lifecycle diagram and install instructions
- `recon/SKILL.md` — research + self-rules + plan, gates on user confirmation
- `preflight/SKILL.md` — cheap test + cost estimate + residual risks, gates on user confirmation
- `hold/SKILL.md` — stop on unhandled failure, offer 3 options, gate on user choice
- `scope/SKILL.md` — drift guard that catches actions outside agreed boundaries
- `budget/SKILL.md` — context and cost tracking enforcement
- `docs/PROTOCOL.md` — how the five skills compose into a lifecycle
- `scripts/validate.py` — validates SKILL.md frontmatter against the Agent Skills spec
- `tests/` — pytest tests for the validator and skill content
- `.claude/` — Claude Code project config (skills, agents, settings)

## Rules for working in this repo

1. **Never modify `~/.claude/` or global config.** All Claude Code config is project-scoped under `.claude/`.
2. **Never install npm packages globally.** Use `npx` or project-scoped installs.
3. **Every SKILL.md must pass `python scripts/validate.py` before committing.**
4. **Keep every SKILL.md under 500 lines** — that's the Agent Skills spec limit.
5. **Frontmatter uses only these keys:** `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Anything else fails validation.
6. **No shell execution in skills.** Skills are instructions, not scripts.
7. **No network calls from skills.** Validator is local-only.

## Style

- Skill prose is direct, second-person imperative ("Run the cheapest version first").
- Each SKILL.md opens with a one-line trigger sentence.
- Every skill ends with a "Rules for this skill" section.
- Cost estimates are always ranges, never point values.

## Commands

```bash
python scripts/validate.py    # validate all SKILL.md files
pytest -q                     # run tests
npx skills add ./recon --agent claude-code   # install our own skill locally for testing