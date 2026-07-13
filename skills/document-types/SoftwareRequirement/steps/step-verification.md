# SwRS 子 skill · Step 9 · 验证

骨架：`skills/workflow-steps/step-verification/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 做形式化/规则化验证
- 检查 artifact 链、tier 合规、forbidden terms、需求字段完整性
- 输出 `passed_with_open_items` 或 `failed`

## VC Checklist

### VC-1 Artifact 链
- [ ] manifest、inventory、source_index、outline、evidence、draft、review 存在

### VC-2 Tier 合规
- [ ] critical claim 只用 T0/T1
- [ ] 历史项目 `SystemArchitecture` file_id 不出现在 `evidence_map` / `claim_support_matrix`

### VC-3 Requirement 规则
- [ ] ID 唯一
- [ ] `shall` / `应` 句式
- [ ] `SWR-IF.Direction` 取值合法
- [ ] 数值带单位

### VC-4 Forbidden 内容
- [ ] 无 HARA / ASIL / SG / TSR / TSC
- [ ] 无 Software Architecture / detailed design 终稿字段
- [ ] 无 `approved` / `compliant` / `production ready`

### VC-5 HITL 与状态
- [ ] `NEEDS_USER_CONFIRMATION` 未被静默改 confirmed
- [ ] candidate 仍为 `inactive` / `proposed`

## From-Scratch

- [ ] open 多不等于失败
- [ ] 没证据的时序/资源值必须保持 open

## With-SystemArchitecture-Reference

- [ ] 机器扫描历史架构 file_id 不得进入事实证据链
- [ ] `SEC-DIFF` 存在且非空

## Review 要点

| 检查点 | 通过条件 |
|---|---|
| 规则一致性 | 字段、枚举、ID、单位符合约束 |
| tier 纯度 | 参考资料完全隔离于事实证据链 |
| 状态保守 | 只允许保守状态，不出现批准/合规状态 |
| 控制完整 | HITL、candidate、open 项控制没有失效 |

## 常见 P0

- 历史架构 file_id 进入 evidence_map
- 接口方向空白却标 confirmed
- 静默填值且无 EVD 无 open
- 状态写成 `approved` 或 `compliant`

## A1 / A2 / B

**A1**：规则验证通过，P0 清零。  
**A2**：回 Step 10 修正后重验。
**B**：验证是守门，不是替代工程判断或人工批准。
