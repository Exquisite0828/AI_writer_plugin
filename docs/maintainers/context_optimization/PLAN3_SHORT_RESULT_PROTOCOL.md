# Plan 3: Short Result Protocol

Status: Plan 3 runtime result contract.

This document records the third context optimization step. It is maintainer reference
only and must not be loaded by runtime prompts as execution context.

## Goal

Plan 3 turns the Plan 2 compact summary idea into a machine-checkable contract:

1. `StepResult` for step execution outputs.
2. `ReviewResult` for review package outputs.

The main agent should read these short result JSON files instead of carrying full
artifact bodies, review details, source text, or step canonical files in long-lived
context.

## Result Contracts

`StepResult` is stored at:

```text
runs/<run_id>/orchestration/step_results/<step>.json
```

Required fields:

```text
kind = step_result
schema_version = 1
run_id
stage
step
status
artifact_paths
artifact_hashes
summary
blocking_issues_count
next_gate_status
```

`ReviewResult` is stored at:

```text
runs/<run_id>/orchestration/review_results/<stage>/<step>.json
```

Required fields:

```text
kind = review_result
schema_version = 1
run_id
stage
step
status
review_package_paths
review_package_hashes
summary
blocking_issues_count
next_gate_status
```

These files are runtime orchestration metadata. They are not professional artifacts, not
evidence sources, not HITL decisions, and not entries for `manifest.artifacts`.

## Validation

Plan 3 adds `ai_writing_plugin.short_results` and two CLI validators:

```bash
python -m ai_writing_plugin validate-step-result --path <result.json> [--run-dir <run_dir>]
python -m ai_writing_plugin validate-review-result --path <result.json> [--run-dir <run_dir>]
```

The validator rejects:

1. Unknown top-level fields, including body-like fields such as `content`, `text`,
   `artifact_bodies`, and `review_details`.
2. Unknown stages, steps, or statuses.
3. Absolute paths, `..`, backslash separators, `runs/` prefixes, and default-context
   paths under `examples/`, `docs/maintainers/`, or `contracts/`.
4. Non-sha256 or mismatched hash maps.
5. Summaries longer than 600 characters or summaries containing code fences.

When `--run-dir` is supplied, the validator also verifies that each referenced file
exists inside the run directory and matches the declared sha256 hash.

## Measurement

Plan 3 uses the same measurement command as Plan 1 and Plan 2:

```bash
python3 -m ai_writing_plugin.context_metrics --root . --json
```

The generated snapshot is stored at:

```text
docs/maintainers/context_optimization/plan3_metrics.json
```

Comparison against Plan 2:

| Metric | Plan 2 | Plan 3 | Delta |
| --- | ---: | ---: | ---: |
| total_files | 145 | 145 | 0 |
| total_bytes | 842442 | 843249 | +807 |
| estimated_tokens | 141507 | 141689 | +182 |
| command bytes | 13283 | 13573 | +290 |
| workflow_orchestrator bytes | 13554 | 14071 | +517 |

The runtime prompt size rises slightly because the short result protocol is now explicit.
The expected context benefit is execution-time stability: dynamic artifact content should
remain in files, while the main agent receives only fixed-shape result metadata.

## Known Limits

Plan 3 does not create workers, does not dispatch subagents, and does not migrate every
step canonical file. It only establishes the short result contract and validation entry
points that later plans can use.

Plan 4 should define minimal context packages for step execution. Plan 5 should add a
progress ledger that records these short results so resume can avoid replaying all prior
artifact content.

## Verification

Plan 3 is guarded by:

```text
tests/test_short_results.py
tests/test_thin_main_agent_boundary.py
tests/test_runtime_context_boundary.py
tests/test_context_metrics.py
```

The validator tests cover valid StepResult and ReviewResult payloads, illegal fields,
path boundaries, hash matching, `--run-dir` checks, and CLI success/failure behavior.
