# Plan 4: Step Context Packages

Status: Plan 4 runtime input package contract.

This document records the fourth context optimization step. It is maintainer reference
only and must not be loaded by runtime prompts as execution context.

## Goal

Plan 4 adds the input-side counterpart to Plan 3 short results. `StepResult` and
`ReviewResult` are compact outputs returned from isolated execution contexts; a
`StepContextPackage` is the compact input passed into a step execution context.

The main agent should pass only the package path. The step execution context should read
the referenced files by path and verify hashes as needed, without requiring the main
agent to paste artifact bodies, input document text, or full step instruction bodies into
long-lived context.

## Package Contract

`StepContextPackage` is stored at:

```text
runs/<run_id>/orchestration/context_packages/<stage>/<step>.json
```

Required fields:

```text
kind = step_context_package
schema_version = 1
run_id
stage
step
task_type
created_at
instruction_refs
run_refs
result_paths
constraints
```

`instruction_refs[]` contains repo-relative runtime instruction paths and sha256 hashes.
Allowed instruction refs are limited to:

```text
skills/step-*/SKILL.md
skills/workflow-steps/*/SKILL.md
skills/document-types/**
```

`run_refs[]` contains run-relative artifact paths and sha256 hashes. `task_brief.json`
is always included by the builder; upstream artifacts can be added through `--input-ref`.

`result_paths` declares the expected short result paths:

```text
orchestration/step_results/<step>.json
orchestration/review_results/<stage>/<step>.json
```

`constraints` is fixed:

```text
paths_and_hashes_only = true
no_artifact_body = true
no_inline_instructions = true
```

These files are runtime orchestration metadata. They are not professional artifacts, not
evidence sources, not HITL decisions, and not entries for `manifest.artifacts`.

## Validation

Plan 4 adds `ai_writing_plugin.context_packages` and two CLI commands:

```bash
python -m ai_writing_plugin build-step-context-package --repo-root . --run-dir <run_dir> --stage <stage> --step <step> --task-type <task_type> [--input-ref <path>] [--overwrite]
python -m ai_writing_plugin validate-step-context-package --path <package.json> [--repo-root .] [--run-dir <run_dir>]
```

The validator rejects:

1. Unknown top-level fields, including body-like fields such as `content`, `text`,
   `artifact_body`, `instructions`, and `canonical_text`.
2. Unknown stages or steps.
3. Instruction refs outside runtime prompt surfaces.
4. Run refs outside the run directory boundary.
5. Non-sha256 values or mismatched hashes when roots are supplied.
6. Non-fixed `result_paths` or `constraints`.

When `repo_root` and `run_dir` are supplied, validation also verifies that all referenced
files exist inside the expected boundary and match the declared sha256 hashes.

## Measurement

Plan 4 uses the same measurement command as earlier plans:

```bash
python3 -m ai_writing_plugin.context_metrics --root . --json
```

The generated snapshot is stored at:

```text
docs/maintainers/context_optimization/plan4_metrics.json
```

Comparison against Plan 3:

| Metric | Plan 3 | Plan 4 | Delta |
| --- | ---: | ---: | ---: |
| total_files | 145 | 145 | 0 |
| total_bytes | 843249 | 844101 | +852 |
| estimated_tokens | 141689 | 141854 | +165 |
| command bytes | 13573 | 13902 | +329 |
| workflow_orchestrator bytes | 14071 | 14594 | +523 |

The runtime prompt size rises slightly because the context package protocol is now
explicit. The expected execution-time benefit is that step workers can be launched with a
stable package path instead of large, changing prompt bodies.

## Known Limits

Plan 4 does not create workers, does not dispatch subagents, and does not migrate every
step canonical file. It only establishes the step input package contract and validation
entry points that later plans can use.

Review-specific context packages are intentionally deferred. Plan 5 should add a progress
ledger that records context package paths and short result paths. Plan 6 can then pilot a
single stage using package-path dispatch.

## Verification

Plan 4 is guarded by:

```text
tests/test_context_packages.py
tests/test_short_results.py
tests/test_thin_main_agent_boundary.py
tests/test_runtime_context_boundary.py
tests/test_context_metrics.py
```

The context package tests cover valid packages, package building, optional document type
instruction refs, illegal fields, path boundaries, hash matching, overwrite protection,
and CLI success/failure behavior.
