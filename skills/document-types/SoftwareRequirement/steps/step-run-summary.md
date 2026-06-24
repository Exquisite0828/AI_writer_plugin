# SwRS 子 skill · Step 14 · 运行总结

骨架：`skills/workflow-steps/step-run-summary/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 生成 `run_summary.md`
- 记录流程统计、gap、风险信号
- 只总结流程，不泄漏项目事实

## Checklist

- [ ] run metadata 完整
- [ ] source / template / reference / sample 数量统计齐全
- [ ] 13 step 状态齐全
- [ ] `SWR-F` / `SWR-IF` / open / HITL / EVD 计数齐全
- [ ] gap 按章节分类
- [ ] 风险信号含“历史架构误用风险”“接口方向 open 风险”
- [ ] 状态与 final_report 一致

## reusable_patterns Checklist

- [ ] 只记录流程模式和 checklist 经验
- [ ] 不记录具体 `SWR-F` / `SWR-IF`、接口名、数值、客户名
- [ ] 可记录“历史架构误用防护”“Direction 列高频缺失”等共性

## From-Scratch

- [ ] 说明高 gap / 高 HITL 是正常现象

## With-SystemArchitecture-Reference

- [ ] 单列“历史架构误用迹象”统计
- [ ] 记录 `SEC-DIFF` 完整性信号

## Review 要点

| 检查点 | 通过条件 |
|---|---|
| 中性 | 不写批准/合规语义 |
| 保密 | 不外泄项目事实 |
| 可复盘 | 统计、风险、gap、step 状态可回看 |
| 可学习 | 经验是流程性的，不是项目性的 |

## 常见 P0

- `run_summary` 写成“已合规/已批准”
- `reusable_patterns` 泄漏项目需求或数值

## A1 / A2 / B

**A1**：总结中性、统计完整、无事实泄漏。  
**A2**：删项目细节、补风险信号。  
**B**：本步是学习与复盘，不是第二份正式交付文档。
