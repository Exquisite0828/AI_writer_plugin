# Plan 7: Review Gate Short Protocol

Status: Plan 7 review gate context optimization protocol.

This document records the seventh context optimization step. It is maintainer reference
only and must not be loaded by runtime prompts as execution context.

## Goal

Plan 7 closes the remaining review/gate context gap after the ingest worker pilot.
Review subagents receive a compact `ReviewContextPackage` instead of main-agent pasted
review material, and stage gates produce a compact `StageGateResult` instead of requiring
the main agent to replay `issues.json`, `review_units.json`, or full decision details
when resuming a run.

This does not implement professional review content, does not launch real subagents, and
does not change the public artifact contract. It only fixes the path/hash/status protocol
needed for later orchestration.

## ReviewContextPackage

`ReviewContextPackage` is stored at:

```text
runs/<run_id>/orchestration/review_context_packages/<stage>.json
```

Required fields:

```text
kind = review_context_package
schema_version = 1
run_id
stage
steps
created_at
step_result_refs
stage_review_refs
result_paths
constraints
```

Refs use the fixed structure:

```text
path
sha256
```

`step_result_refs` must match the package `steps` exactly and point to:

```text
orchestration/step_results/<step>.json
```

`stage_review_refs` may only include existing files from this allowlist:

```text
stage_reviews/<stage>/review_prompt.md
stage_reviews/<stage>/review_units.json
stage_reviews/<stage>/issues_schema.json
stage_reviews/<stage>/review_context.json
```

`issues.json` is deliberately not part of `ReviewContextPackage`. It remains a review
output and may be opened only when the user needs issue details.

`constraints` is fixed:

```text
paths_and_hashes_only = true
no_artifact_body = true
no_inline_review_details = true
main_agent_passes_package_path_only = true
```

## StageGateResult

`StageGateResult` is stored at:

```text
runs/<run_id>/orchestration/stage_gate_results/<stage>.json
```

Required fields:

```text
kind = stage_gate_result
schema_version = 1
run_id
stage
status
decision_ref
review_result_refs
summary
blocking_issues_count
next_gate_status
created_at
```

Allowed `status` values:

```text
accepted
needs_revision
blocked
skipped
pending_user_confirmation
```

`accepted` and `skipped` map to:

```text
next_gate_status = can_continue
```

The other statuses map to their own blocking state:

```text
needs_revision
blocked
pending_user_confirmation
```

`decision_ref` points to the original runtime gate decision when it exists:

```text
stage_reviews/<stage>/decision.json
```

The decision remains the raw stage review gate record. `StageGateResult` is only a short
summary and path/hash index for recovery and continuation.

## CLI

Plan 7 adds `ai_writing_plugin.review_context_packages`,
`ai_writing_plugin.stage_gate_results`, and four CLI commands:

```bash
python -m ai_writing_plugin build-review-context-package --repo-root . --run-dir <run_dir> --stage <stage> --step <step> [--step <step> ...] [--overwrite]
python -m ai_writing_plugin validate-review-context-package --path <package.json> [--repo-root .] [--run-dir <run_dir>]
python -m ai_writing_plugin build-stage-gate-result --run-dir <run_dir> --stage <stage> [--decision <path>] [--review-result <path> ...] [--status <status>]
python -m ai_writing_plugin validate-stage-gate-result --path <result.json> [--run-dir <run_dir>]
```

Validation fails closed on:

1. Unknown fields, including body-like fields such as `content`, `text`,
   `artifact_body`, `review_units_body`, `issues_body`, and `decision_body`.
2. Invalid stage, step, or gate status values.
3. Absolute paths, `..`, backslashes, `runs/` prefixes, and paths outside the run-result
   boundary.
4. Non-sha256 values or mismatched hashes when `run_dir` is supplied.
5. StepResult or ReviewResult refs whose delegated short-result validation fails.

## Runtime Boundary

The runtime prompts now state:

1. Generate `ReviewContextPackage` before dispatching review subagents.
2. Pass only the package path to review subagents.
3. Write `StageGateResult` after a stage gate decision.
4. Resume or continue from `ProgressLedger` plus `StageGateResult`.
5. Do not replay `issues.json` or `review_units.json` bodies by default.

The main agent may still open a single issue file on demand when presenting concrete
blocking details to the user. The default recovery path stays compact and stable.

## Measurement

Plan 7 uses the same measurement command as earlier plans:

```bash
python3 -m ai_writing_plugin.context_metrics --root . --json
```

The generated snapshot is stored at:

```text
docs/maintainers/context_optimization/plan7_metrics.json
```

Comparison against Plan 6:

| Metric | Plan 6 | Plan 7 | Delta |
| --- | ---: | ---: | ---: |
| total_files | 145 | 145 | 0 |
| total_bytes | 846873 | 849009 | +2136 |
| estimated_tokens | 142377 | 142788 | +411 |
| command bytes | 15317 | 16141 | +824 |
| workflow_orchestrator bytes | 15951 | 17263 | +1312 |

The runtime prompt size increases slightly because the review/gate handoff is now
explicit. The intended execution-time benefit is lower dynamic context growth: recovery
can use `ProgressLedger` and `StageGateResult` instead of replaying review package bodies.

## Known Limits

Plan 7 does not validate the full historical stage-review decision contract and does not
replace `validate-stage-review` or `record-stage-review-decision`.

Plan 7 does not generate professional review content. `issues.json`, `review_units.json`,
and `decision.json` remain runtime files under `runs/<run_id>/stage_reviews/<stage>/`.

Full review worker migration and all-step worker dispatch remain deferred.

## Verification

Plan 7 is guarded by:

```text
tests/test_review_context_packages.py
tests/test_stage_gate_results.py
tests/test_step_worker_dispatch.py
tests/test_progress_ledger.py
tests/test_context_packages.py
tests/test_short_results.py
tests/test_thin_main_agent_boundary.py
tests/test_runtime_context_boundary.py
tests/test_context_metrics.py
```

The new tests cover package/result builders, validators, CLI success/failure behavior,
body-field rejection, path-boundary enforcement, hash checking, and delegated short-result
validation.
