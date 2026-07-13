# Technical Decisions

Status: current tracked implementation decisions.

## 1. Source of implementation truth

The current command parser, Python validators, tests, and plugin manifest define what is
implemented. Product goals and historical baselines cannot promote removed code into a
current capability.

If documentation conflicts with code, update the documentation or create a new active
phase/spec before changing implementation.

## 2. Runtime split

The system deliberately separates two responsibilities.

### Python deterministic metadata layer

Python owns:

- Phase 0 run initialization;
- input path/role/hash metadata;
- context telemetry and budget diagnostics;
- step context packages;
- worker dispatch metadata;
- short StepResult and ReviewResult validation;
- progress ledger updates;
- review context packages;
- strict stage-review issue index/detail metadata;
- compact stage-gate results.

Python currently does not own professional content generation, semantic review,
verification conclusions, final delivery, profile evaluation, or profile promotion.

### Claude Code agent workflow

The `/write` command and Skills define a 7-stage, 13-step agent workflow. The main agent
is a thin controller. Independent workers read only referenced inputs/instructions, write
their owned professional artifacts, and return compact path/hash results.

Task/Agent handoff is required. There is no fallback in which the long-lived main agent
silently performs a professional step when a worker is unavailable.

## 3. Language and dependencies

- Runtime language: Python 3.11+.
- Runtime dependencies: Python standard library only in the current package metadata.
- Test framework: pytest via the optional `dev` extra.
- Structured metadata: JSON.
- Human-readable runtime instructions and reports: Markdown.
- Task configuration: a deliberately limited YAML subset parsed by
  `ai_writing_plugin.run_scaffold`; the current package does not depend on PyYAML.

The limited parser supports the current task shape and fails closed on unsupported
structures. It must not be described as a general YAML implementation.

## 4. Current CLI decision

The CLI exposes 19 commands in these families:

- Phase 0: `init-run`;
- telemetry: `context-telemetry`, `check-context-budget`;
- short-result validators;
- step-context builders/validators;
- progress-ledger builders/validators;
- worker-dispatch preparation/completion/validation;
- review-context builders/validators;
- stage-review issue builders/validators;
- stage-gate-result builders/validators.

The canonical list belongs to `python -m ai_writing_plugin --help` and
`contracts/CURRENT_ARTIFACT_CONTRACTS.md`.

The old one-shot/stage content commands and resume lifecycle are not current interfaces.
Future high-level commands require a dedicated active implementation phase.

## 5. Artifact and path decisions

- All runtime output is contained by `runs/<run_id>/`.
- `init-run` creates `input_refs.json`, `manifest.json`, and `task_brief.json` only.
- Orchestration metadata lives under `runs/<run_id>/orchestration/`.
- Metadata carries run-relative paths and SHA-256 hashes, not artifact/input bodies.
- Dispatch preparation propagates validated prior StepResult artifacts in fixed workflow
  order. Stable merge order is defaults, automatic upstream refs, preserved package
  extras, then new explicit refs; paths are deduplicated without reading bodies.
- Validators reject path traversal, unexpected fields, invalid statuses, missing files,
  and hash mismatches where file validation is requested.
- Progress state is updated through builders rather than hand-patched.
- Completion status/count/gate metadata comes from ReviewResult when present and StepResult
  otherwise; `complete-step-worker-dispatch --status` is only an equality assertion.

The artifact contract distinguishes Python-enforced metadata from professional artifacts
owned by agent workers.

## 6. Context-boundary decision

Long-lived main-agent context retains only stable orchestration rules, compact state,
paths, hashes, counts, and short summaries.

Step workers receive a StepWorkerDispatch and StepContextPackage path. Review workers
receive a ReviewContextPackage path. Runtime prompts do not bulk-read maintainer docs,
all document types, the examples tree, or the full run tree.

The current step wrapper and canonical workflow Skill are required. Document-type routing
is lazy: the selected type's root Skill and per-step overlay are independently optional,
and only an exact existing file is referenced and hash-validated. Root-only mode is valid;
missing optional overlays do not fail and sibling document types are not scanned. The
existence of a directory does not make it an official or engine-enforced document type.

## 7. Review-cycle decision

The review worker is read-only with respect to professional artifacts. Its fixed output
order is strict `issues.json`, public issue build, public issue validation, then one
ReviewResult per stage step. The source accepts only the documented issue fields and
run-contained artifact refs. Python transactionally materializes the canonical compact
`issues_index.json` and per-issue details; an actively referenced set cannot be replaced.

Revision is performed by redispatching the affected original step worker. Redispatching an
earlier step transactionally removes every later workflow step's old ContextPackage,
Dispatch, and ledger entry; those workers must run again in fixed order because their
inputs bind upstream artifact hashes. After all A2 and invalidated downstream StepResults
are current, `build-review-context-package --overwrite` starts the next cycle:
it strips consumed stage-review refs, synchronizes ContextPackage/Dispatch/Ledger hashes,
preserves StepResult bindings, clears old ReviewResult bindings, and validates all
candidate metadata before replacing anything. A failed write restores the old bytes. The
next review replaces the fixed-path issue set and reviews the complete stage, so repeated
A2 cycles do not retain stale issue hashes.

## 8. Evidence and approval decision

```text
fact source != sample document
```

- Only project `source` material may support project-specific facts.
- `sample` and expected-output material are shape/style inputs only.
- `reference` material cannot independently prove a project fact.
- Critical claims without project evidence or explicit HITL remain pending.
- Review and verification outputs are advisory/engineering artifacts.
- A stage gate is orchestration permission, not professional approval.
- The current StageGateResult `--status` override is structurally validated but does not
  prove HITL; the agent protocol, not Python alone, enforces the genuine-user-decision
  requirement before continuation.

## 9. Document-type decision

`hara`, `technical_solution`, `test_report`, and `fsr` remain official L3 product/domain
labels with maintained Skill/fixture assets. Current Python code does not implement a
document-type registry or type-specific content rules.

`generic_document`, external profile YAML, and `custom_technical_note` are design/config
assets. They are not loaded or enforced by the current Python package.

`TechnicalSafetyConcept` is a nonofficial skill-layer prototype: its Skill, step overlays,
and fixture are present, while Python rules, registry, end-to-end content execution, and
dedicated engine tests are absent. Official L3 TSC and HSC/SSC are deferred.

## 10. Candidate-learning decision

Skills may describe proposed candidate artifacts, but the current Python package does not
generate, evaluate, activate, or promote them. Stable Skills and profiles cannot be
overwritten automatically.

## 11. Framework decision

The current repository does not introduce RAG, a vector database, LangChain, a generic
workflow platform, or a heavy agent framework. New dependencies require an active phase
and a demonstrated need.

## 12. Verification decision

Current verification consists of:

- pytest coverage for run scaffolding and orchestration metadata contracts;
- CLI help inspection;
- Claude Code plugin manifest validation when the CLI is available;
- runtime-context boundary scans;
- Git hygiene checks.

Tests do not currently prove end-to-end professional document generation or domain
correctness.

## Current decision summary

| Topic | Current decision |
| --- | --- |
| Python | 3.11+, standard-library runtime |
| Tests | pytest |
| Task parsing | Limited YAML subset, fail closed |
| Python ownership | Phase 0 scaffold and orchestration metadata |
| Professional content | Independent Claude Code workers |
| Long-lived controller | Paths/hashes/short state only |
| Current high-level content CLI | None |
| Runtime output | `runs/<run_id>/` |
| Domain labels | Four official L3 asset categories; no Python registry |
| External profiles | Files/design only; no current loader |
| TSC | Nonofficial skill prototype; official implementation deferred |
| Professional approval | Always outside automated metadata results |
| Heavy framework dependency | None |
