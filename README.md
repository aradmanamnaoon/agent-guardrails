# Agent Guardrails

Five portable **Markdown-based agent workflow skills** for research, preflight checks, scope review, budget reporting, and failure recovery. They *request* human review and pauses; they do not technically enforce tool permissions, budgets, or security boundaries.

## The problem

AI coding agents fail expensively not because the model is weak but because the workflow has no gates. Agents write code, run commands, and make changes without stopping to ask: did I do enough homework? Is this really safe? How much will this actually cost? Scope creep turns small tasks into large refactors overnight. Cost overruns go undetected until tokens are burned or bills arrive. Unrecoverable failures leave systems broken with no path back. These three failure modes — scope creep, cost overruns, unrecoverable failures — are the norm for agentic workflows today.

## The fix

Five skills compose into a suggested lifecycle: **recon** (research and propose self-rules), **preflight** (cheap verification and cost estimates), **hold** (request recovery decisions), **scope** (flag possible drift), and **budget** (report estimated/observed consumption when measurable). Each installs independently via `npx skills add`. Compliance depends on the host agent; no tool call is blocked by this repository alone.

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
- **Budget checkpoints are advisory** — preflight's range becomes a baseline for the agent to compare with observed usage **if usage data is available**. The skill cannot meter costs or force a runtime halt.
- **Scope as a contract** — the original task defines boundaries. Actions outside those boundaries trigger drift detection, not silent expansion.
- **Confirmation gates at each phase** — recon requires explicit confirmation before planning starts; preflight requires it before real runs begin; hold requires choice between recovery options.

## Security

The skill definitions are Markdown instructions plus a local format validator (`scripts/validate.py`, requiring PyYAML). The repository's Markdown does not itself implement sandboxing, network isolation, credential control, authenticated approval, or runtime cost limits. Installing through `npx`, using an AI model, or connecting tools may involve network requests and data sharing under their own settings. Review the [trust boundaries and evaluation protocol](docs/BOUNDARIES_AND_EVALUATION.md) before relying on these instructions.

## Status

Early release. Built to be composed. Each skill works independently; together they form a coherent lifecycle. Feedback welcome via GitHub issues. If you find edge cases or have suggestions for additional safeguards, please open an issue or submit a PR.

## License

MIT
