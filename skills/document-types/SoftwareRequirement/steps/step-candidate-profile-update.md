# SwRS 子 skill · Step 15 · 候选 profile 更新

骨架：`skills/workflow-steps/step-candidate-profile-update/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 提炼可复用 checklist / review 信号
- 产出 `candidate_profile_update.yaml`、`candidate_skill_patch.md`
- 保持 `proposed` / `inactive`

## 可提炼信号 Checklist

- [ ] `SWR-F` 强制 `Linked upstream ID`
- [ ] `SWR-IF` 强制 `Direction` / `Counterpart` / `Trigger`
- [ ] 时序/资源值必须带单位
- [ ] 历史项目 `SystemArchitecture` 不得作为事实 source
- [ ] 需求与设计分层扫描
- [ ] forbidden terms 扫描
- [ ] `SEC-DIFF` 强制规则（With-Reference）

## 禁止写入 Checklist

- [ ] 本项目具体需求 ID
- [ ] 接口名、周期、超时、资源值
- [ ] 客户名、项目名、ECU 名
- [ ] 本次具体差异条目
- [ ] 任何批准/合规模板话术

## From-Scratch

- [ ] 可提炼“输入不足时保持 open”的流程信号

## With-SystemArchitecture-Reference

- [ ] 可提炼“历史架构 source 防误标”“`SEC-DIFF` 强制存在”“matrix file_id 防护”
- [ ] 不得写入本次参考架构的具体内容

## Review 要点

| 检查点 | 通过条件 |
|---|---|
| 可复用性 | 是通用流程规则，不是项目事实 |
| 安全性 | `active=false`，需人工审查 |
| 聚焦性 | 只补强 SwRS checklist / review，不扩成新文档类型 |

## 常见 P0

- candidate 写入项目事实
- candidate 自动启用
- 把本次参考架构差异条目固化进通用 patch

## A1 / A2 / B

**A1**：只输出通用信号，状态保守。  
**A2**：删具体事实、补风险说明。  
**B**：候选 patch 只能增强方法学，不能沉淀项目答案。
