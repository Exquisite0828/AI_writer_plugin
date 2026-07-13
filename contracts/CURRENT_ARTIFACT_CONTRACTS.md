# Current Artifact Contracts

Status: current implementation contract for the tracked repository.

This file describes what the current Python package creates or validates, and separately
records the artifact ownership expected by the Claude Code worker protocol. It does not
describe the removed Phase 0-8 Python writing engine as a current capability.

## 1. Scope and authority

The repository currently has three distinct capability layers.

1. **Python-enforced artifacts**: Phase 0 run scaffolding and orchestration metadata.
2. **Agent-worker artifacts**: professional writing artifacts produced by independent
   workers following `commands/write.md` and the selected workflow/document-type skills.
3. **Removed or future capabilities**: the former one-shot writing engine, resumable
   lifecycle, profile loader/eval, correction harvesting, and profile promotion.

Layer 1 is created or structurally validated by the current Python package. StepResult
and ReviewResult are written by workers and then validated by Python; the other current
metadata families have Python builders. Layer 2 is an instruction-level runtime
contract: Python may validate paths and hashes reported by a worker, but it does not
generate or semantically approve the professional content.

When this file conflicts with the parser or validators under `ai_writing_plugin/`, the
tracked Python code and tests are the implementation truth and this file must be fixed.

## 2. Current CLI surface

The current CLI entry is:

```bash
python -m ai_writing_plugin <command>
```

The parser exposes exactly these 19 commands:

| Area | Commands |
| --- | --- |
| Context telemetry | `context-telemetry`, `check-context-budget` |
| Phase 0 | `init-run` |
| Short results | `validate-step-result`, `validate-review-result` |
| Step context | `build-step-context-package`, `validate-step-context-package` |
| Progress | `init-progress-ledger`, `record-step-progress`, `validate-progress-ledger` |
| Worker dispatch | `prepare-step-worker-dispatch`, `complete-step-worker-dispatch`, `validate-step-worker-dispatch` |
| Review context | `build-review-context-package`, `validate-review-context-package` |
| Stage review issues | `build-stage-review-issues`, `validate-stage-review-issues` |
| Stage gate result | `build-stage-gate-result`, `validate-stage-gate-result` |

The current CLI does **not** expose a one-shot writing command, stage content commands,
resume lifecycle, HITL recorder, review execution/decision lifecycle, profile
loader/generator, eval, correction harvesting, or profile promotion. The two stage-review
issue commands build and validate compact metadata only. Names such as `write-run`,
`resume-run`, `draft-run`, `review-run`, `finalize-run`, `profile-from-spec`, and
`profile-promote` are not current executable interfaces.

## 3. Shared invariants

- Runtime files are stored below `runs/<run_id>/` and are not committed.
- `run_id` matches `^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$` and cannot contain `..`.
- Orchestration refs and worker-reported artifact refs are run-relative POSIX paths;
  absolute paths, `~`, backslashes, `runs/` prefixes, dot segments, and traversal are
  rejected where their validators apply. `input_refs.json` is the exception: each ref
  declares `path_kind=repo_relative|external`, and an `external` ref must be absolute.
- Hash references use lowercase 64-character SHA-256 values.
- Metadata validators reject missing and unexpected fields.
- A hash reference is not professional approval and does not prove that source content is
  correct or sufficient for a claim.
- `sample` and expected-output material are never project fact sources.
- Critical professional claims require project source evidence or explicit human
  confirmation; otherwise workers keep them pending or `NEEDS_USER_CONFIRMATION`.

## 4. Phase 0 run scaffold

### 4.1 Command and tree

The controller owns run initialization. Its fixed order is `init-run`,
`init-progress-ledger`, then `prepare-step-worker-dispatch`; a failure stops before the
next operation. No step worker invokes `init-run`.

```bash
python -m ai_writing_plugin init-run --task <task.yaml>
```

`init-run` creates one new directory and exactly three root artifacts:

```text
runs/<run_id>/
  input_refs.json
  manifest.json
  task_brief.json
```

It does not pre-create professional stage directories and does not draft, review, verify,
finalize, learn, or resume a run.

### 4.2 `manifest.json`

Top-level fields:

```text
run_id
task_file
created_at
status
phase
artifacts
```

Fixed Phase 0 values:

```text
status = initialized
phase = phase_0
```

`task_file` is the resolved task path. `artifacts` records `input_refs.json`,
`manifest.json`, and `task_brief.json`; the `input_refs.json` entry includes its SHA-256.
The scaffold owns this file. Workers must not hand-edit it.

### 4.3 `task_brief.json`

Exact fields:

```text
run_id
task_type
task_title
target_audience
output_format
strict_template
allow_inference
requires_human_confirmation
```

Defaults are `output_format=markdown`, `strict_template=false`, and
`allow_inference=false`. The scaffold owns this file. It is a compact task summary, not a
copy of input bodies and not a document-type registry decision.

### 4.4 `input_refs.json`

Fixed metadata:

```text
schema_version = input_refs.v1
created_by = ai_writing_plugin.input_refs
```

Top-level fields:

```text
schema_version
run_id
created_by
constraints
task_ref
input_materials
warnings
```

Fixed constraints:

```text
paths_and_hashes_only = true
no_inline_body = true
examples_opt_in_only = true
sample_is_not_fact_source = true
deterministic_no_timestamps = true
```

`task_ref` fields:

```text
path
path_kind
sha256
size_bytes
role = task
read_policy = metadata_only
fact_source_allowed = false
```

Each `input_materials[]` entry contains:

```text
material_id
role
path
path_kind
sha256
size_bytes
mime_type
read_policy
fact_source_allowed
selected_by = task
```

Allowed roles are `source`, `template`, `checklist`, `reference`, `sample`,
`expected_output_shape`, `other`, and the reserved task role. Only `source` may have
`fact_source_allowed=true`. Sample/example/expected-output paths are forced to non-fact
and cannot use unrestricted fact-reading semantics.

The file stores paths, hashes, sizes, roles, and policies only. It never embeds task or
input bodies.

## 5. Workflow topology

The orchestration metadata recognizes seven stages and 13 stage-step pairs:

| Stage | Steps |
| --- | --- |
| `ingest` | `step-input-materials`, `step-material-inventory`, `step-source-index` |
| `outline` | `step-template-outline` |
| `evidence_planning` | `step-research-questions`, `step-evidence-map` |
| `draft` | `step-conservative-draft` |
| `review` | `step-review`, `step-verification` |
| `finalize` | `step-revision`, `step-final-report` |
| `learning` | `step-run-summary`, `step-candidate-profile-update` |

The Python package validates this topology but does not execute the professional steps.

## 6. `StepContextPackage`

Path:

```text
orchestration/context_packages/<stage>/<step>.json
```

Builder and validator:

```text
build-step-context-package
validate-step-context-package
```

Exact fields:

```text
kind = step_context_package
schema_version = 1
run_id
stage
step
task_type
created_at
instruction_refs
input_refs_ref
run_refs
result_paths
constraints
```

`instruction_refs[]`, `input_refs_ref`, and `run_refs[]` are `{path, sha256}` references.
The current step wrapper and canonical workflow Skill are required. The selected
document-type root Skill and per-step overlay are both lazy optional refs: each is included
only when that exact file exists. A root Skill without an overlay is valid, absence of
either optional file is not an error, and sibling document types are never scanned. Every
ref that is included must exist and match its hash. `input_refs_ref` points to
`input_refs.json`; `run_refs` always begins with `task_brief.json`. For
`step-input-materials` the defaults also include controller-created `manifest.json`.

`build-step-context-package` keeps its direct, explicit-input behavior.
`prepare-step-worker-dispatch` additionally validates the ProgressLedger and every completed,
Ledger-bound prior StepResult in the fixed 13-step order, then propagates its real `artifact_paths`
without reading artifact bodies. The final stable ordering is:

```text
default refs
-> automatically propagated upstream artifact refs
-> additional refs preserved from an overwritten existing package
-> new explicit --input-ref values
```

Paths are stably deduplicated. `input_refs.json` remains in `input_refs_ref` instead of
being duplicated in `run_refs[]`; `task_brief.json` remains the default ref. This means a
Step 1-reported `manifest.json` naturally reaches later steps through normal upstream
propagation. An upstream result already bound in the Ledger fails closed when its referenced
file or artifact is missing, stale, hash-mismatched, or stage/step-mismatched. A later step may
still be prepared in isolation when an earlier step has no completed Ledger binding.

Expected result paths are:

```text
step_result = orchestration/step_results/<step>.json
review_result = orchestration/review_results/<stage>/<step>.json
```

Fixed constraints require paths/hashes only, no artifact body, no input body, and no
inline instructions.

## 7. `StepWorkerDispatch`

Path:

```text
orchestration/worker_dispatches/<stage>/<step>.json
```

Builder, completion command, and validator:

```text
prepare-step-worker-dispatch
complete-step-worker-dispatch
validate-step-worker-dispatch
```

Exact fields:

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

The two refs use `{path, sha256}`. A dispatch binds the exact context package and points
to the mutable progress ledger. Its fixed boundary requires package-path-only handoff,
worker-side reference reading, short-result-only main-agent reads, and no artifact/input
bodies.

Preparing a dispatch records `context_ready` in the ledger. When an existing dispatch is
prepared with `--overwrite-dispatch`, the builder first validates the old Ledger,
ContextPackage, and StepWorkerDispatch, then
clears that step's stale StepResult/ReviewResult bindings, resets its counts/gate status,
and binds the current ContextPackage. Because every later prepared step consumes completed
upstream outputs, the same transaction removes every later workflow step's stale
ContextPackage, StepWorkerDispatch, and ledger entry. The controller must redispatch those
later steps in fixed 13-step order; fixed-path result files left on disk are unbound until
their workers replace and complete them. Any failure restores every touched metadata file.
With `--overwrite-package`, existing additional `run_refs[]` are preserved and new
`--input-ref` paths are merged after validated upstream artifacts with stable path
deduplication. An existing package that does not already match the invocation identity and
complete merged ref order is rejected unless `--overwrite-package` is used.

Completing a dispatch validates the worker's StepResult and optional ReviewResult,
requires the result files at the canonical paths declared by that dispatch, checks
run/stage/step identity, and updates the ledger and dispatch atomically. An existing
ReviewResult binding cannot be silently dropped by repeating completion without a
ReviewResult. The authoritative completion status comes from ReviewResult when one is
supplied and from StepResult otherwise. The optional
`complete-step-worker-dispatch --status` argument is an assertion only: omitting it uses
the authoritative status, an equal value is accepted, and a different value fails closed
without changing Dispatch or Ledger state. Blocking count and next-gate status come from
the same authoritative result. Completion does not validate the professional meaning of
reported artifacts.

## 8. Short results

Allowed result statuses are:

```text
done
needs_revision
blocked
skipped
```

### 8.1 `StepResult`

Path:

```text
orchestration/step_results/<step>.json
```

Exact fields:

```text
kind = step_result
schema_version = 1
run_id
stage
step
status
artifact_paths
artifact_hashes
summary
blocking_issues_count
next_gate_status
```

### 8.2 `ReviewResult`

Path:

```text
orchestration/review_results/<stage>/<step>.json
```

Exact fields:

```text
kind = review_result
schema_version = 1
run_id
stage
step
status
review_package_paths
review_package_hashes
summary
blocking_issues_count
next_gate_status
```

For both kinds, the path list and hash-map keys must match exactly. With `--run-dir`, all
reported files must exist inside the run and match their hashes. `summary` is at most 600
characters and cannot contain code fences; `blocking_issues_count` is a non-negative
integer; `next_gate_status` is a non-empty string of at most 120 characters.

## 9. `ProgressLedger`

Path:

```text
orchestration/progress_ledger.json
```

Commands:

```text
init-progress-ledger
record-step-progress
validate-progress-ledger
```

Top-level fields:

```text
kind = progress_ledger
schema_version = 1
run_id
created_at
updated_at
entries
```

Each entry contains:

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

Ledger statuses are `not_started`, `context_ready`, `running`, `done`,
`needs_revision`, `blocked`, and `skipped`. Each stage/step pair appears at most once.
Refs are null or `{path, sha256}` and are validated against their delegated contracts.
The ledger is mutable orchestration state and must be updated through builders, not hand
patched.

After stage review, the agent-runtime protocol re-runs
`complete-step-worker-dispatch` for each step with the unchanged final StepResult and the
corresponding final ReviewResult. This binds `review_result_ref` and refreshes the entry's
status, blocking count, and next-gate status from that ReviewResult.

If review requests revision, the review worker does not modify professional artifacts or
StepResult. The controller re-prepares each affected original step worker with both
overwrite flags and adds `stage_reviews/<stage>/issues_index.json`; the reset makes it
safe for that worker to replace its artifact and StepResult. After all affected steps are
complete, `build-review-context-package --overwrite` starts the next full-stage review
cycle through the transaction described below.

## 10. `ReviewContextPackage`

Path:

```text
orchestration/review_context_packages/<stage>.json
```

Builder and validator:

```text
build-review-context-package
validate-review-context-package
```

Exact fields:

```text
kind = review_context_package
schema_version = 2
run_id
stage
steps
created_at
context_package_refs
step_result_refs
stage_review_refs
result_paths
constraints
```

`steps` is a non-empty unique list. Context-package and StepResult refs must match those
steps in order. Optional `stage_review_refs` may point only to the current stage's
`review_prompt.md`, `review_units.json`, `issues_schema.json`, `review_context.json`, or
`issues_index.json`; this builder does not create those review files.

With `--overwrite`, the builder is the transaction boundary that must run before the
review worker replaces fixed-path issue or ReviewResult files. It validates the current
Ledger and selected ContextPackages, Dispatches, StepResults, ReviewResults, and referenced
issue metadata; removes consumed `stage_reviews/<stage>/...` refs from the selected
ContextPackages; recomputes those package refs; synchronizes every affected Dispatch and
Ledger `context_package_ref`; preserves current `step_result_ref` bindings; clears the
whole selected stage's `review_result_ref` bindings; and restores status, blocking count,
and next-gate status from each current StepResult. The replacement ReviewContextPackage
has no previous-cycle mutable `stage_review_refs`. All candidate metadata is validated
before commit, and any failure restores the old bytes instead of leaving a partial cycle.

The expected result path is:

```text
orchestration/stage_gate_results/<stage>.json
```

ReviewContextPackage does not duplicate per-step ReviewResult output paths. For every
item in `steps[]`, the review worker follows the matching `context_package_refs[]` entry
and uses that StepContextPackage's `result_paths.review_result`. The agent-worker protocol
requires an exact one-to-one mapping:

```text
ReviewContextPackage.steps[]
<-> per-step ReviewResult
<-> ProgressLedger.review_result_ref
<-> StageGateResult.review_result_refs[]
```

One stage review worker writes one ReviewResult for every step, in `steps[]` order. A
single stage-aggregate result, a missing result, a duplicate step, or an extra step is a
runtime `metadata_invalid` failure. This is an orchestration-policy requirement built
from existing schemas; ReviewContextPackage remains schema version 2.

A step worker ends after writing and validating its StepResult; it does not dispatch a
nested reviewer. Across the runtime, all seven orchestration metadata families are
persisted; stage-review issue metadata is persisted separately under `stage_reviews/`.
ProgressLedger, per-step ReviewResults, and StageGateResult provide the
authoritative continuation and gate bindings; ContextPackages, Dispatches, StepResults,
and ReviewContextPackages remain persisted metadata inputs to those decisions. Former
per-step review/revision state files under a local run's `subagent/` directory are legacy
material: the current runtime does not read, migrate, delete, or use them for continuation.

The fixed boundary requires paths/hashes only, no artifact bodies, no inline review
details, and package-path-only handoff from the main agent.

## 11. Stage review issue metadata

Public builder and validator:

```text
build-stage-review-issues
validate-stage-review-issues
```

The review worker first writes the strict source file at:

```text
stage_reviews/<stage>/issues.json
```

Its top-level object has exactly one field, `issues`. Every item has exactly these fields:

```text
issue_id
severity
category
title
summary
location_refs
artifact_refs
recommendation
rationale
```

Severity is one of `P0`, `P1`, `P2`, `P3`, or `info`; issue IDs are unique. Artifact refs
are run-contained `{path, sha256}` values whose files must exist and match. Unknown,
missing, body-like, duplicate, unsafe, or hash-mismatched input fails closed.

The public flow is:

```bash
python -m ai_writing_plugin build-stage-review-issues \
  --run-dir runs/<run_id> \
  --stage <stage> \
  --source stage_reviews/<stage>/issues.json

python -m ai_writing_plugin validate-stage-review-issues \
  --run-dir runs/<run_id> \
  --path stage_reviews/<stage>/issues_index.json
```

The builder produces only the canonical compact index/detail split:

```text
stage_reviews/<stage>/issues_index.json
stage_reviews/<stage>/issues/<issue_id>.json
```

`issues_index.json` has exactly `kind`, `schema_version`, `run_id`, `stage`,
`issue_count`, `blocking_issues_count`, `severity_counts`, and `issues`. Each compact
`issues[]` entry has `issue_id`, `severity`, `category`, `short_title`, and an
`issue_ref` path/hash. Each detail has exactly `kind`, `schema_version`, `run_id`,
`stage`, the nine source issue fields, and bounded content. P0/P1 contribute to the
blocking count. The index never embeds full issue details or artifact bodies.

Existing output requires `--overwrite`. Replacement is rejected while the current issue
set is still referenced by a ContextPackage, ReviewContextPackage, Ledger-bound state,
decision, or gate. Candidate index/details are built and validated before replacement;
any write or validation failure restores the previous set byte for byte.

The stage review worker's required order is:

```text
write issues.json
-> build-stage-review-issues
-> validate-stage-review-issues
-> write and validate one ReviewResult per stage step
```

The issue metadata records review findings; it does not modify professional artifacts,
approve conclusions, or replace the per-step ReviewResult contract.

## 12. `StageGateResult`

Path:

```text
orchestration/stage_gate_results/<stage>.json
```

Builder and validator:

```text
build-stage-gate-result
validate-stage-gate-result
```

Exact fields:

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

Gate statuses are `accepted`, `needs_revision`, `blocked`, `skipped`, and
`pending_user_confirmation`. With neither a decision file nor a `--status` override,
the builder defaults to `pending_user_confirmation`. `accepted` and `skipped` map to
`can_continue`; other statuses map to their corresponding non-continuation state.

The CLI currently accepts `--status` even when no decision or ReviewResult is supplied,
and the validator checks that value structurally rather than proving a human decision.
Therefore an override-generated `accepted`/`skipped` result is not evidence of HITL.
The agent-runtime policy must refuse those continuation states without a genuine explicit
user decision and the required review checks.

Before a stage gate is built by the agent runtime, every ReviewContextPackage step must
have a validated ReviewResult whose path/hash is already bound in the corresponding
ProgressLedger entry. The builder receives all of those ReviewResults through repeated
`--review-result` arguments in the same step order. Any `needs_revision` or `blocked`
result prevents an `accepted` runtime decision; all-`done` still waits at
`pending_user_confirmation` until genuine HITL.

If a decision is supplied, its stage/decision must match. It cannot set
`professional_approval=true`; an optional decision scope must be
`stage_review_gate_only`. When a stage issues index exists, the decision must bind its
path and hash. A stage gate controls orchestration only and is never professional
approval.

## 13. Agent-worker professional artifact ownership

The Claude Code runtime may ask independent workers to create professional artifacts.
These paths are reported through StepResult/ReviewResult, but their content is not
generated or semantically validated by the Python package.

| Step | Instruction-level owned outputs |
| --- | --- |
| `step-input-materials` | read-only verification of controller-created `input_refs.json`, `manifest.json`, and `task_brief.json`; StepResult reports their final path/hash; no newly authored scaffold or final prose |
| `step-material-inventory` | `inputs/input_inventory.json` and parsing notes |
| `step-source-index` | document navigation, `knowledge/source_index.json`, provenance and gap artifacts |
| `step-template-outline` | template structure and outline artifacts under `plans/` |
| `step-research-questions` | research questions and section-planning artifacts under `plans/` |
| `step-evidence-map` | evidence map, claim support, citation, section-task and writing-plan artifacts |
| `step-conservative-draft` | section drafts and `draft/full_draft.md` |
| `step-review` | review packages under `review/` and stage-review material when required |
| `step-verification` | mechanical verification reports under `verify/` |
| `step-revision` | `revision_plan.json` and controlled artifacts under `revised/` |
| `step-final-report` | review-ready files under `final/` |
| `step-run-summary` | neutral trace/summary artifacts under `trace/` and `learning/` |
| `step-candidate-profile-update` | proposed/inactive candidate material under `learning/` |

Exact prose structure and domain boundaries come from the current step skill and selected
document-type overlay. A worker must not create a full artifact tree in advance, claim
that missing stages ran, or convert a pending claim into approval language.

Candidate material is a proposal only. The current repository has no Python command that
activates a profile or overwrites a stable Skill.

## 14. Removed and non-current contracts

The Git history contains a former Phase 0-8 deterministic writing engine and related
contracts. That implementation was removed before the current scaffold/metadata layer
was rebuilt. Its lifecycle commands, run-state model, profile/eval system, correction
harvesting, and promotion flow are not current interfaces.

Future work may reintroduce selected capabilities only under an explicit active
phase/spec. Historical behavior must not be inferred from this current contract or used
as an instruction to implement a future phase early.
