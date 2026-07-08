# Plan 10: Active Runtime Context Metrics

Status: Plan 10 active metrics and document-type lazy routing boundary.

This document records the tenth context optimization step. It is maintainer reference
only and must not be loaded by runtime prompts as execution context.

## Goal

Plan 1-9 reduced dynamic context growth by moving step and review work behind
path/hash protocols and real worker handoff requirements. The remaining large surface is
static runtime markdown, especially `skills/document-types/**`.

Plan 10 separates two measurements:

```text
total runtime surface = all commands/**/*.md and skills/**/*.md
active runtime context = files needed for one selected task_type and scope
```

It also makes document-type routing lazy in the runtime prompts. The main agent confirms
`task_type`, then puts only the selected document-type paths and hashes into
StepContextPackage. It must not bulk-read all document types.

## Metrics Modes

The context metrics tool now supports:

```bash
python3 -m ai_writing_plugin.context_metrics --root . --mode total --json
python3 -m ai_writing_plugin.context_metrics --root . --mode active-workflow --task-type hara --json
python3 -m ai_writing_plugin.context_metrics --root . --mode active-step --task-type hara --step step-input-materials --json
```

`total` keeps the Plan 1 behavior and scans `commands/` plus `skills/`.

`active-workflow` counts only:

```text
commands/write.md
skills/workflow-orchestrator/SKILL.md
skills/writing-core/SKILL.md
all 13 step wrappers
all 13 workflow canonical steps
the selected task_type document root
the selected task_type step overlays
```

`active-step` counts only:

```text
commands/write.md
skills/workflow-orchestrator/SKILL.md
skills/writing-core/SKILL.md
the selected step wrapper
the selected canonical step
the selected task_type document root
the selected task_type step overlay
```

The new fields are:

```text
mode
task_type
step
total_runtime_estimated_tokens
active_reduction_vs_total
excluded_document_type_files
excluded_document_type_bytes
```

The token estimate remains `ceil(character_count / 4)` and is only a trend metric, not a
provider billing token count.

## Current Snapshot

After Plan 10 prompt updates:

```text
total runtime surface: 145 files, 850,903 bytes, 143,097 estimated tokens
hara active workflow: 43 files, 299,229 bytes, 49,910 estimated tokens
hara step-input-materials active step: 7 files, 71,653 bytes, 13,108 estimated tokens
```

For `task_type=hara`, active workflow reduces the measured runtime context by about
65.1% versus total. This meets the Plan 10 target of at least 40% reduction in active
workflow measurement.

## Runtime Boundary

Runtime prompts now require `DocumentTypeLazyLoad`:

```text
main agent confirms task_type
main agent writes only selected document-type path/hash refs into StepContextPackage
worker reads selected document type files through package refs
main agent and orchestrator do not bulk-read all document types
worker must not read sibling document types
```

Example: when `task_type=hara`, the active package may include
`skills/document-types/hara/SKILL.md` and hara step overlays. It must not include sibling
document-type rules such as `SoftwareArchitecture` or `SystemRequirement`.

## Known Limits

Plan 10 does not move files out of `skills/document-types/**`, split the plugin, or
change how the Claude Code host injects registered skills. If the host still injects all
skills into the first model call, Plan 10 can prove the active context boundary but cannot
physically lower that host-injected total surface by itself.

If real validation shows `host_injects_total_runtime_surface`, follow-up work should move
document-type rules behind a physical lazy-loading boundary, such as plugin splitting,
data-file relocation, or document-type package generation outside registered skill files.

## Real Validation Note

Controlled validation with `examples/hara_minimal_fixture/task.yaml` reached the first
step worker and review worker before budget stop.

Observed session:

```text
session_id: faceff23-2e1b-4936-ad78-b4f0c1e3939e
run_dir: runs/hara-20260708T150132Z
main Agent tool calls: 2
main max effective context: 74,479
main cache ratio: 0.895080
step worker max effective context: 44,340
step worker cache ratio: 0.935852
review worker max effective context: 40,100
review worker cache ratio: 0.781668
```

Document-type reads in the main agent, step worker, and review worker were limited to:

```text
skills/document-types/hara/SKILL.md
skills/document-types/hara/steps/step-input-materials.md
```

No sibling document-type reads were observed.

The same validation also exposed a separate protocol drift: the real agent still wrote
some orchestration files manually with non-standard fields, so Python validators rejected
that run's `StepWorkerDispatch`, `StepContextPackage`, and `ProgressLedger`. This is not
part of Plan 10's active-context scope, but follow-up work should require real runtime
execution to call the existing Python builder/validator commands instead of hand-writing
orchestration JSON.

## Verification

Plan 10 is guarded by:

```text
tests/test_context_metrics.py
tests/test_context_packages.py
tests/test_thin_main_agent_boundary.py
tests/test_runtime_context_boundary.py
```

The tests cover:

```text
total / active-workflow / active-step metrics
selected task_type document refs only
no sibling document type refs in StepContextPackage
DocumentTypeLazyLoad prompt contract
no broad runtime reads of maintainer docs, examples, or runs
```
