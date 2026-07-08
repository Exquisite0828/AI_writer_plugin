# Plan 6: Ingest Worker Pilot

Status: Plan 6 runtime worker dispatch pilot.

This document records the sixth context optimization step. It is maintainer reference
only and must not be loaded by runtime prompts as execution context.

## Goal

Plan 6 connects the compact handoff pieces from Plans 2-5 into a testable pilot path for
the `ingest` stage only. The main agent prepares a dispatch file, passes only the
dispatch/context package path to an isolated step execution context, and records compact
results back into the progress ledger.

This is not a full worker implementation. Python does not launch Claude/Codex subagents,
does not generate professional artifacts, and does not migrate all 13 workflow steps.

## Dispatch Contract

`StepWorkerDispatch` is stored at:

```text
runs/<run_id>/orchestration/worker_dispatches/<stage>/<step>.json
```

Required fields:

```text
kind = step_worker_dispatch
schema_version = 1
run_id
stage
step
created_at
context_package_ref
progress_ledger_ref
result_paths
constraints
```

Refs use the fixed structure:

```text
path
sha256
```

`constraints` is fixed:

```text
package_path_only = true
worker_reads_refs = true
main_agent_reads_short_results_only = true
no_artifact_body = true
```

Plan 6 deliberately allows only this pilot scope:

```text
stage = ingest
step = step-input-materials | step-material-inventory | step-source-index
```

All other stages and steps fail closed so runtime prompts and tests do not imply that
the whole workflow has been migrated to workers.

## CLI

Plan 6 adds `ai_writing_plugin.step_worker_dispatch` and three CLI commands:

```bash
python -m ai_writing_plugin prepare-step-worker-dispatch --repo-root . --run-dir <run_dir> --stage ingest --step <step> --task-type <task_type> [--input-ref <path>] [--overwrite-package] [--overwrite-dispatch]
python -m ai_writing_plugin complete-step-worker-dispatch --run-dir <run_dir> --stage ingest --step <step> --step-result <path> [--review-result <path>] [--status <status>]
python -m ai_writing_plugin validate-step-worker-dispatch --path <dispatch.json> [--repo-root .] [--run-dir <run_dir>]
```

`prepare-step-worker-dispatch` requires an existing `ProgressLedger`, creates or reuses
the `StepContextPackage`, writes the dispatch file, and records the ledger entry as
`context_ready`.

`complete-step-worker-dispatch` validates the `StepResult` and optional `ReviewResult`,
then records their path/hash refs in the ledger. If no explicit `--status` is supplied,
the review result status wins when present; otherwise the step result status is used.

## Validation

The dispatch validator rejects:

1. Unknown fields, including body-like fields such as `content`, `text`, `artifact_body`,
   `result_body`, `package_body`, and `instructions`.
2. Any stage or step outside the `ingest` pilot scope.
3. Ref paths outside the run directory boundary.
4. Non-sha256 values or mismatched hashes when `run_dir` is supplied.
5. Non-fixed `result_paths` or `constraints`.

When roots are supplied, validation delegates:

```text
context_package_ref -> validate_step_context_package(..., repo_root=..., run_dir=...)
progress_ledger_ref -> validate_progress_ledger(..., run_dir=...)
```

This keeps the worker handoff compact and stable. The dispatch file points to a package
and ledger; it never inlines instruction bodies, artifact bodies, input material text, or
review details.

## Measurement

Plan 6 uses the same measurement command as earlier plans:

```bash
python3 -m ai_writing_plugin.context_metrics --root . --json
```

The generated snapshot is stored at:

```text
docs/maintainers/context_optimization/plan6_metrics.json
```

Comparison against Plan 5:

| Metric | Plan 5 | Plan 6 | Delta |
| --- | ---: | ---: | ---: |
| total_files | 145 | 145 | 0 |
| total_bytes | 845440 | 846873 | +1433 |
| estimated_tokens | 142082 | 142377 | +295 |
| command bytes | 14531 | 15317 | +786 |
| workflow_orchestrator bytes | 15304 | 15951 | +647 |

The runtime prompt size rises slightly because the pilot boundary and dispatch path are
now explicit. The expected execution-time benefit is that the first stage has a concrete,
testable package-path worker handoff instead of routing every step through the main
agent's long-lived context.

## Known Limits

Plan 6 does not implement real subagent launching. It establishes a deterministic local
protocol that future runtime orchestration can call.

Review-specific context packages, stage review gate merging, and full migration of all
13 workflow steps remain deferred to later plans.

## Verification

Plan 6 is guarded by:

```text
tests/test_step_worker_dispatch.py
tests/test_progress_ledger.py
tests/test_context_packages.py
tests/test_short_results.py
tests/test_thin_main_agent_boundary.py
tests/test_runtime_context_boundary.py
tests/test_context_metrics.py
```

The worker dispatch tests cover prepare, package reuse, missing ledger failure,
completion, pilot scope enforcement, illegal fields, path boundaries, hash matching,
delegated validation, and CLI success/failure behavior.
