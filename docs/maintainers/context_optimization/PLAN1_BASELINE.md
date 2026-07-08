# Plan 1 Baseline: Context And Cache Optimization

Status: Plan 1 baseline record.

This document records the first measurement baseline for reducing runtime context growth
and improving cache stability. It is maintainer reference only and must not be loaded by
runtime prompts as execution context.

## Measurement Method

Plan 1 measures the runtime prompt surface only:

```text
commands/**/*.md
skills/**/*.md
```

The measurement command is:

```bash
python -m ai_writing_plugin.context_metrics --root . --json
```

In this local environment, `python` may not exist as an executable name. The same module
was verified with:

```bash
python3 -m ai_writing_plugin.context_metrics --root . --json
```

`estimated_tokens` is a trend metric only:

```text
ceil(character_count / 4)
```

It is not provider billing tokenization and must not be used as a cost invoice.

## Baseline Snapshot

The generated baseline is stored at:

```text
docs/maintainers/context_optimization/baseline_metrics.json
```

Current measured summary:

```text
total_files: 145
total_bytes: 840995
estimated_tokens: 141262
scope: commands/, skills/
```

Category summary:

| Category | Files | Bytes | Estimated tokens |
| --- | ---: | ---: | ---: |
| command | 1 | 12706 | 2258 |
| document_type | 116 | 692754 | 116768 |
| step_wrapper | 13 | 7713 | 1934 |
| workflow_orchestrator | 1 | 12684 | 2037 |
| workflow_step | 13 | 104532 | 15815 |
| writing_core | 1 | 10606 | 2450 |

Largest current runtime prompt files include:

1. `skills/document-types/hara/steps/step-conservative-draft.md`
2. `skills/document-types/SoftwareArchitecture/SKILL.md`
3. `skills/workflow-steps/step-source-index/SKILL.md`
4. `skills/document-types/TechnicalSafetyConcept/SKILL.md`
5. `skills/document-types/hara/steps/step-verification.md`

## Known High-Risk Context Drivers

The current runtime prompt architecture still says that workflow artifacts are produced
by the main execution context, with independent subagents primarily used for review.
That means the main agent can accumulate:

1. Step instructions.
2. Step-owned artifacts and summaries.
3. Stage-review package details.
4. User gate decisions.
5. Subagent review outputs.

This is consistent with the observed risk that long workflow execution approaches the
available context window. The CC Switch screenshots from July 2026 are treated as human
observation, not as automated test input.

Cache hit rate is likely low because dynamic runtime content can appear early and often:

1. Different step skills are loaded across the workflow.
2. Document-type overlays vary by `task_type`.
3. Artifact contents and review outputs change every run.
4. The controller context currently carries more than stable paths and hashes.

## Comparison Rules For Later Plans

Later context optimization plans should compare against this baseline using the same
command and the same scope. A later plan may improve the tool, but it should keep this
Plan 1 payload readable for historical comparison.

Useful comparison fields:

1. `total_files`
2. `total_bytes`
3. `estimated_tokens`
4. `by_category`
5. `largest_files`
6. `hotspot_patterns`

Plan 1 intentionally does not set pass/fail thresholds. It creates a repeatable baseline
so later plans can make evidence-backed claims.

## Boundaries

Plan 1 does not:

1. Change `/ai-writing-plugin:write` behavior.
2. Change any workflow step semantics.
3. Add worker/subagent orchestration.
4. Read CC Switch session logs.
5. Treat `runs/` artifacts as product input.
6. Scan `examples/**`, `contracts/**`, or `docs/maintainers/**` as runtime context.

Plan 1 only adds a maintainer measurement tool, a baseline record, and tests that protect
the measurement scope.
