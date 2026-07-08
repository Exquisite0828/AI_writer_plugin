# Runtime Context Boundary Policy

Status: Current maintainer policy.

This policy defines which repository materials may enter Claude Code runtime context during normal plugin execution. It exists to prevent maintainer documents, examples, and artifact contracts from being treated as default runtime input or as a checklist for creating every possible output.

## Problem Statement

The observed issue is not that Claude Code has provenly loaded the entire `docs/maintainers/` and `examples/` folders into context.

The confirmed risk is runtime context boundary pollution: runtime prompts and skills can blur execution instructions, maintainer documentation, artifact contracts, examples, and run outputs. When that boundary is unclear, Claude Code may treat reference material as operational instructions or treat a full artifact contract as a run creation checklist.

The practical failure mode is over-eager runtime behavior, such as pre-creating many `runs/<run_id>/` directories or artifacts because a reference list was embedded in a runtime skill.

## Repository Context Classes

| Path | Context class | Runtime rule |
| --- | --- | --- |
| `commands/` | Runtime entry prompts | May be loaded for command execution. Keep minimal and do not embed maintainer design detail. |
| `skills/` | Runtime skill prompts | May enter context when a skill is selected. Describe only current runtime duties and step-owned outputs. |
| `contracts/` | Runtime-readable contracts | Read intentionally only when exact artifact paths, required fields, or schemas are needed. Do not load by default. |
| `docs/maintainers/` | Maintainer design docs | Maintainer reference only. Do not use as runtime execution instructions. |
| `docs/` user docs | Product documentation | Human-facing guidance. Do not treat as hidden command input. |
| `examples/` | Demo fixtures | Read only when the user explicitly chooses a demo task or a test references a committed fixture. |
| `runs/` | Runtime outputs | Generated output only. Do not commit. Read only for resume, review, diagnosis, or explicit user inspection. |

## Runtime Prompt Rules

Runtime files are `commands/**/*.md` and `skills/**/*.md`.

Runtime files must not:

1. Reference `docs/maintainers/*` as execution instructions.
2. Glob or bulk-read `examples/**` as default context or default input.
3. Embed the complete artifact tree from `contracts/CURRENT_ARTIFACT_CONTRACTS.md`.
4. Instruct Claude Code to pre-create every possible `runs/<run_id>/` subdirectory or artifact.
5. Treat sample, demo, or expected-output content as factual evidence.

Runtime files may:

1. Point to `contracts/CURRENT_ARTIFACT_CONTRACTS.md` as the single artifact/schema authority.
2. Read that contract intentionally for a concrete contract question.
3. Mention specific example task paths only as opt-in demo commands or deterministic test fixtures.
4. List only the artifacts owned by the current command or workflow step.

Document-type step files under `skills/document-types/*/steps/` are domain overlays. They may define role classification, critical claims, review wording, and domain checks, but they must not redeclare ownership of shared runtime artifacts such as run creation, manifests, or global artifact trees.

## Engine-Owned Run Start

Run start is owned by the deterministic engine, not by prompt text. The runtime entry for Phase 0 is:

```bash
python -m ai_writing_plugin init-run --task <task.yaml>
```

This command may create only `runs/<run_id>/manifest.json` and `runs/<run_id>/task_brief.json`. Runtime prompts may request or inspect those artifacts, but must not hand-write them or pre-create downstream artifact directories.

## Contract Boundary

`contracts/CURRENT_ARTIFACT_CONTRACTS.md` is the single source of truth for artifact names, paths, and schema expectations when a contract exists.

Runtime prompts must not duplicate that contract in full. Duplicated contract lists drift over time and can be misread as instructions to generate every listed artifact. A runtime skill may summarize the contract's purpose, then require intentional contract reads only when exact path or schema detail is needed.

## Examples Boundary

`examples/` contains committed demos and deterministic fixtures. It is not a default knowledge base.

Allowed use:

1. A user explicitly runs a documented demo task.
2. A test case references a fixture.
3. A maintainer manually inspects example shape or output style.

Disallowed use:

1. Runtime prompts bulk-read all examples.
2. Example content supports professional facts or conclusions.
3. Demo task files are silently used as default input for unrelated runs.

## Maintainer Explanation Template

Use this wording when explaining the issue to reviewers or teammates:

```text
The problem is not proven full-folder context loading of docs/maintainers and examples.

The real issue is runtime context boundary pollution. Runtime skills included or pointed at reference material in a way that could make Claude Code treat artifact contracts, maintainer docs, or demo fixtures as execution instructions.

The concrete risk is that reference lists, especially artifact lists, can become accidental checklists. That can lead to over-generation, such as creating many runs/<run_id>/ directories or artifacts before the relevant workflow step owns them.

The fix is to keep runtime prompts minimal, make contracts intentionally readable rather than embedded, keep maintainer docs out of runtime execution paths, and allow examples only as explicit demos or deterministic test fixtures.
```

## Acceptance Checks

Before claiming this boundary is preserved, run static checks over runtime prompt files:

```bash
rg -n "docs/maintainers|examples/\\*\\*|Core artifacts include|docs/CURRENT_ARTIFACT_CONTRACTS\\.md" commands skills
```

Expected result:

1. No runtime reference to `docs/maintainers` as execution input.
2. No runtime instruction to bulk-read `examples/**`.
3. No embedded `Core artifacts include` full artifact tree.
4. No reference to the old artifact contract path.

Then run:

```bash
claude plugin validate .
git diff --check
```
