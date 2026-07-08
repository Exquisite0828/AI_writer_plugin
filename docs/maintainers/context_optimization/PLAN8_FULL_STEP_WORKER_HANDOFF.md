# Plan 8: Full Step Worker Handoff

Status: Plan 8 full workflow worker handoff protocol.

This document records the eighth context optimization step. It is maintainer reference
only and must not be loaded by runtime prompts as execution context.

## Goal

Plan 8 expands the `StepWorkerDispatch` handoff from the Plan 6 `ingest` pilot to all
13 workflow steps. The main agent now has one consistent step dispatch rule: create a
`StepContextPackage`, create a `StepWorkerDispatch`, pass only the dispatch/context
package path to the isolated step execution context, then read short result metadata.

This is not a real Python launcher for Claude/Codex subagents. It does not generate
professional artifacts and does not change the artifact contract. It only removes the
runtime prompt and validator escape hatch where non-`ingest` steps were not yet part of
the worker handoff protocol.

## Workflow Topology

`StepWorkerDispatch` now accepts exactly these stage-step pairs:

```text
ingest:
  step-input-materials
  step-material-inventory
  step-source-index
outline:
  step-template-outline
evidence_planning:
  step-research-questions
  step-evidence-map
draft:
  step-conservative-draft
review:
  step-review
  step-verification
finalize:
  step-revision
  step-final-report
learning:
  step-run-summary
  step-candidate-profile-update
```

Valid stages and valid steps are not enough by themselves. The pair must match the fixed
workflow topology. For example, `ingest/step-final-report` fails closed.

## Dispatch Contract

The JSON schema is unchanged from Plan 6:

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

Refs still use:

```text
path
sha256
```

`constraints` remains fixed:

```text
package_path_only = true
worker_reads_refs = true
main_agent_reads_short_results_only = true
no_artifact_body = true
```

The canonical dispatch path is unchanged:

```text
runs/<run_id>/orchestration/worker_dispatches/<stage>/<step>.json
```

## Runtime Boundary

Runtime prompts now describe a single rule:

```text
全 13 step worker handoff
```

Every step is dispatched through `StepWorkerDispatch`. The main agent does not keep a
separate non-worker route for later stages. It still must not paste artifact bodies,
bulk-read canonical step files, or bring dynamic artifact/review/input material bodies
back into long-lived context.

Plan 7 review and gate protocols remain in force:

```text
ReviewContextPackage
StageGateResult
ProgressLedger
StepResult
ReviewResult
```

## Measurement

Plan 8 uses the same measurement command as earlier plans:

```bash
python3 -m ai_writing_plugin.context_metrics --root . --json
```

The generated snapshot is stored at:

```text
docs/maintainers/context_optimization/plan8_metrics.json
```

Comparison against Plan 7:

| Metric | Plan 7 | Plan 8 | Delta |
| --- | ---: | ---: | ---: |
| total_files | 145 | 145 | 0 |
| total_bytes | 849009 | 848349 | -660 |
| estimated_tokens | 142788 | 142659 | -129 |
| command bytes | 16141 | 15743 | -398 |
| workflow_orchestrator bytes | 17263 | 17001 | -262 |

The prompt shrinks slightly because pilot caveats are removed. The more important
execution-time effect is behavioral: every step has the same path-only worker handoff,
so main-agent context no longer grows by carrying non-`ingest` step execution details.

## Known Limits

Plan 8 still does not start a real subagent from Python. The runtime host must provide
the independent step execution context.

Plan 8 does not generate professional content, perform review/verification judgment, or
change `contracts/CURRENT_ARTIFACT_CONTRACTS.md`.

## Verification

Plan 8 is guarded by:

```text
tests/test_step_worker_dispatch.py
tests/test_progress_ledger.py
tests/test_context_packages.py
tests/test_short_results.py
tests/test_review_context_packages.py
tests/test_stage_gate_results.py
tests/test_thin_main_agent_boundary.py
tests/test_runtime_context_boundary.py
tests/test_context_metrics.py
```

The dispatch tests cover all 13 legal stage-step pairs, stage-step mismatch rejection,
CLI success/failure behavior, delegated package/ledger validation, path boundaries,
hash matching, and body-field rejection.
