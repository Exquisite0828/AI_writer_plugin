# Plan 2: Thin Main Agent Boundary

Status: Plan 2 runtime boundary update.

This document records the second context optimization step. It is maintainer reference
only and must not be loaded by runtime prompts as execution context.

## Goal

Plan 2 changes the top-level runtime prompt contract from "main agent executes every
workflow step" to "main agent acts as a thin controller".

The thin controller keeps only stable orchestration state in long-lived context:

1. Stage and step ordering.
2. Paths and hashes.
3. Compact step summaries.
4. HITL gate state.
5. Blocking counts and next gate status.

It must not carry full artifact bodies, full review details, input document text, or
bulk-loaded step canonical files in the long-lived main context.

## Runtime Boundary Change

Plan 2 updates only the top-level runtime surfaces:

```text
commands/write.md
skills/workflow-orchestrator/SKILL.md
```

The new runtime language says that each step artifact is produced by an independent
`step execution context`. The main agent receives only a compact summary with:

```text
step
stage
status
artifact_paths
artifact_hashes
review_package_paths
blocking_issues_count
next_gate_status
```

This is a prompt/runtime boundary change only. Plan 2 does not add a Python `StepResult`
schema, does not implement worker/subagent dispatch, and does not change artifact
contracts.

## Measurement

Plan 2 uses the same measurement command as Plan 1:

```bash
python3 -m ai_writing_plugin.context_metrics --root . --json
```

The generated snapshot is stored at:

```text
docs/maintainers/context_optimization/plan2_metrics.json
```

Comparison against Plan 1:

| Metric | Plan 1 | Plan 2 | Delta |
| --- | ---: | ---: | ---: |
| total_files | 145 | 145 | 0 |
| total_bytes | 840995 | 842442 | +1447 |
| estimated_tokens | 141262 | 141507 | +245 |
| command bytes | 12706 | 13283 | +577 |
| workflow_orchestrator bytes | 12684 | 13554 | +870 |

The runtime markdown size rises slightly because Plan 2 adds explicit context hygiene
rules. That is acceptable for this plan: the target is lower main-context growth during
execution, not immediate runtime prompt byte reduction.

## Expected Cache Impact

Plan 2 alone does not guarantee provider cache hits. Its value is to make later plans
cacheable by keeping the main prompt prefix more stable:

1. Stable orchestration text remains in the main context.
2. Dynamic artifact content stays in files under `runs/<run_id>/`.
3. Step-specific instructions move toward isolated execution contexts.
4. The main agent receives paths, hashes, and compact status instead of changing bodies.

Plan 3 should turn the compact summary into a machine-checkable result contract. Plan 4
should define minimal context packages for step execution. Plan 5 should add a progress
ledger so the main agent can resume without replaying all prior artifacts.

## Known Limits

Plan 2 intentionally does not rewrite every workflow step canonical file. Some step
canonical files still use older "main execution context" wording and will need migration
when the worker protocol is introduced.

Plan 2 also does not change deterministic Python behavior. The current CLI remains
limited to the existing engine entry points; full worker dispatch belongs to later plans.

## Verification

Plan 2 is guarded by:

```text
tests/test_thin_main_agent_boundary.py
tests/test_runtime_context_boundary.py
tests/test_context_metrics.py
```

The new thin-boundary test protects the top-level command and orchestrator from
regressing to direct main-agent artifact production.
