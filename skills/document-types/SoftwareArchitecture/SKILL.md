---
name: software-architecture-document-type
description: 中文优先指导汽车控制器产品 Software Architecture（SwAD，软件架构）文档写作；保留 ASPICE SWE.2、ISO 26262-6 软件层接口、SwRS 追溯、组件分配、接口边界、tier、HITL 与 candidate-update 约束。
---

# Software Architecture Document Type Skill

Use this skill for `task_type: SoftwareArchitecture` only when the agent workflow explicitly selects this guidance. This is a non-official L3 Skill/overlay asset. The metadata builder may place its paths/hashes in StepContextPackage for that exact task type, but Python has no Software Architecture rules registry or end-to-end content engine. Default communication is Chinese; keep Software Architecture、SwAD、SWE.2、ISO 26262-6、SwRS、System Architecture、SWA-COMP-xx、SWA-IF-xx、RTE、BSW、HITL、NEEDS_USER_CONFIRMATION.

## Purpose

Software Architecture supports a review-ready ECU software architecture package in ASPICE SWE.2 / ISO 26262-6 context. It organizes software boundary, layers, logical/physical architecture, components, interfaces, SwRS allocation, diagnostics/degradation, safety-related software constraints by citation only, resources/timing, verification method candidates, assumptions, and open confirmations.

It does not produce HARA, FSR, TSC, detailed design, code-level design, ASPICE assessment pass, ISO compliance, architecture approval, or production release approval.

## Method Boundaries

- Read materials by L1→L2→L3→original text.
- One architecture fact = one claim with T0/T1 EVD or explicit open; no blanket evidence for whole tables.
- From-Scratch: many `confirmation_required` / placeholder rows are expected; do not fill missing SwRS, interface direction, task period, stack size, RTE port direction, or component split.
- With-Reference: historical SwAD is `sample` only. It may guide section/table shape, never component/interface/task/resource facts. Include SEC-DIFF / TASK-DIFF when reference is used.

## Typical Inputs

T1 source examples: SwRS, current project System Architecture, software context/layering, AUTOSAR/BSW/MCAL/OS constraints, RTE/service/internal API specs, diagnostics/degradation notes, chip/memory/timing budgets, existing TSR/software safety inputs for SEC-SAFE-ARCH citation only.

Template/checklist/reference/sample keep their roles. Historical SwAD is T4 sample unless the user provides explicit current-project source status.

## Expected Sections

Core sections: scope, inputs/source boundary, software context/layers, upstream SwRS/System Architecture, logical architecture, physical/task architecture, components, interfaces/direction, SwRS allocation, diagnostics/degradation, safety-related architecture constraints by citation, resources/timing, verification candidates, assumptions/open items, review status, optional SEC-DIFF for With-Reference.

## Critical Claims

Critical claims include architecture decomposition, upstream linkage, component definition, interface direction/boundary, allocation rationale, task/scheduling, diagnostics/degradation, resource/timing budgets, safety-related software architecture linkage, verification method, completeness/consistency/sufficiency, and final approval/compliance. They require T0/T1 support or remain `NEEDS_USER_CONFIRMATION`.

## Forbidden Content

- hazard、hazardous event、S/E/C、ASIL、Safety Goal as new HARA/FSR output.
- TSR / technical safety mechanisms as TSC final content.
- detailed design, unit design, algorithms, code, class-level implementation.
- approved / compliant / ASPICE level achieved / ISO 26262 compliant / production ready.
- sample SwAD components, interfaces, tasks, timing, resource budgets as project facts.

SEC-SAFE-ARCH may only cite existing TSR/software safety source and link it to components/interfaces/partitioning; no new HARA, ASIL, or TSR judgment.

## Source Policy

T0=HITL, T1=current project source, T2=template/checklist, T3=reference methodology, T4=sample shape/style, T5=inference. Current project `SystemArchitecture` and SwRS can be T1. Historical SwAD cannot support `SWA-COMP-xx`, `SWA-IF-xx`, task periods, memory/stack budgets, interface timeouts, or allocation facts.

sample 绝不是 fact source。reference is not project-specific fact support.

## Review / Verification Focus

- SWE.2 architecture decomposition, allocation, interface, and design constraints.
- Every component/interface/allocation has source or open.
- Interfaces include direction, peer, boundary, responsibility.
- Logical and physical architecture are consistent.
- Diagnostics/degradation/resources/timing have source or open.
- No HARA/ASIL/SG/TSR/TSC/detailed-design leakage.
- Historical SwAD/sample not used as fact.
- `NEEDS_USER_CONFIRMATION` preserved.

Final report is review-ready, not formal sign-off.
