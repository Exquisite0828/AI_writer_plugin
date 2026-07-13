# SwRS 子 skill · Step 8 · 审查

骨架：`skills/workflow-steps/step-review/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 从内容质量与工程语义角度审查 `draft/full_draft.md`
- 输出 `review/*`
- 审查结论只代表 review-ready，不代表正式批准

## ASPICE SWE.1 对照 Checklist

- [ ] 上游软件需求分析是否完整
- [ ] 软件需求规格是否结构化、可验证
- [ ] 与上游系统需求和系统架构是否一致
- [ ] 双向追溯是否建立
- [ ] open 项是否被记录和沟通

## 内容审查 Checklist

- [ ] 每条 `SWR-F` 有上游 ID
- [ ] 每条 `SWR-IF` 有方向、对端、触发/时序或 open
- [ ] 时序/资源/诊断值有 source 或 open
- [ ] 软件需求与软件架构设计未混写
- [ ] 安全相关软件需求只作引用
- [ ] `SEC-DIFF` 在 With-Reference 场景下存在且具体
- [ ] 无批准/合规/量产措辞

## ISO 26262 关注点

- [ ] 需求可作为软件开发与软件验证输入
- [ ] 不含新的安全分析结论
- [ ] 若上游已有安全需求，其映射和边界清楚

## From-Scratch

- [ ] 重点看 gap 是否诚实
- [ ] 不因为草稿“看起来不完整”就建议凭经验补齐

## With-SystemArchitecture-Reference

- [ ] 重点看历史架构是否渗入正文事实
- [ ] 重点看 `SEC-DIFF` 是否泛化成“基本沿用”

## Review 要点

| 维度 | 关注点 |
|---|---|
| 正确性 | 与上游系统需求、当前项目架构一致 |
| 可测性 | 需求有条件、动作、结果 |
| 分层性 | 需求不下沉为设计 |
| 追溯性 | 上游、架构上下文、验证方法可追 |
| 边界性 | 历史参考不当事实、结论不越权 |

## 常见 P0

- 样例/历史架构支撑正文事实
- 需求无上游却标 confirmed
- 需求中含设计实现细节
- 写“通过 SWE.1 / ISO 26262”

## A1 / A2 / B

**A1**：审查项均有结论，P0 已识别。  
**A2**：把 findings 交给 Step 10 修订。
**B**：Review 重点是找错和找风险，不是替用户补事实。
