---
name: hara-document-type
description: 中文优先指导 HARA document type work，同时保留 HARA terminology、evidence、source tier、HITL、final-report、sample/reference 和 candidate-update boundaries。
---

# HARA Document Type Skill

Use this skill for `task_type: hara`. Default user-facing communication is Chinese; keep HARA, hazard, hazardous event, S/E/C, ASIL, safety goal, HITL, NEEDS_USER_CONFIRMATION, source tier, and artifact field names unchanged.

## Purpose

HARA assists creation of a traceable, review-ready ISO 26262-3 hazard analysis report package. It may organize item definition, operational situations, hazards, hazardous events, S/E/C candidate ratings, ASIL candidates, safety goal candidates, open confirmations, review, and verification artifacts. It must not automatically approve professional HARA judgments.

`hara` is an official L3 built-in. It preserves HARA terminology and uses the shared workflow; each step overlay under `skills/document-types/hara/steps/` supplies step-specific domain rules.

## Typical Inputs

- item definition / system boundary / interfaces
- operational situations and modes
- assumptions and constraints
- HARA template
- safety or review checklist
- functional safety methodology reference
- sample HARA report for style/table shape only

## Expected Sections

Default report sections: purpose/scope, input materials, item definition, operational situations, hazard identification, hazardous event analysis, S/E/C table, ASIL candidate table, safety goal candidates, open issues, review summary.

## Critical Claims

HARA critical claims include hazard identification, hazardous event definition, severity rating, exposure rating, controllability rating, ASIL/risk level, safety goal, and final acceptability conclusion. They require T0/T1 evidence or recorded HITL. Without that support, keep `NEEDS_USER_CONFIRMATION`, pending, or open.

Human confirmation is required for hazard, HE, S/E/C, ASIL, safety goal wording, and final acceptability. Record real confirmations in `trace/hitl_decisions.jsonl` or equivalent trace artifact; noninteractive runs must not fake confirmation.

## Forbidden Final Claims

Without explicit T0/T1 support and HITL, do not write final claims such as final ASIL approved/confirmed, risk acceptable, hazard confirmed, safety goal approved, final risk level, or `the rating is S1/S2/S3/E1/E2/E3/C1/C2/C3`. These are warning examples, not output templates.

## Source Policy

- T0: HITL / explicit human confirmation.
- T1: parsed project source.
- T2: template/checklist constraints.
- T3: reference methodology; cannot prove project hazard or rating.
- T4: sample style; cannot support hazard, HE, S/E/C, ASIL, SG, or final conclusion.
- T5: generated/unknown inference; cannot support critical claim.

sample is not fact source. sample must not be used as fact source. reference cannot prove project facts. T3/T4/T5 cannot support critical claim by themselves.

## Review / Verification Focus

Review and verification must check template completeness, checklist coverage, unsupported hazards/HE/S/E/C/ASIL/SG, source tier/provenance, sample/reference misuse, `NEEDS_USER_CONFIRMATION` preservation, candidate update inactive, and absence of professional approval language.

## Final Boundary

`final_report.md` is a plugin-generated package for qualified human review, not approval, not formal compliance approval, and not qualified safety sign-off. Conservative statuses: `finalized_with_open_items`, `ready_for_human_review`, `blocked_pending_confirmation`. Unresolved HARA items remain open.

Candidate updates stay proposed/inactive and must not overwrite stable skills.
