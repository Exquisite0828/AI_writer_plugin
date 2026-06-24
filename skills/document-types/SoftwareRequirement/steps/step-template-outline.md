# SwRS 子 skill · Step 4 · 模板大纲

骨架：`skills/workflow-steps/step-template-outline/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 产出 `outline_l1.md`、`outline_l2.md`、`template_structure.json`
- 定义 SwRS 章节与表列，不写正文
- 明确区分软件需求、软件架构、软件设计

## 强制 L1 Checklist

- [ ] `SEC-SCOPE`
- [ ] `SEC-INPUT`
- [ ] `SEC-SWCTX`
- [ ] `SEC-UPTRACE`
- [ ] `SEC-FUNC`
- [ ] `SEC-IF`
- [ ] `SEC-TIME`
- [ ] `SEC-RESOURCE`
- [ ] `SEC-DIAG`
- [ ] `SEC-TRACE`
- [ ] `SEC-VERIF`
- [ ] `SEC-ASSUMP`
- [ ] `SEC-REVIEW`

## L2 表列 Checklist

### `SEC-FUNC`
- [ ] `SWR-F ID`
- [ ] `Requirement statement`
- [ ] `Linked upstream ID`
- [ ] `Architecture context`
- [ ] `Verification method`
- [ ] `Evidence source`
- [ ] `Confirmation status`

### `SEC-IF`
- [ ] `SWR-IF ID`
- [ ] `Interface name`
- [ ] `Direction`
- [ ] `Counterpart`
- [ ] `Trigger / timing`
- [ ] `Requirement statement`
- [ ] `Evidence source`
- [ ] `Confirmation status`

### `SEC-TIME / SEC-RESOURCE / SEC-DIAG`
- [ ] 时序值/工况/单位列
- [ ] 资源约束列（CPU、RAM、NVM、调度依赖等）
- [ ] 诊断触发、检测、响应、降级行为列

## Forbidden Checklist

- [ ] 不含 HARA / FSR / TSR / TSC / Software Architecture / Unit Design 章节
- [ ] 不含模块设计、线程设计、类设计、状态机实现细节章节
- [ ] 不含批准、合规、量产结论章节

## From-Scratch

- [ ] 缺证据章节只保留占位，不在大纲中假设内容完整
- [ ] `SEC-SAFE-SW` 可为 optional/open

## With-SystemArchitecture-Reference

- [ ] 增加 `SEC-DIFF`
- [ ] `SEC-DIFF` 仅比较差异类型，不承载参考资料事实
- [ ] 不从历史架构继承表列中的默认值

## Review 要点

| 检查点 | 通过条件 |
|---|---|
| 结构正确 | 章节能覆盖 SWE.1 软件需求分析 |
| 层级正确 | 需求章节不越界到架构/设计 |
| 接口完备 | `Direction`、`Counterpart`、`Trigger / timing` 列齐全 |
| 参考边界 | 参考架构只影响 shape，不影响事实列内容 |

## 常见 P0

- 大纲出现架构/设计终稿章节
- `SEC-IF` 无 `Direction`
- `SEC-DIFF` 缺失但却存在大量参考使用场景

## A1 / A2 / B

**A1**：大纲覆盖完整、层级正确。  
**A2**：补列、删越界章节、补 `SEC-DIFF`。  
**B**：后续正文只能沿本步定义的列写，不得擅自扩成设计文档。
