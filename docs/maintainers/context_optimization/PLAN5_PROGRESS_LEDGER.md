# Plan 5: Progress Ledger

Status: Plan 5 runtime progress ledger contract.

This document records the fifth context optimization step. It is maintainer reference
only and must not be loaded by runtime prompts as execution context.

## Goal

Plan 5 adds a compact `ProgressLedger` so the main agent can resume or continue a run
without replaying historical artifacts, context packages, step results, or review
results.

The main agent should read one short ledger first, use it to decide the next step, and
open an individual package/result file only when that specific step needs to continue,
be verified, or be diagnosed.

## Ledger Contract

`ProgressLedger` is stored at:

```text
runs/<run_id>/orchestration/progress_ledger.json
```

Required top-level fields:

```text
kind = progress_ledger
schema_version = 1
run_id
created_at
updated_at
entries
```

Each `entries[]` item records only:

```text
stage
step
status
updated_at
context_package_ref
step_result_ref
review_result_ref
blocking_issues_count
next_gate_status
```

Refs use the fixed structure:

```text
path
sha256
```

Paths are run-relative POSIX paths. CLI inputs may be run-relative paths or absolute
paths inside the run directory, but the stored ledger always normalizes them to
run-relative paths.

Allowed ledger statuses:

```text
not_started
context_ready
running
done
needs_revision
blocked
skipped
```

The ledger is runtime orchestration metadata. It is not a professional artifact, not an
evidence source, not a HITL decision, and not an entry for `manifest.artifacts`.

## Validation

Plan 5 adds `ai_writing_plugin.progress_ledger` and three CLI commands:

```bash
python -m ai_writing_plugin init-progress-ledger --run-dir <run_dir> [--overwrite]
python -m ai_writing_plugin record-step-progress --run-dir <run_dir> --stage <stage> --step <step> --status <status> [--context-package <path>] [--step-result <path>] [--review-result <path>]
python -m ai_writing_plugin validate-progress-ledger --path <ledger.json> [--run-dir <run_dir>]
```

The validator rejects:

1. Unknown top-level or entry fields, including body-like fields such as `content`,
   `text`, `artifact_body`, `result_body`, `package_body`, and `instructions`.
2. Unknown stages or steps.
3. Status values outside the ledger status enum.
4. Duplicate entries for the same `(stage, step)` pair.
5. Ref paths outside the run directory boundary.
6. Non-sha256 values or mismatched hashes when `run_dir` is supplied.

When `run_dir` is supplied, validation also delegates referenced files to the Plan 4 and
Plan 3 validators:

```text
context_package_ref -> validate_step_context_package(..., run_dir=...)
step_result_ref     -> validate_step_result(..., run_dir=...)
review_result_ref   -> validate_review_result(..., run_dir=...)
```

This keeps the ledger narrow: it records where short metadata lives and proves integrity
with hashes, but it does not inline package bodies, result bodies, artifact bodies, or
instruction bodies.

## Measurement

Plan 5 uses the same measurement command as earlier plans:

```bash
python3 -m ai_writing_plugin.context_metrics --root . --json
```

The generated snapshot is stored at:

```text
docs/maintainers/context_optimization/plan5_metrics.json
```

Comparison against Plan 4:

| Metric | Plan 4 | Plan 5 | Delta |
| --- | ---: | ---: | ---: |
| total_files | 145 | 145 | 0 |
| total_bytes | 844101 | 845440 | +1339 |
| estimated_tokens | 141854 | 142082 | +228 |
| command bytes | 13902 | 14531 | +629 |
| workflow_orchestrator bytes | 14594 | 15304 | +710 |

The runtime prompt size rises slightly because the resume protocol is now explicit. The
expected execution-time benefit is lower dynamic context growth: resume and continuation
can start from one stable ledger instead of re-reading or re-summarizing every historical
package/result.

## Known Limits

Plan 5 does not create workers, does not dispatch subagents, and does not migrate every
step canonical file. It only establishes the progress ledger contract and validation
entry points that later plans can use.

Stage review gate merging is not finalized here. The ledger records short progress state,
short result refs, blocking issue counts, and next gate status; the gate decision remains
the existing `stage_reviews/<stage>/decision.json` responsibility.

Plan 6 can now pilot a worker path using three stable handoff files:

```text
ProgressLedger
StepContextPackage
StepResult / ReviewResult
```

## Verification

Plan 5 is guarded by:

```text
tests/test_progress_ledger.py
tests/test_context_packages.py
tests/test_short_results.py
tests/test_thin_main_agent_boundary.py
tests/test_runtime_context_boundary.py
tests/test_context_metrics.py
```

The progress ledger tests cover initialization, overwrite protection, entry upsert,
run-relative ref normalization, illegal fields, path boundaries, duplicate entries, hash
matching, delegated Plan 3/4 validation, and CLI success/failure behavior.
