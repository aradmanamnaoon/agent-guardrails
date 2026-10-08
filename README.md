# Agent Guardrails

Five portable Agent Skills that compose into a lifecycle for AI coding agents. Stops expensive mistakes before they happen by layering research gates, cheap verification, scope enforcement, cost tracking, and failure recovery.

## The problem

AI coding agents fail expensively not because the model is weak but because the workflow has no gates. Agents write code, run commands, and make changes without stopping to ask: did I do enough homework? Is this really safe? How much will this actually cost? Scope creep turns small tasks into large refactors overnight. Cost overruns go undetected until tokens are burned or bills arrive. Unrecoverable failures leave systems broken with no path back. These three failure modes — scope creep, cost overruns, unrecoverable failures — are the norm for agentic workflows today.

## The fix

Five portable Agent Skills that compose into a lifecycle: **recon** (research and propose self-rules), **preflight** (cheap verification and cost estimation), **hold** (stop-and-recover on unhandled failures), **scope** (drift guard against silent boundary crossing), and **budget** (context and cost tracking enforcement). Each installs independently via `npx skills add`. Together they provide layered escalation where every step waits for explicit user confirmation before proceeding.

## The lifecycle

```text
                       SETUP                          EXECUTE
  ┌──────────────────────────────────────────┐  ┌──────────────────────────┐
  │                                          │  │                          │
  │  recon ──▶ preflight ──▶ (confirmed)     │  │   work   ┌─ scope         │
  │    │          │                          │  │    │     ├─ budget        │
  │    │          └──▶ budget: register      │  │    │     └─ hold          │
  │    │              baseline               │  │    │                     │
  │    └──▶ (confirmed by user)              │  │    └──▶ done / hold      │
  │                                          │  │                          │
  └──────────────────────────────────────────┘  └──────────────────────────┘
```

## What each skill does

### recon

Research and proposal gate for non-trivial coding tasks. Inspects repository state, classifies task complexity, proposes 3–7 task-specific self-rules, produces a structured report (Task / What I found / Unknowns / Anticipated failure classes / Proposed self-rules / Awaiting confirmation), then stops for user confirmation before proceeding. Designed to prevent wasted effort on misaligned plans by surfacing constraints early. Not a substitute for domain expertise — flags unknowns instead of guessing.

### preflight

Cheap verification and cost estimation gate before expensive, long-running, or irreversible operations. Identifies the cheapest verifiable version of the target operation, runs it, reports any bugs without stopping, estimates cost as a range (never a point value), lists residual risks using probability × impact columns, and stops for user confirmation before the real run begins. Use when about to train a model, batch process, loop over production data, or perform any operation that cannot be cleanly undone.

### hold

Stop-and-recover gate that triggers ONLY on failures not anticipated in preflight's residual risk list. When triggered, stops all agent action, classifies the failure (new class, materialised risk, or invalidated plan), produces a structured report with evidence, offers exactly three options (fix-and-restart, continue-with-caution, abort), and waits for user selection. Explicitly NOT for routine errors or transient errors. Prevents blind retry loops on systemic issues while enabling graceful recovery.

### scope

Drift guard that fires during execution when the agent is about to touch a file or run a command outside the boundaries agreed in recon. Compares the pending action against recon's proposed self-rules and the original task description. On drift, stops, shows the specific action that exceeds scope, and offers three options (proceed with justification, defer to follow-up, revert). Prevents silent scope creep where a small task quietly becomes a large one.

### budget

Context and cost tracking guard that registers a baseline estimate at preflight time and checks actual consumption against it at defined checkpoints during execution. Warns at 75 percent of estimate, stops at 100 percent. Prevents silent context window blowout and runaway token spend where the real cost of a long-running agent session is only discovered after the fact. Complements preflight's one-time estimate by making it enforceable.

## Install

Primary install via the Vercel skills registry:

```bash
npx skills add aradmanamnaoon/agent-guardrails
```

Per-agent installation paths:

| Agent | Path |
|---|---|
| Claude Code | `.claude/skills/` |
| Codex CLI | `.agents/skills/` |
| Cursor | `.cursor/skills/` |
| GitHub Copilot | `.github/skills/` |

Run `npx skills list` to see which path your agent uses.

## Design principles

- **Layered escalation** — not every error triggers hold. Only unhandled failures stop execution; anticipated risks were already priced in during preflight.
- **Estimation as a range** — never a single number. Every cost is expressed as min-max with confidence level and basis.
- **Enforcement of the estimate** — preflight's range becomes an enforceable baseline tracked by budget. The estimate is a contract, not a guess.
- **Scope as a contract** — the original task defines boundaries. Actions outside those boundaries trigger drift detection, not silent expansion.
- **Confirmation gates at each phase** — recon requires explicit confirmation before planning starts; preflight requires it before real runs begin; hold requires choice between recovery options.

## Security

These skills contain **no shell execution**, **no network calls**, and **no credential access**. They are pure Markdown plus one local Python validator (`scripts/validate.py`). The validator itself is auditable in under five minutes: check the frontmatter schema, verify allowed keys (name, description, license), confirm line count limits, and ensure code fences are balanced. No external dependencies beyond PyYAML. No API keys required. No data leaves your machine.

## Status

Early release. Built to be composed. Each skill works independently; together they form a coherent lifecycle. Feedback welcome via GitHub issues. If you find edge cases or have suggestions for additional safeguards, please open an issue or submit a PR.

## License

MIT
