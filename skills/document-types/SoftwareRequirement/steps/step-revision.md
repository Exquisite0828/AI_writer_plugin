# SwRS 子 skill · Step 10 · 修订

骨架：`skills/workflow-steps/step-revision/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 根据 Step 8/9 findings 修订草稿
- 写 `revised/full_draft.md` 与 `change_log.md`
- 不新增无证据的软件需求事实

## 修订优先级 Checklist

- [ ] 先删 HARA / TSC / 架构设计泄漏
- [ ] 再处理 sample / 历史架构支撑事实的问题
- [ ] 再补上游追溯与接口字段
- [ ] 再修时序/资源/诊断 open 与验证方法
- [ ] 最后处理文风、单位、ID 一致性

## 修订原则 Checklist

- [ ] 每项修改都可追到 issue_id
- [ ] 无 EVD 不新增 requirement
- [ ] 不把 `NEEDS_USER_CONFIRMATION` 静默改 confirmed
- [ ] 不删除 open 项，只能转移或补证据关闭
- [ ] `change_log.md` 记录 before/after 与 decision_basis

## From-Scratch

- [ ] 不为“看上去完整”而关闭 open
- [ ] 重点修 shall 句式、追溯、字段完整性

## With-SystemArchitecture-Reference

- [ ] 绝不使用历史架构来关 P0
- [ ] 若删掉参考痕迹后产生缺口，必须保留 open
- [ ] `SEC-DIFF` 的修订仍基于本项目 source / HITL

## Review 要点

| 检查点 | 通过条件 |
|---|---|
| 变更可追溯 | 每项修订有来源和依据 |
| 不引入新风险 | 修订没有新增伪事实 |
| 参考边界保持 | 历史架构未被拿来填坑 |
| 回归一致性 | 修订后 trace、matrix、open 同步更新 |

## 常见 P0

- 为关问题伪造 EVD
- 静默删除 open
- 用历史架构关闭差异或补时序值

## A1 / A2 / B

**A1**：P0 已关闭或转 open，修订可追溯。  
**A2**：继续修 blocker 并回归验证。  
**B**：修订目标是更保守、更可追溯，不是更“漂亮”。
