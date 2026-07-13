# Project Context Brief

Status: current implementation snapshot after the Python writing-engine removal and
runtime metadata rebuild.

This page is the shortest maintainer-oriented statement of repository reality. Current
Python code and tests take precedence over older design narratives.

## Current capability layers

| Layer | Current state |
| --- | --- |
| Python-enforced | Phase 0 `init-run`, `input_refs.json`, context telemetry, and orchestration metadata builders/validators |
| Claude Code runtime | `/ai-writing-plugin:write`, thin-controller instructions, 7 stages, 13 step workers, review-worker handoff, and user-controlled stage gates |
| Domain assets | document-type Skills, step overlays, task fixtures, profile examples, and design specs |
| Removed or future | one-shot content engine, `write-run`, resume lifecycle, Python document-type registry, profile loader, eval, correction harvesting, and promotion |

The Python package does not currently generate professional drafts, review content,
verification conclusions, final reports, or learning artifacts. Independent Claude Code
workers may create those artifacts under the runtime protocol, then report paths and
hashes through metadata validated by Python.

## Product purpose

The product goal remains an evidence-aware professional document workflow:

```text
input materials
-> material inventory
-> source index and provenance
-> template outline
-> research questions and evidence planning
-> conservative draft
-> review and verification
-> revision and review-ready delivery
-> run summary and proposed candidate update
```

This is the target product workflow and the current agent instruction topology. It is
not a claim that a one-shot Python implementation exists.

## Current entry points

Claude Code plugin entry:

```text
/ai-writing-plugin:write "Run the writing workflow with path/to/task.yaml"
```

The entry requires an environment that exposes Task/Agent worker handoff. The main agent
acts as a thin controller. If independent workers are unavailable, the runtime must fail
closed with `worker_unavailable` rather than generate professional artifacts in the main
context.

Python entry:

```bash
python -m ai_writing_plugin --help
python -m ai_writing_plugin init-run --task path/to/task.yaml
```

`init-run` creates only:

```text
runs/<run_id>/input_refs.json
runs/<run_id>/manifest.json
runs/<run_id>/task_brief.json
```

The remaining Python commands build or validate compact runtime metadata. The exact
surface and schemas are defined in
`contracts/CURRENT_ARTIFACT_CONTRACTS.md`.

## Document-type status

The repository retains four official L3 **product labels**:

- `hara`
- `technical_solution`
- `test_report`
- `fsr`

The current tree contains Skills and fixtures for these labels. It does not contain a
Python document-type registry, Python rules modules, or end-to-end content-engine tests.
“Official L3” therefore describes the maintained product/domain asset category, not a
currently enforced Python execution level.

Other asset levels:

- `generic_document`: generic Skill/profile/task assets; current Python does not execute
  a generic writing pipeline or load its profile.
- `custom_technical_note`: external profile demo asset; current Python has no external
  profile loader.
- `TechnicalSafetyConcept`: nonofficial skill-layer prototype with a root Skill, step
  overlays, and a demo fixture. It has no Python rules/registry, end-to-end content CLI,
  or dedicated engine test. Official L3 TSC and downstream HSC/SSC remain deferred.
- Additional directories under `skills/document-types/` are nonofficial runtime assets;
  their presence alone is not a public support or compatibility guarantee.

## Non-negotiable boundaries

- `source` may support project facts when relevant and correctly interpreted.
- `template` and `checklist` constrain structure and review; they do not prove facts.
- `reference` may support method or background, not project-specific facts.
- `sample` and expected output may guide shape and style only.
- Critical claims require project evidence or explicit human confirmation.
- Missing support stays pending, open, or `NEEDS_USER_CONFIRMATION`.
- A hash match, worker completion, review result, stage gate, or final report is not
  professional approval.
- Candidate updates remain proposals; no current Python command activates them.
- Runtime output stays under ignored `runs/<run_id>/`.

## Repository map

- User status and setup: `README.md`
- Current artifact and metadata contract: `contracts/CURRENT_ARTIFACT_CONTRACTS.md`
- Current architecture: `docs/maintainers/ARCHITECTURE.md`
- Current technical decisions: `docs/TECHNICAL_DECISIONS.md`
- Future sequencing: `docs/maintainers/ROADMAP.md`
- Runtime context policy: `docs/maintainers/RUNTIME_CONTEXT_BOUNDARY.md`
- Maintainer operations: `docs/RUNBOOK.md`
- Historical HARA snapshot: `docs/baselines/HARA_MVP_BASELINE.md`

Historical phase plans and process records are retained by Git history, not used as
current execution instructions. Any future content-engine work requires a new explicit
active phase/spec before implementation.
