# AI Professional Document Writing Plugin Architecture

Status: current implementation architecture plus explicitly separated target direction.

## 1. Architecture rule

Current code and tests define implemented behavior. Target workflows, domain specs, and
historical baselines describe intent but do not imply that removed Python modules still
exist.

The current repository is not a complete deterministic writing engine. It is:

```text
Claude Code command and Skill protocol
+ thin agent controller
+ independent step/review workers
+ deterministic Python run scaffold and orchestration metadata
+ document-type guidance and fixtures
```

## 2. Current implementation

### 2.1 Plugin command layer

`commands/write.md` provides the single user-facing command. It confirms the task and
material source, initializes a run, then delegates control to the workflow orchestrator.
It does not directly write professional artifacts or approve conclusions.

Initialization is controller-owned and ordered: `init-run` creates the three Phase 0
files, `init-progress-ledger` creates orchestration state, and only then may
`prepare-step-worker-dispatch` prepare Step 1. The Step 1 worker consumes those immutable
files and does not invoke `init-run`.

### 2.2 Thin-controller layer

`skills/workflow-orchestrator/SKILL.md` defines seven ordered stages and 13 steps. The
controller keeps compact state only:

- current stage and step;
- ProgressLedger state;
- package/result paths and hashes;
- blocking counts and next-gate status;
- short summaries;
- explicit user gate state.

It does not retain or replay input bodies, artifact bodies, or full review details.

### 2.3 Python metadata layer

The tracked Python package provides:

- `init-run` and the three Phase 0 artifacts;
- `input_refs.json` path/role/hash boundaries;
- context telemetry and deterministic budget diagnostics;
- StepContextPackage builders/validators;
- StepWorkerDispatch preparation/completion/validation;
- StepResult and ReviewResult validation;
- ProgressLedger initialization/update/validation;
- ReviewContextPackage builders/validators;
- strict stage-review issue index/detail builders/validators;
- StageGateResult builders/validators.

These capabilities are exposed by exactly 19 current CLI commands; the canonical list is
the parser help and `contracts/CURRENT_ARTIFACT_CONTRACTS.md`.

It does not parse all professional inputs into knowledge artifacts, write drafts, perform
semantic review, finalize reports, resume a content lifecycle, load profiles, run evals,
or promote candidate updates.

### 2.4 Worker layer

An independent step worker receives only dispatch/package paths. It reads the referenced
current-step instructions and run/input refs, creates the artifacts owned by that step,
writes a compact StepResult, and validates that result before returning. Dispatch
preparation supplies the package defaults, then validated artifacts reported by all
completed upstream StepResults in the fixed 13-step order, then preserved package extras,
then newly explicit refs; paths are stably deduplicated. It propagates identities only and
does not read upstream artifact bodies.

The step worker does not dispatch another worker and does not persist a separate
review/revision state file. Research or execution progress may be tracked inside the
isolated worker invocation, but is not orchestration metadata and is not replayed into
the controller.

One independent review worker per stage receives only a ReviewContextPackage path. It
writes strict `stage_reviews/<stage>/issues.json`, invokes the public issue builder and
validator to produce the canonical compact index/details, and then writes exactly one
compact ReviewResult for every `steps[]` entry using the per-step output path declared by
the referenced StepContextPackage. The controller validates and binds each result back to
the matching ledger entry without turning review into professional approval.

The review worker is review-only: it never rewrites professional artifacts or StepResult.
For P0/P1 or explicit `needs_revision`, the controller passes the stage issue index to the
affected original step worker through an overwritten ContextPackage/Dispatch. Redispatch
of an earlier step atomically invalidates every later workflow step's ContextPackage,
Dispatch, and ledger entry because those packages bind upstream artifact hashes; the
controller reruns that downstream closure in fixed order. After all revised and invalidated
StepResults are rebound, `build-review-context-package --overwrite` transactionally
strips consumed stage-review refs, refreshes affected ContextPackage/Dispatch/Ledger
bindings, preserves current StepResults, clears the stage's old ReviewResults, and starts
a complete stage re-review. It must finish before the review worker replaces fixed-path
issue or ReviewResult files; failure restores all affected metadata bytes.

If Task/Agent handoff is unavailable, the controller records `worker_unavailable` and
stops. It must not execute the professional step in the main context.

Orchestration and stage-review metadata is persisted. ProgressLedger, per-step
ReviewResults, and StageGateResult are the authoritative bindings for continuation and
gates; the context, dispatch, step-result, review-context, and issue files remain persisted
inputs. Legacy
`subagent/` directories in an existing local run are ignored and left untouched.

### 2.5 Storage layer

All runtime state lives under:

```text
runs/<run_id>/
```

The Python-enforced root starts with:

```text
input_refs.json
manifest.json
task_brief.json
```

Compact orchestration metadata lives under `orchestration/`. Professional worker
artifacts may occupy `inputs/`, `knowledge/`, `plans/`, `draft/`, `review/`, `verify/`,
`revised/`, `final/`, `trace/`, and `learning/` only when the corresponding worker
actually runs and reports them.

The exact contract is `contracts/CURRENT_ARTIFACT_CONTRACTS.md`.

## 3. Control flow

```text
user task
-> /write command
-> init-run + init-progress-ledger
-> prepare StepWorkerDispatch
-> independent step worker
-> validate StepResult
-> complete dispatch and update ledger
-> build ReviewContextPackage
-> independent review worker
-> write strict issues.json, build and validate the compact issue set
-> write and validate one ReviewResult per stage step
-> re-complete each dispatch and bind every ledger review_result_ref
-> if revision is required: redispatch affected original step workers with the issue index,
   invalidate and rerun all later workflow handoffs, complete their new StepResults,
   transactionally overwrite ReviewContextPackage, replace the issue set, and re-review
   the full stage
-> explicit stage decision
-> build StageGateResult with all per-step ReviewResults and validate it
-> next stage or stop
```

A missing, duplicate, unexpected, or stage/step-mismatched ReviewResult stops the stage
as `metadata_invalid`. A single stage-aggregate ReviewResult is not part of the current
contract. All per-step results must be current in the ledger before gate construction.

The fixed stage order is:

```text
ingest -> outline -> evidence_planning -> draft -> review -> finalize -> learning
```

The current Python package validates this control metadata. The host agent performs the
actual worker handoff.

## 4. Data flow

The intended professional data flow is:

```text
declared material refs
-> inventory and document navigation
-> source/provenance index
-> outline and research questions
-> evidence/citation/claim planning
-> conservative draft
-> review and mechanical verification
-> controlled revision and review-ready report
-> neutral summary and proposed candidate material
```

This is an agent-worker artifact flow. The current Python layer guarantees only the
initial refs and orchestration metadata around it.

## 5. Context and trust boundaries

### 5.1 Input boundary

`task.yaml` declares paths and roles. `init-run` resolves inputs and records path, hash,
size, MIME type, role, read policy, and fact-source permission without copying bodies.

Only a declared `source` may be fact-supporting. Sample-like paths are forced to
non-fact behavior.

### 5.2 Instruction boundary

StepContextPackage always references the current step wrapper and canonical workflow
Skill. The selected document-type root Skill and per-step overlay are each lazy optional:
an existing file is included and hash-validated, while an absent root or overlay is legal.
A root-only document type therefore works without placeholder overlays. Sibling document
types and the examples tree are not default context.

### 5.3 Result boundary

Workers return paths, hashes, short summaries, blocking counts, and gate status. The main
agent does not treat a reported path as proof of semantic quality. Validators can prove
file identity and metadata shape, not professional correctness.

`complete-step-worker-dispatch` derives status, blocking count, and next-gate status from
ReviewResult when present and StepResult otherwise. Its optional `--status` is only an
equality assertion; a mismatch fails without changing Dispatch or Ledger state.

### 5.4 Approval boundary

Stage acceptance means the user permits orchestration to continue. It never means the
document, evidence, architecture, safety judgment, test conclusion, or compliance state
is professionally approved.

This is an agent-runtime policy, not a fully enforced Python invariant. The current
StageGateResult builder accepts a structural `--status` override without a decision file;
such metadata cannot prove HITL and the thin controller must not treat it as permission
to continue without a genuine user decision.

## 6. Failure model

The runtime fails closed for:

- missing task or declared input file;
- unsafe path or unsupported task-YAML structure;
- invalid/missing metadata fields;
- invalid stage-step pair;
- missing referenced file;
- SHA-256 mismatch;
- invalid stage-review issue source or unsafe issue-set replacement;
- missing worker capability;
- invalid StepResult/ReviewResult;
- absent user decision where a gate requires it.

Failures remain explicit. The controller does not silently skip a stage, fabricate a
worker result, or remove an unresolved confirmation marker.

## 7. Document-type architecture

The current repository separates product labels from executable Python support.

### Official product/domain assets

`hara`, `technical_solution`, `test_report`, and `fsr` are the four official L3 labels.
Their Skills and fixtures define maintained domain guidance. No current Python registry
or type-specific content engine enforces those rules.

### Generic and external profile assets

`generic_document` and the external profile files illustrate the intended L1/L2 model.
The current Python package neither loads those YAML profiles nor changes behavior from
their fields.

### Nonofficial skill-layer assets

PascalCase and other additional document-type directories are runtime guidance assets,
not official compatibility promises. `TechnicalSafetyConcept` specifically has a Skill,
step overlays, and demo fixture, but no Python rules/registry, end-to-end content command,
or dedicated engine test. Official L3 TSC and HSC/SSC are deferred.

## 8. Evidence architecture

The runtime guidance preserves these policies:

```text
T0 = explicit human confirmation
T1 = project source
T2 = template/checklist constraint
T3 = reference methodology/background
T4 = sample style/shape
T5 = generated or unknown inference
```

Only T0/T1 may close a critical project claim. T2-T5 can shape work or expose gaps but
cannot independently prove a critical claim.

Traceability is designed as:

```text
input ref -> original location -> source/provenance -> evidence -> claim -> citation
```

Hash validation proves identity, not truth or sufficiency.

## 9. Current versus target architecture

| Capability | Current | Target, only under future active spec |
| --- | --- | --- |
| Phase 0 scaffold | Python implemented/tested | Preserve |
| Orchestration metadata | Python implemented/tested | Preserve and extend deliberately |
| Agent step/review protocol | Runtime Skills present | Validate with real host integration |
| Professional content stages in Python | Absent | Optional staged reintroduction |
| Resume lifecycle | Absent | Design only if justified |
| Python document-type registry/rules | Absent | Add with fixtures and regression tests |
| External profile loader | Absent | Add schema, loader, safety tests |
| Eval/correction/promotion | Absent | Add only after stable content engine |

Target architecture is not an implementation backlog by itself. Every future row requires
a separately approved active phase/spec.

## 10. Extension gates

A future official document type is not complete merely because a Skill or fixture exists.
It requires, under an active phase:

1. a precise domain spec and source policy;
2. executable rules integrated into the then-current engine architecture;
3. positive and negative deterministic fixtures;
4. regression tests for evidence, terminology, final status, and leakage;
5. current user and maintainer documentation;
6. proof that existing types do not regress.

Likewise, an external profile mechanism is not current until a loader, validation model,
failure behavior, and tests exist.

## 11. Architecture non-goals

Without an active phase, do not:

- restore the removed engine wholesale;
- introduce RAG, vector storage, LangChain, or a generic agent platform;
- make every document type a separate pipeline;
- use sample content as facts;
- automate professional approval;
- auto-activate candidate profile or Skill changes;
- treat historical plans as current execution instructions.

## 12. Verification boundary

Current pytest coverage verifies scaffolding, path/hash contracts, context packages,
dispatch, progress, short results, review packages, stage-gate metadata, telemetry, and
thin-controller boundaries, including stage-review issue metadata and multi-cycle reset.

It does not prove professional content accuracy, complete end-to-end `/write` execution,
or provider-level prompt-cache behavior. Those claims require separate evidence.

## 13. Maintainer update rule

Whenever implementation scope changes:

1. inspect `python -m ai_writing_plugin --help`;
2. inspect current modules and tests;
3. update the current artifact contract first;
4. update this architecture and Project Context;
5. update user docs and changelog;
6. ensure historical behavior is explicitly labeled or removed from current docs.

Do not preserve an inaccurate “completed phase” claim for narrative continuity. Git
history is the archive.
