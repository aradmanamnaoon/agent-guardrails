# Protocol

How the five skills compose into a coherent agent workflow lifecycle: research → cheap test → cost → execute → recover. Each skill is independently installable, but together they provide layered escalation that stops expensive mistakes before they happen.

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

## State transitions

| Phase | Entry trigger | Exit gate | On abort |
|---|---|---|---|
| recon | non-trivial task start | user confirms | report only |
| preflight | recon confirmed | user proceeds | nothing run |
| scope | file/command outside plan | user picks option | action reverts |
| budget | preflight registered + checkpoints | user continues | pause execution |
| hold | unhandled failure | user picks 1, 2, or 3 | task stops |

## Composition contract

Each skill installs independently via `npx skills add`. When all five are present, they run in the order shown above. When only some are present, each still functions correctly — for example, having only `recon` produces a plan and stops for confirmation without needing any other skill. The composition is what makes the workflow coherent; individual skills are composable building blocks.

This architecture avoids coupling: no skill imports or calls another. Instead, they share a common protocol: produce a report, stop, wait for explicit user direction. That shared pattern is what enables reliable orchestration at the CLI level.

## Error handling

Failures that were anticipated during preflight (listed in residual risks) do not trigger `hold`. They are simply logged and the user decides whether to proceed. Only failures that represent genuinely unhandled problems activate the recovery path. This distinction prevents warning fatigue while surfacing real issues.

The three recovery options offered by `hold` cover all reasonable paths forward: fix-and-restart, continue-with-caution, or abort. None of them auto-correct — the user always makes the final decision.
