# Plan 9: Real Worker Handoff Boundary

Status: Plan 9 runtime worker/subagent handoff boundary.

This document records the ninth context optimization step. It is maintainer reference
only and must not be loaded by runtime prompts as execution context.

## Goal

Plan 9 closes the gap found during real CLI validation after Plan 8: the repository had
`StepWorkerDispatch`, `StepContextPackage`, and short result protocols, but the observed
Claude session did not show a real `Task`/subagent tool call. That meant the main agent
could still perform step work itself even though the protocol files existed.

Plan 9 makes the runtime prompt fail closed. Step and review work must be handed to an
independent worker through Claude Code `Task tool`. If the runtime route does not expose
`Task tool`, the main agent must stop the current step or review, report
`worker_unavailable`, and avoid executing the step in the main context.

## Runtime Boundary

The main agent remains a thin controller. For each step it must:

```text
read ProgressLedger
build StepContextPackage
build StepWorkerDispatch
call Task tool for a step worker
read only StepResult short JSON
update ProgressLedger
```

The step worker receives only:

```text
StepWorkerDispatch path
StepContextPackage path
```

For review, the main agent must:

```text
build ReviewContextPackage
call Task tool for a review worker
read only ReviewResult short JSON
update ProgressLedger
```

The review worker receives only:

```text
ReviewContextPackage path
```

The main agent must not pass artifact bodies, canonical step bodies, review detail bodies,
or raw input material bodies to the worker.

## Fail-Closed Rule

When `Task tool` is unavailable, Plan 9 requires fail-closed behavior:

```text
status = worker_unavailable
do not execute step artifacts in the main agent
do not run review in the main agent
do not bulk-read canonical step files
do not paste artifact or review bodies into long-lived context
```

This keeps context growth bounded even on runtime routes that do not expose subagents.

## Measurement

Plan 9 uses the same measurement command as earlier plans:

```bash
python3 -m ai_writing_plugin.context_metrics --root . --json
```

The generated snapshot is stored at:

```text
docs/maintainers/context_optimization/plan9_metrics.json
```

The expected prompt-size change is small. The primary success criterion is behavioral:
runtime prompts now forbid main-agent fallback when a real worker is unavailable.

## Real Validation Target

After implementation, run one controlled real workflow with
`examples/hara_minimal_fixture/task.yaml` and parse the newest Claude session log. The
validation should report:

```text
Task/subagent tool calls observed, or worker_unavailable_detected
max effective context
cache_read_input_tokens ratio
whether only orchestration short JSON was read by the main agent
```

If the runtime route does not expose `Task tool`, the correct result is
`worker_unavailable_detected`. Do not claim full real worker execution in that case.

## Known Limits

Plan 9 does not implement a Python launcher for Claude/Codex subagents. It does not
generate professional artifacts, perform review/verification judgment, or modify
`contracts/CURRENT_ARTIFACT_CONTRACTS.md`.

Static runtime markdown size remains a separate optimization problem. If the host still
injects all document-type skills into every request, follow-up work should address
document-type lazy routing rather than adding more worker protocol files.

## Verification

Plan 9 is guarded by:

```text
tests/test_thin_main_agent_boundary.py
tests/test_runtime_context_boundary.py
tests/test_context_metrics.py
```

The thin-controller boundary test now requires `Task tool`, `worker_unavailable`,
`fail closed`, path-only worker inputs, and no main-agent fallback.
