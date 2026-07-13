# SwRS 子 skill · Step 11 · 最终报告

骨架：`skills/workflow-steps/step-final-report/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 打包 `final/final_report.md` 与 `final/delivery_summary.md`
- 状态只允许保守枚举
- 明示下游交接边界

## final_report Checklist

- [ ] 文档信息、状态、修订历史齐全
- [ ] 说明非 HARA / TSC / Software Architecture / design 终稿
- [ ] 列出 source / template / reference / sample 边界
- [ ] 包含 `SEC-FUNC`、`SEC-IF`、`SEC-TIME`、`SEC-RESOURCE`、`SEC-DIAG`、`SEC-TRACE`、`SEC-VERIF`
- [ ] Open Items Registry 完整
- [ ] 审查/验证摘要存在但不写 sign-off

## 下游交接 Checklist

- [ ] 可作为 Software Architecture / test planning 的输入
- [ ] open 项明确告知下游不得静默关闭
- [ ] 上游追溯与架构上下文对下游可见

## 状态 Checklist

- [ ] `ready_for_human_review`
- [ ] `finalized_with_open_items`
- [ ] `blocked_pending_confirmation`
- [ ] 禁止 `approved` / `validated` / `compliant`

## From-Scratch

- [ ] gap 分类进入 `delivery_summary`
- [ ] open 项数量与风险说明匹配

## With-SystemArchitecture-Reference

- [ ] 明示“历史项目 `SystemArchitecture` 仅作参考，不支撑本项目软件需求事实”
- [ ] 包含 `SEC-DIFF`
- [ ] 下游说明中明确不得用历史架构关闭 open

## Review 要点

| 检查点 | 通过条件 |
|---|---|
| 交付边界 | 文档是 review-ready，不是批准文件 |
| 信息完整 | 正文、追溯、open、审查/验证摘要齐全 |
| 参考边界声明 | 历史架构参考边界明确写出 |
| 下游安全性 | 下游不会误把 open 当关闭、不会误把参考当事实 |

## 常见 P0

- 写批准/合规结论
- 漏掉 open 项
- With-Reference 未声明历史架构边界

## A1 / A2 / B

**A1**：交付包完整、状态保守、边界清楚。  
**A2**：补字段、补 open、补参考边界声明。  
**B**：final 只提高可交接性，不改变事实来源边界。
