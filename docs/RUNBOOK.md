# Repository Runbook

Status: current operations for the Phase 0 scaffold, orchestration metadata, and Claude Code worker protocol.

## 1. Environment

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

All commands below assume the repository root.

## 2. Baseline checks

```bash
.venv/bin/python -m ai_writing_plugin --help
.venv/bin/python -m pytest -q -p no:cacheprovider
claude plugin validate .
git status --short
git ls-files runs/
```

The test suite covers scaffolding and orchestration metadata. It does not prove end-to-end professional content generation.

## 3. Current CLI inventory

The current parser has 19 commands:

```text
context-telemetry
check-context-budget
init-run
validate-step-result
validate-review-result
build-step-context-package
validate-step-context-package
init-progress-ledger
record-step-progress
validate-progress-ledger
prepare-step-worker-dispatch
complete-step-worker-dispatch
validate-step-worker-dispatch
build-review-context-package
validate-review-context-package
build-stage-review-issues
validate-stage-review-issues
build-stage-gate-result
validate-stage-gate-result
```

Consult `--help` for exact arguments. No current command runs the full professional writing lifecycle or resumes it.

## 4. Initialize a run

```bash
.venv/bin/python -m ai_writing_plugin init-run \
  --task path/to/task.yaml
```

Expected root files:

```text
input_refs.json
manifest.json
task_brief.json
```

Verify:

```text
manifest.status = initialized
manifest.phase = phase_0
input_refs.schema_version = input_refs.v1
```

No downstream professional directory is expected at this point.

`init-run` belongs to the controller. If it fails, stop: do not initialize the ledger or
prepare any worker dispatch.

## 5. Initialize orchestration state

```bash
.venv/bin/python -m ai_writing_plugin init-progress-ledger \
  --run-dir runs/<run_id>
```

This creates:

```text
orchestration/progress_ledger.json
```

The required startup sequence is `init-run → init-progress-ledger →
prepare-step-worker-dispatch`.

## 6. Prepare a step handoff

Example for the first step:

```bash
.venv/bin/python -m ai_writing_plugin prepare-step-worker-dispatch \
  --repo-root . \
  --run-dir runs/<run_id> \
  --stage ingest \
  --step step-input-materials \
  --task-type <task_type>
```

This creates/updates only metadata:

```text
orchestration/context_packages/ingest/step-input-materials.json
orchestration/worker_dispatches/ingest/step-input-materials.json
orchestration/progress_ledger.json
```

For `step-input-materials`, the dispatched worker receives an already initialized run.
It must not call `init-run` or modify the three root scaffold files. It checks their
input-role and evidence boundaries and reports their final paths/hashes through
StepResult. Its StepContextPackage points to `input_refs.json` separately and automatically
includes both `task_brief.json` and `manifest.json` in `run_refs[]`.

For every later dispatch, `prepare-step-worker-dispatch` validates the ProgressLedger and
each completed, Ledger-bound prior StepResult in the fixed 13-step order, then propagates every real reported
artifact path/hash. `run_refs[]` order is always defaults, automatic upstream artifacts,
preserved extras from an overwritten package, and newly explicit `--input-ref` values,
with stable path deduplication. `input_refs.json` is not duplicated in `run_refs[]`; a
Step 1-reported `manifest.json` therefore reaches later steps through upstream propagation.
If an already-bound upstream result points to a stale or missing file, a bad hash, or the
wrong stage/step, dispatch preparation stops. Earlier steps with no completed Ledger binding
are skipped so isolated metadata preparation remains possible.

Validate before dispatch:

```bash
.venv/bin/python -m ai_writing_plugin validate-step-context-package \
  --path runs/<run_id>/orchestration/context_packages/ingest/step-input-materials.json \
  --repo-root . --run-dir runs/<run_id>

.venv/bin/python -m ai_writing_plugin validate-step-worker-dispatch \
  --path runs/<run_id>/orchestration/worker_dispatches/ingest/step-input-materials.json \
  --repo-root . --run-dir runs/<run_id>
```

## 7. Worker execution boundary

Pass only the StepWorkerDispatch and StepContextPackage paths to a real independent Task/Agent worker. The wrapper and canonical workflow Skill refs are required. The selected document-type root Skill and per-step overlay are independently optional and included only when the exact file exists; root-only document types are valid. Every included instruction ref must still exist and match its hash. The worker:

1. reads referenced instructions and run/input refs;
2. writes only its owned professional artifacts;
3. writes `orchestration/step_results/<step>.json`;
4. runs `validate-step-result` itself;
5. returns a short summary/path, not artifact bodies.

If no independent worker is available, stop with `worker_unavailable`.

## 8. Close a step

```bash
.venv/bin/python -m ai_writing_plugin validate-step-result \
  --run-dir runs/<run_id> \
  --path runs/<run_id>/orchestration/step_results/<step>.json

.venv/bin/python -m ai_writing_plugin complete-step-worker-dispatch \
  --run-dir runs/<run_id> \
  --stage <stage> \
  --step <step> \
  --step-result orchestration/step_results/<step>.json

.venv/bin/python -m ai_writing_plugin validate-progress-ledger \
  --run-dir runs/<run_id> \
  --path runs/<run_id>/orchestration/progress_ledger.json
```

Completion status is derived from ReviewResult when one is supplied and StepResult
otherwise. The optional `complete-step-worker-dispatch --status` is an assertion only:
omit it or pass that same status. A different value fails closed without changing the
Dispatch or Ledger; blocking count and next-gate status come from the same result.

Do not modify a StepResult after completion. If it changes, revalidate and complete the dispatch again so the ledger binds the final hash.

## 9. Build review handoff

After all selected steps in a stage have valid StepResults:

```bash
.venv/bin/python -m ai_writing_plugin build-review-context-package \
  --repo-root . \
  --run-dir runs/<run_id> \
  --stage <stage> \
  --step <step-one> \
  --step <step-two>
```

Use the exact steps for that stage and repeat `--step` as needed. Validate:

```bash
.venv/bin/python -m ai_writing_plugin validate-review-context-package \
  --path runs/<run_id>/orchestration/review_context_packages/<stage>.json \
  --run-dir runs/<run_id>
```

Pass only that package path to one independent review worker for the stage. Step workers do not dispatch nested reviewers or create separate review-state files. The stage review worker is review-only: it records review material and issues but never modifies professional artifacts or StepResult.

The review worker first writes the strict source file
`stage_reviews/<stage>/issues.json`. It has exactly an `issues` list; each item has exactly
`issue_id`, `severity`, `category`, `title`, `summary`, `location_refs`, `artifact_refs`,
`recommendation`, and `rationale`. Severity is `P0`, `P1`, `P2`, `P3`, or `info`, and all
artifact refs are run-contained path/hash pairs. Then it runs:

```bash
.venv/bin/python -m ai_writing_plugin build-stage-review-issues \
  --run-dir runs/<run_id> \
  --stage <stage> \
  --source stage_reviews/<stage>/issues.json

.venv/bin/python -m ai_writing_plugin validate-stage-review-issues \
  --run-dir runs/<run_id> \
  --path stage_reviews/<stage>/issues_index.json
```

This creates the canonical compact index and
`stage_reviews/<stage>/issues/<issue_id>.json` details. Existing output requires
`--overwrite`, and overwrite is allowed only after the prior issue set is no longer bound
by active context/review/ledger/decision/gate metadata. Build/validation is transactional;
failure leaves the previous issue set intact.

Only after that succeeds does the worker follow `context_package_refs[]` and, in the exact
`steps[]` order, write one validated ReviewResult per step under:

```text
orchestration/review_results/<stage>/<step>.json
```

Each referenced StepContextPackage already declares its own `result_paths.review_result`; ReviewContextPackage does not duplicate those paths. A single stage-aggregate ReviewResult is invalid. Missing, duplicate, unexpected, or stage/step-mismatched results are `metadata_invalid` and stop the stage.

After the worker returns, close the review for every step in `steps[]` order:

```bash
.venv/bin/python -m ai_writing_plugin validate-review-result \
  --run-dir runs/<run_id> \
  --path runs/<run_id>/orchestration/review_results/<stage>/<step>.json

.venv/bin/python -m ai_writing_plugin complete-step-worker-dispatch \
  --run-dir runs/<run_id> \
  --stage <stage> \
  --step <step> \
  --step-result orchestration/step_results/<step>.json \
  --review-result orchestration/review_results/<stage>/<step>.json
```

Then run `validate-progress-ledger` and confirm that every selected step still binds the final StepResult hash and now binds the matching final ReviewResult hash. Do not build the stage gate until all `review_result_ref` values are present and current.

### 9.1 Revision cycle

If any ReviewResult is `needs_revision`, keep the gate closed. Use the validated
`stage_reviews/<stage>/issues_index.json`; the review worker does not repair the
professional artifacts itself. For each affected step, re-prepare the original worker:

```bash
.venv/bin/python -m ai_writing_plugin prepare-step-worker-dispatch \
  --repo-root . \
  --run-dir runs/<run_id> \
  --stage <stage> \
  --step <step> \
  --task-type <task_type> \
  --input-ref stage_reviews/<stage>/issues_index.json \
  --overwrite-package \
  --overwrite-dispatch
```

This preserves the target ContextPackage's previous additional `run_refs[]`, appends the
issue index once, and clears that step's stale StepResult/ReviewResult ledger bindings.
Because later prepared steps contain hashes of upstream artifacts, the same transaction
removes every later workflow step's old ContextPackage, StepWorkerDispatch, and ledger
entry. It leaves fixed-path result/artifact files on disk but they are no longer bound.
Any failure restores all touched metadata bytes.

Dispatch the original step worker to perform its A2 instructions, then validate and
complete its new StepResult normally. Next, re-prepare, rerun, validate, and complete every
invalidated downstream step in fixed 13-step order so each package receives current
upstream hashes. Do not reuse the old unbound StepResult merely because its file still
exists.

After the revised target and every invalidated downstream step are complete, start a new
review cycle for the complete original stage step list:

```bash
.venv/bin/python -m ai_writing_plugin build-review-context-package \
  --repo-root . \
  --run-dir runs/<run_id> \
  --stage <stage> \
  --step <step-one> \
  --step <step-two> \
  --overwrite
```

This overwrite is the review-cycle transaction boundary and must finish before the review
worker overwrites fixed-path issue or ReviewResult files. It validates the current cycle,
strips consumed `stage_reviews/<stage>/...` refs from selected ContextPackages, recomputes
their refs, synchronizes affected Dispatch and Ledger bindings, preserves current
StepResult refs, clears all selected steps' old ReviewResult refs, restores status/counts
from StepResult, and creates a new ReviewContextPackage without the previous mutable
`stage_review_refs`. Any failure restores every touched metadata file.

The worker can now replace the issue set with
`build-stage-review-issues --overwrite`, validate it, and re-review every step in the
stage. Validate and bind all new ReviewResults in order. Repeat the same sequence for a
second or later A2 cycle: finish A2 StepResults, run review-context `--overwrite`, replace
and validate issues, then perform a full-stage review. Never perform a partial re-review
or build a gate from mixed review cycles.

## 10. Build stage-gate metadata

Without a decision file:

```bash
.venv/bin/python -m ai_writing_plugin build-stage-gate-result \
  --run-dir runs/<run_id> \
  --stage <stage> \
  --review-result orchestration/review_results/<stage>/<step-one>.json \
  --review-result orchestration/review_results/<stage>/<step-two>.json
```

Repeat `--review-result` for every ReviewContextPackage step in the same order. One-step stages pass exactly one result. If any per-step ReviewResult is `needs_revision` or `blocked`, the agent protocol must not create an `accepted` gate. Even when all are `done`, the default remains `pending_user_confirmation` until a genuine user decision exists.

The default is `pending_user_confirmation`. With a separately created explicit decision file, add:

```text
--decision stage_reviews/<stage>/decision.json
```

`build-stage-gate-result` also exposes `--status`, but that separate gate override is only
structurally validated: it can produce `accepted` without proving a decision or review.
Do not use it to bypass HITL.
The agent protocol may continue only from a genuine explicit user decision that satisfies
the review checks.

Validate:

```bash
.venv/bin/python -m ai_writing_plugin validate-stage-gate-result \
  --run-dir runs/<run_id> \
  --path runs/<run_id>/orchestration/stage_gate_results/<stage>.json
```

There is no current Python command that authors the user decision. Do not fabricate one. A gate controls continuation only and never records professional approval. If a bound ReviewResult changes, revalidate it, re-complete that step dispatch, revalidate the ledger, and rebuild any affected StageGateResult.

## 11. Stage topology

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

The Python layer validates this topology but does not execute the professional work.

## 12. Context diagnostics

```bash
.venv/bin/python -m ai_writing_plugin context-telemetry \
  --root . --task-type hara --step step-evidence-map --json

.venv/bin/python -m ai_writing_plugin check-context-budget \
  --root . --task-type hara --step step-evidence-map --json
```

These are deterministic surface estimates, not provider cache measurements or document-quality metrics.

## 13. Document-type status

- Official L3 product/domain asset labels: `hara`, `technical_solution`, `test_report`, `fsr`.
- Current Python registry/type rules: absent.
- Generic/external profile loading: absent.
- TSC: nonofficial Skill/overlay/fixture prototype; official L3 implementation deferred.

Do not infer execution support from a fixture or Skill directory alone.

## 14. Failure and recovery

Current recovery is metadata-oriented, not a Python content-resume lifecycle:

- inspect ProgressLedger;
- validate the individual package/result/ref that failed;
- regenerate the affected metadata through its builder when safe;
- re-run the independent worker when professional artifacts are invalid;
- never hand-patch hashes or accepted gate state.

## 15. Git hygiene

```bash
git status --short
git status --short -- runs/
git ls-files runs/
git diff --check
```

Do not commit `runs/`, caches, local archives, or optional raw reference folders.

## 16. Current contract

For exact fields, fixed values, paths, statuses, and ref/hash rules, use:

```text
contracts/CURRENT_ARTIFACT_CONTRACTS.md
```
