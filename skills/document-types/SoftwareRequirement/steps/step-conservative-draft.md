# SwRS 子 skill · Step 7 · 保守草稿

骨架：`skills/workflow-steps/step-conservative-draft/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 按 `section_tasks.json` 写 `draft/full_draft.md`
- 仅使用 `allowed_evidence`
- 产出 review-ready 草稿，不写设计终稿或合规结论

## 成稿 Checklist

- [ ] 每条需求用 `shall` / `应`
- [ ] 单条单义、可验证
- [ ] 每条 `SWR-F` 有上游 ID 与架构上下文
- [ ] 每条 `SWR-IF` 有 `Direction`、`Counterpart`、`Trigger / timing`
- [ ] 时序/资源值缺证据时写 `NEEDS_USER_CONFIRMATION`
- [ ] 诊断需求写软件行为，不写详细实现
- [ ] 安全相关软件需求只引用既有上游，不做新分析

## 写作语言 Checklist

- [ ] 避免“高效”“稳定”“合理”“足够”等模糊词
- [ ] 数值必须带单位
- [ ] 主体明确，如“软件应…”“Bootloader 应…”
- [ ] 不把设计方案写成需求，如线程分配、模块内部算法、类结构

## Forbidden Checklist

- [ ] 不出现 HARA / ASIL / SG / TSR / TSC
- [ ] 不出现 Software Architecture / detailed design 终稿内容
- [ ] 不出现 `approved`、`compliant`、`production ready`
- [ ] 不使用历史项目 `SystemArchitecture` 的事实字段作为正文证据

## From-Scratch

- [ ] `NEEDS_USER_CONFIRMATION` 多是正常状态
- [ ] 不为关闭 open 而补默认周期、默认资源值

## With-SystemArchitecture-Reference

- [ ] `SEC-DIFF` 至少一行，且差异具体
- [ ] 历史架构措辞无本项目 EVD 时不得进入正文
- [ ] “沿用参考架构”必须由 HITL 或本项目 source 支撑

## Review 要点

| 检查点 | 通过条件 |
|---|---|
| 需求质量 | 清晰、可测、单义 |
| 追溯完整 | `SWR-F` / `SWR-IF` 可追到上游 |
| 架构边界 | 用架构解释上下文，不把架构设计写成要求 |
| 参考边界 | 历史架构只出现在 `SEC-DIFF` 或注释语境，不支撑事实 |

## 常见 P0

- `SWR-IF` 无方向却标 confirmed
- 把任务、线程、模块设计写入 SwRS
- 从历史架构抄接口、周期、资源值
- 写“已满足 ASPICE/ISO 26262”

## A1 / A2 / B

**A1**：草稿保守、可追溯、无设计泄漏。  
**A2**：删违规正文、补 open、修 shall 语句。  
**B**：草稿的每一行都应能追溯到 `allowed_evidence` 或显式 open。
