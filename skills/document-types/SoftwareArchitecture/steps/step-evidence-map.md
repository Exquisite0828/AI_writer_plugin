# Software Architecture 子 skill · Step 6 · 证据·引用·章节计划

骨架：`skills/workflow-steps/step-evidence-map/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## Purpose

必须按三阶段顺序执行：

1. **Phase A evidence map**：L1→L2→L3→原文 → EVD。每条 EVD 支撑一个可审查 architecture claim；critical claim 仅 T0/T1。
2. **Phase B citation plan**：建立 `claim_support_matrix.json`，将 claim type 绑定 EVD/tier；缺证据写 `NEEDS_USER_CONFIRMATION` 和 `unresolved_questions.md`。
3. **Phase C section tasks**：生成 `section_tasks.json` / `writing_plan.md`；每个 TASK 声明 `allowed_evidence`，Step 7 只能用这些 EVD。

## Claim Types

Required claim coverage: `architecture_wording`, `upstream_swrs_linkage`, `system_architecture_context`, `component_definition`, `software_interface_architecture`, `allocation_rationale`, `task_scheduling_architecture`, `diagnostic_architecture`, `resource_timing_budget`, `safety_architecture_linkage`, `verification_method`, `architecture_completeness_consistency`.

## Rules

- One architecture fact = one claim with EVD or explicit open; no blanket EVD for a full table.
- SwRS allocation claims cite SwRS L3 text, not second-hand paraphrase.
- Interface direction needs interface spec/RTE/config EVD or open.
- SEC-SAFE-ARCH cites only explicit TSR/software safety source and cannot support "implemented/covered" claims.
- No HARA/ASIL/Safety Goal fields enter the matrix as new analysis.
- TASK-IF, TASK-ALLOC, TASK-RES, TASK-SAFE-ARCH commonly stay `confirmation_required` unless evidence is strong.

## Scenario Focus

From-Scratch: unresolved rows are normal; every allocation/interface/resource claim has EVD or open. Do not reduce open counts by inference.

With-Reference: historical SwAD must not appear as EVD `source_file_id` for critical claims. It may appear only as T4 `reference_shape_only`, outside critical matrix. Include TASK-DIFF; its evidence must be current-project source.

## Review / Checklist

- Phase A/B/C all present and internally consistent.
- Each EVD has `source_file_id`, L1/L2/L3, `location`, excerpt, tier.
- T4/T5 do not support critical claims.
- Components/interfaces/allocation/resources/diagnostics each have EVD or unresolved.
- `section_tasks.json` matches matrix and outline; every TASK has narrow `allowed_evidence`.
- Matrix covers all claim types and marks missing support as open.
- With-Reference matrix contains no historical SwAD support for components/interfaces/allocation/resources.

P0: historical SwAD in evidence_map/matrix as fact; fabricated citation; TASK-ALLOC supported without allowed evidence; SEC-SAFE-ARCH blanket support; T4 supports critical claim.

P1: EVD excerpt mismatches L3; matrix missing claim type; section task IDs drift from outline.

## A1 / A2 / B

**A1**：三 phase 产物齐全，EVD↔matrix↔TASK 一致，tier 合规。
**A2**：失败 phase 局部重跑；修正 tier/open，而不是补事实。
**B**：Step 7 必须可仅凭 TASK `allowed_evidence` 成稿。
