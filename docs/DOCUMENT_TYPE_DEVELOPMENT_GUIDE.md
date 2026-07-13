# Document Type Development Guide

Status: completion criteria for a future active phase; not evidence that a current Python document-type engine exists.

## Current baseline

The repository has document-type Skills, overlays, specs, profiles, and fixtures. Current Python code has no document-type registry, executable type rules, profile loader, or end-to-end content engine.

Repository policy retains four official L3 product/domain labels: `hara`, `technical_solution`, `test_report`, and `fsr`. Their present asset status must not be confused with Python enforcement.

`TechnicalSafetyConcept` is a nonofficial skill-layer prototype with Skill/overlay/fixture assets only. Official L3 TSC and HSC/SSC are deferred.

## Before implementation

Do not add executable document-type behavior without a dedicated active phase/spec. The spec must define:

- exact domain purpose and non-goals;
- source, template, checklist, reference, and sample policies;
- default/required sections;
- critical claims and required human confirmations;
- forbidden final claims and allowed final statuses;
- artifact/API changes;
- positive and negative fixtures;
- regression and compatibility requirements.

## Completion model

A future official type is complete only when all layers exist:

1. **Domain Spec**: human-readable purpose and safety boundaries.
2. **Executable Rules**: integrated with the then-current Python content architecture.
3. **Fixtures**: deterministic positive and negative cases.
4. **Tests**: type rules, evidence, leakage, final status, and full supported flow.
5. **Skill Guidance**: concise runtime instructions that do not replace executable rules.
6. **Product Docs**: accurate setup, scope, limitations, and examples.

A Skill or fixture alone is not an official executable implementation.

## Shared pipeline rule

Future types must reuse one shared content pipeline. Domain-specific code may supply sections, claims, confirmation rules, terminology, review focus, and final-status policy. It must not duplicate the whole workflow.

## Required safety tests

At minimum, future tests must cover:

- sample is never a fact source;
- reference does not prove project facts;
- unsupported critical claims remain pending;
- forbidden approval language is blocked;
- final report remains review-ready, not approved;
- document-type terminology does not leak across domains;
- candidate changes remain inactive;
- existing types do not regress.

## Fixture rule

Fixtures are deterministic test/demo inputs. They are never project fact sources outside their own test task, and expected outputs must not be hard-coded into product logic.

## Runtime context rule

Runtime files should load only the selected document type. Do not bulk-read sibling Skills or all examples. Domain overlays may refine current-step rules but cannot redefine Phase 0 ownership or the global artifact tree.

## Current verification commands

These checks exist now:

```bash
.venv/bin/python -m ai_writing_plugin --help
.venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_runtime_context_boundary.py
claude plugin validate .
```

They validate the current scaffold/metadata/runtime surfaces. They do not prove a future type's content engine. An active type phase must add its own real test files and acceptance commands before claiming support.

## TSC rule

Do not upgrade TSC from nonofficial Skill prototype to official L3 by documentation change. Official TSC requires its own active phase, executable rules, fixtures, negative cases, tests, and compatibility evidence. HSC/SSC remain out of scope until separately authorized.

## Review checklist

Before merging a future type implementation, verify:

- every documented module and command exists;
- every referenced test exists and passes;
- support level wording matches actual implementation;
- no professional approval is implied;
- source/sample/reference boundaries are enforced;
- current artifact contract is updated intentionally;
- user and maintainer docs agree;
- deferred types remain deferred.
