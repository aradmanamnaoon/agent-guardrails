---
name: preflight
description: Cheap verification and cost estimation gate before expensive, long-running, or irreversible operations. Identifies the cheapest verifiable version of the target operation, runs it, reports any bugs without stopping, estimates cost as a range (never a point value), lists residual risks using probability x impact columns, and stops for user confirmation before the real run begins. Use when about to train a model, batch process, loop over production data, or perform any operation that cannot be cleanly undone.
license: MIT
---

# Preflight

Before spending real resources, spend almost none. This skill verifies your plan with the cheapest possible test, estimates real costs as ranges, and stops for your go-ahead before starting anything expensive.

## When this runs

This skill activates on ANY of these triggers:

- Training, batch processing, or loops over more than ~100 items
- API calls that cost money or have rate limits
- Operations that write to production, cloud services, or shared storage
- Any command the user describes as "expensive", "long", or "risky"

State explicitly: this skill runs after recon is confirmed and before the real run begins.

## Procedure

### 1. Identify the cheapest version

Find the minimal verifiable proxy for your intended operation:

| Real operation | Cheap version |
|---|---|
| Train on 10,000 samples | Train on 10 samples, 1 epoch |
| Loop over all users | Loop over the first 3 users |
| Process 500 files | Process the first file |
| Call an API 1,000 times | Call it once, print the response |
| Database migration | Run against a copied schema |
| Full integration test suite | Run one unit test that exercises the same code path |

### 2. Run the cheap version

Execute it. Do not ask for permission - the whole point is that it is cheap.

Record:
- Exact command
- Input used
- Outcome (pass/fail)
- Wall time
- Any error messages

### 3. Report bugs, do not stop

If the cheap version fails, note the failure and continue to the estimate. The failure is information for the report, not a reason to halt. The user decides whether to halt.

Exception: if the cheap version fails in a way that makes the real run impossible (missing dependency, invalid credentials), say so and stop.

### 4. Estimate the real cost

Produce a RANGE, never a single number. Include:
- Tokens (if LLM calls are involved)
- Time (wall clock)
- Money (if any paid service is involved)
- Confidence level: high / medium / low
- Basis: how you derived the estimate

Bad example: "This will cost $5."
Good example: "$3-$8, based on a 10-sample run extrapolated 1,000x. Confidence: medium - the cost per sample may not be linear."

### 5. List residual risks

Only list risks the cheap test could not rule out. If the cheap test passed and ruled something out, do not mention it here.

Use this table format:

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Rate limit at 500 calls | Medium | Run pauses | Exponential backoff |
| OOM at batch 64 | Low | Full restart | Reduce to batch 16 |

If there are no residual risks, write: "None identified."

### 6. Produce the report

Output exactly this template wrapped in a markdown code block. Make absolutely sure the closing fence is on its own line:

```markdown
## Preflight Report

### Cheap test
- Command: [exact command]
- Input: [what was used]
- Outcome: passed / failed - [error if failed]
- Duration: [X seconds]

### Cost estimate (real run)
- Tokens: ~[min]-[max]
- Time: ~[min]-[max] minutes
- Cost: ~$[min]-$[max]
- Confidence: [high / medium / low]
- Basis: [how you derived it]

### Residual risks
[table or "None identified"]

### Awaiting confirmation
Reply "proceed" or "abort".
```

### 7. Stop

Wait for the user. Do not start the real run.

## Rules for this skill

- Always run the cheap version. Never skip to the estimate without it.
- Always produce a range for cost, never a point estimate.
- If the user replies "proceed", execute the real run.
- If the user replies "abort", stop and summarise what was not done.
- If the user replies anything else, treat it as a request to revise the preflight report.

## Common mistakes

- Skipping the cheap test and going straight to the cost estimate. The cheap test is the evidence base for everything else.
- Giving a point estimate instead of a range. Every cost is a range, even when the range is narrow.
- Listing residual risks that the cheap test already ruled out. That section is only for what remains unknown.
- Proceeding without waiting for user confirmation. The stop is mandatory.
- Treating "abort" as a reason to explain the plan again. Abort means stop.
