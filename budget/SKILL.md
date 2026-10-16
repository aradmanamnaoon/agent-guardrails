---
name: budget
description: Advisory budget checkpoint skill for agents. Records a baseline estimate, compares observed usage when metrics exist, requests a warning at 75 percent, and instructs the agent to pause at 100 percent. Does not implement runtime metering or enforce token, time, or spending limits.
license: MIT
---

# Budget

Preflight estimates the cost. Budget asks the host agent to compare observed usage and pause at thresholds. This Markdown skill is not a runtime meter or hard spending limit; use external platform limits for enforcement.

## When this runs

Two trigger points:

1. Registration - when preflight is confirmed, register the estimate as the baseline. The baseline is: tokens (min-max), time (min-max), money (min-max), and the estimate's confidence level.

2. Checkpoints - at each of the following moments during execution, compare actual against baseline:
   - After every major step in the plan
   - Before any operation the agent expects to cost more than 10 percent of the baseline
   - When the user asks "how are we doing"
   - On any error that might indicate wasted work

## Procedure

### 1. Register the baseline

When preflight is confirmed, store the estimate. Record:
- Token range from the preflight report
- Time range from the preflight report
- Money range from the preflight report
- Confidence level (high / medium / low)

### 2. Check at each checkpoint

Compare actual consumption against the baseline. Compute:
- Percentage of upper bound consumed
- Trajectory: on pace, faster, or slower than expected
- Confidence drift: is the original confidence level still valid?

### 3. Warn at 75 percent

When consumption reaches 75 percent of the upper bound, produce this report. Do not stop - just warn.

Output exactly this template wrapped in a markdown code block. Make absolutely sure the closing fence is on its own line:

```markdown
## Budget Warning

### Baseline (from preflight)
- Tokens: [min]-[max]
- Time: [min]-[max] minutes
- Cost: $[min]-$[max]

### Current consumption
- Tokens used: [measured value, or UNKNOWN if unavailable]
- Time elapsed: [measured value, or UNKNOWN if unavailable]
- Cost accrued: [measured value, or UNKNOWN if unavailable]
- Percentage of upper bound: [X]% (or UNKNOWN when usage is unavailable)

### Trajectory
- Pace: [on track / faster / slower] than expected
- Projected final: [min]-[max]

### Recommendation
[One of: continue, checkpoint with user, reduce scope]

### Awaiting confirmation
Reply "continue" or "pause".
```

### 4. Stop at 100 percent

When consumption reaches 100 percent of the upper bound, stop and escalate using hold. The budget is exhausted. Do not continue without explicit user approval for additional budget.

### 5. Update the baseline if user approves more

If the user approves additional budget, update the baseline to reflect the new range and continue.

## Rules for this skill

- If actual token/time/money usage is unavailable, write UNKNOWN. Never guess a measured consumption percentage or claim a threshold was enforced.
- This is an instruction for a cooperating agent, not a guarantee that tools or billing will stop. For hard caps, use host/platform limits.

- Only check at defined checkpoints. Do not check after every action - that creates noise.
- Always report against the upper bound, not the lower. Budget safety uses worst-case.
- If confidence in the original estimate was low, check more frequently.
- The 75 percent warning is a warning, not a stop. The 100 percent threshold is the stop.
- If the user approves more budget, reset the baseline - do not keep accumulating against the original.

## Common mistakes

- Warning at every checkpoint. Warnings are only for the 75 percent threshold.
- Stopping at 75 percent. That is a warning, not a stop.
- Comparing against the lower bound instead of the upper. Budget safety uses the upper bound.
- Continuing past 100 percent without user approval. The budget is a contract.
- Failing to update the baseline after user approval. Reset, do not accumulate.
