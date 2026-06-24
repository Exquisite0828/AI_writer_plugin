# SwRS 子 skill · Step 6 · 证据·引用·章节计划

骨架：`skills/workflow-steps/step-evidence-map/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 建立 `EVD-xxx`
- 形成 `claim_support_matrix.json`
- 生成 `section_tasks.json` 与 `writing_plan.md`

## Phase A · 证据映射 Checklist

- [ ] 每条 critical claim 有 EVD 或 `NEEDS_USER_CONFIRMATION`
- [ ] EVD 含 `source_file_id`、L1/L2/L3、`location`、`excerpt`、`tier`
- [ ] `tier` 用于 critical claim 时只能是 T0/T1
- [ ] 接口 EVD 能证明方向、触发、时序或至少其中一部分
- [ ] 时序/资源/诊断 EVD 能证明数值或行为；无则 open

## Phase B · 引用计划 Checklist

- [ ] `requirement_wording`
- [ ] `upstream_linkage`
- [ ] `architecture_context_linkage`
- [ ] `interface_definition`
- [ ] `timing_or_resource_limit`
- [ ] `diagnostic_behavior`
- [ ] `safety_related_linkage`
- [ ] `verification_method`
- [ ] `requirement_completeness_sufficiency`

## Phase C · TASK Checklist

- [ ] `TASK-FUNC`
- [ ] `TASK-IF`
- [ ] `TASK-TIME`
- [ ] `TASK-RESOURCE`
- [ ] `TASK-DIAG`
- [ ] `TASK-SAFE`
- [ ] `TASK-TRACE`
- [ ] `TASK-VERIF`
- [ ] `TASK-DIFF` 仅 With-Reference

## 架构引用边界 Checklist

- [ ] **当前项目** `SystemArchitecture` 可作为 `architecture_context_linkage` 的 EVD
- [ ] **历史项目** `SystemArchitecture` 不得出现在 `evidence_source`
- [ ] 历史项目架构最多作为 `style_hint`
- [ ] 不允许用历史架构的任务周期、模块分工、接口超时去支撑本项目 claim

## From-Scratch

- [ ] 大量 `confirmation_required` 合理
- [ ] 无当前项目架构时，`architecture_context_linkage` 保持 open

## With-SystemArchitecture-Reference

- [ ] `TASK-DIFF` 必须存在
- [ ] 与差异有关的事实仍必须来自本项目 source
- [ ] 历史架构 file_id 不得进入 matrix 的 `evidence_source`

## Review 要点

| 检查点 | 通过条件 |
|---|---|
| matrix 合法性 | 每条 claim 的证据链合法且可追 |
| 架构上下文使用正确 | 当前项目架构可支撑上下文；历史架构不能支撑事实 |
| 任务可执行 | 每个 TASK 允许证据范围清楚 |
| 保守性 | 没证据就 open，不编 citation |

## 常见 P0

- 用 sample/历史架构支撑软件需求 claim
- 编造上游链接或 citation
- 让 `TASK-DIFF` 直接引用历史架构事实

## A1 / A2 / B

**A1**：EVD、matrix、TASK 一致且 tier 合规。  
**A2**：删除违规证据、回退 claim、补 unresolved。  
**B**：后续草稿只可使用 `allowed_evidence`。
