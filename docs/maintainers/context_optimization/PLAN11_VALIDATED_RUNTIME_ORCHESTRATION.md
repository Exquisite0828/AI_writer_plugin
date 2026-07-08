# Plan 11: Validated Runtime Orchestration Metadata

Status: Plan 11 runtime metadata validation boundary.

This document records the eleventh context optimization step. It is maintainer reference
only and must not be loaded by runtime prompts as execution context.

## Goal

Plan 10 real validation showed the main workflow could create real step/review sidechain
workers and obey document-type lazy routing. It also exposed a separate drift problem:
some runtime orchestration JSON files were still hand-written by the agent and did not
match the Python validators.

Plan 11 closes that gap. Runtime orchestration metadata must be produced by
`python -m ai_writing_plugin` builder commands and validated before the next action. If a
validator fails, the workflow must fail closed with `metadata_invalid`.

## Runtime Rule

The runtime prompt now forbids:

```text
hand-written orchestration JSON
manual ProgressLedger patching
continuing after validator failure
StepResult status = completed
```

The required command boundary is:

```text
init-progress-ledger
prepare-step-worker-dispatch
validate-step-context-package
validate-step-worker-dispatch
validate-progress-ledger
validate-step-result
complete-step-worker-dispatch
build-review-context-package
validate-review-context-package
validate-review-result
build-stage-gate-result
validate-stage-gate-result
```

Step results must use one of the validator-supported statuses:

```text
done | needs_revision | blocked | skipped
```

## ReviewContextPackage v2

`ReviewContextPackage` is now `schema_version=2`.

It adds:

```text
context_package_refs[]
```

The refs are ordered exactly like `steps[]` and point to:

```text
orchestration/context_packages/<stage>/<step>.json
```

Validators check that every referenced StepContextPackage:

```text
exists
has a matching sha256
is valid against StepContextPackage schema
matches run_id, stage, and step
```

This removes the need for the main agent to hand-write fields such as
`canonical_step`, `document_type_root`, `document_type_step`, or `writing_core` into a
review package. Review workers can open the referenced StepContextPackage and then read
only the path/hash refs already present there.

## Measurement

Plan 11 metrics are generated with:

```bash
python3 -m ai_writing_plugin.context_metrics --root . --json
```

Current snapshot:

```text
runtime prompt files: 145
runtime prompt bytes: 858,593
estimated tokens: 144,604
```

The prompt-size increase is intentional and small. The purpose of Plan 11 is behavioral:
prevent runtime metadata drift from forcing future resume/continue flows to reread
artifacts, canonical step bodies, or review detail bodies.

## Real Validation Target

After implementation, run one controlled workflow with
`examples/hara_minimal_fixture/task.yaml`. The run may stop at the budget limit, but every
metadata file created before budget stop must validate:

```text
ProgressLedger
StepWorkerDispatch
StepContextPackage
StepResult
ReviewContextPackage
ReviewResult, if produced
```

If all produced metadata validates before budget stop, record the result as:

```text
validated_until_budget_stop
```

Do not claim all 13 steps have completed unless the run actually reaches the final stage.

## Real Validation Result

Plan 11 validation first exposed two remaining real-runtime drifts:

```text
1. The workflow used Agent sidechain workers, but the first StepResult contained extra
   fields such as task_type, knowledge_gaps_count, completed_at, and revision_required.
2. A ProgressLedger entry was later observed without the required step_result_ref.sha256.
```

The runtime prompts were tightened so the worker prompt must include the full
StepResult/ReviewResult field lists, forbid unknown result fields, and require each
worker to run the relevant validator before returning.

The final controlled run stopped after the first step worker by design:

```text
run_id: hara-20260708T204735Z
session_id: 8225a2d5-c4c3-4bfb-807e-679dac8e2456
scope: first step worker only; no review worker, no stage gate
```

Independent validator checks passed for:

```text
ProgressLedger
StepWorkerDispatch
StepContextPackage
StepResult
```

Session log observations:

```text
main tools: Agent=1, Bash=14, Read=6, Write/Edit=0
main document-type reads: none
worker document-type reads: skills/document-types/hara/SKILL.md
worker document-type reads: skills/document-types/hara/steps/step-input-materials.md
sibling document-type reads: none observed
main max effective context: 59,232 tokens
worker max effective context: 47,526 tokens
main cache read ratio: 0.9410
worker cache read ratio: 0.9178
```

This is recorded as:

```text
validated_until_first_step_worker_stop
```

It proves the Plan 11 metadata path can run with a real Agent worker and strict
validators for the first handoff. It does not prove all 13 workflow steps or review gate
workers have completed end to end.

## Known Limits

Plan 11 does not implement a Python LLM launcher and does not physically split
document-type skills out of the plugin runtime surface. If a host injects all skills into
the first model call, follow-up work should address physical document-type lazy loading.

Plan 11 also does not modify `contracts/CURRENT_ARTIFACT_CONTRACTS.md`; orchestration
metadata is runtime control state, not product artifact contract.

## Verification

Plan 11 is guarded by:

```text
tests/test_runtime_metadata_cli_contract.py
tests/test_review_context_packages.py
tests/test_thin_main_agent_boundary.py
```

The full protocol regression set also includes:

```text
tests/test_step_worker_dispatch.py
tests/test_progress_ledger.py
tests/test_context_packages.py
tests/test_short_results.py
tests/test_stage_gate_results.py
tests/test_runtime_context_boundary.py
tests/test_context_metrics.py
```
