# SwRS 子 skill · Step 5 · 大纲分析与写作计划

骨架：`skills/workflow-steps/step-research-questions/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 为每个 L2 建 `section_writing_plans.json`
- 定义 `required_evidence`、`writing_mode_hint`、`subtasks`
- 不写正文，只规划如何写

## 默认 `sp-*` Checklist

- [ ] `sp-uptrace`：上游需求/架构来源确认
- [ ] `sp-func`：软件功能需求写作计划
- [ ] `sp-if`：接口需求写作计划
- [ ] `sp-time`：时序/性能计划
- [ ] `sp-resource`：资源约束计划
- [ ] `sp-diag`：诊断/降级计划
- [ ] `sp-safe`：安全相关软件需求引用计划
- [ ] `sp-trace`：双向追溯计划
- [ ] `sp-verif`：验证方法计划
- [ ] `sp-diff`：仅 With-Reference 时启用

## writing_mode_hint Checklist

- [ ] `supported`：T0/T1 证据充分
- [ ] `conservative_candidate`：证据部分充分
- [ ] `confirmation_required`：关键字段待确认
- [ ] `placeholder_only`：只有占位和 open

## 计划内容 Checklist

- [ ] 每条 `SWR-F` 计划都指定上游需求与架构上下文
- [ ] 每条 `SWR-IF` 计划都指定方向、对端、触发/时序来源
- [ ] 时序/资源计划明确数值来源或确认路径
- [ ] 诊断计划区分“触发条件”“软件响应”“降级行为”
- [ ] 任何缺口都转成 open，不写 `supported`

## From-Scratch

- [ ] 没有当前项目架构支撑的需求不能标 `supported`
- [ ] 验证方法默认 `confirmation_required`
- [ ] 资源/时序章节通常更偏 `placeholder_only`

## With-SystemArchitecture-Reference

- [ ] 历史项目架构不得进入任何 `required_evidence`
- [ ] `sp-diff` 必须存在
- [ ] “与参考类似”不能作为计划依据，只能形成 review question

## Review 要点

| 检查点 | 通过条件 |
|---|---|
| 证据前置 | 每个计划项都知道该去哪里找证据 |
| 写作模式保守 | 证据不足时不冒进 |
| 架构使用边界 | 当前项目架构可入计划，历史项目架构不可入 `required_evidence` |
| 追溯闭环 | `sp-trace` 覆盖上游到 SwRS 及反向检查 |

## 常见 P0

- 把历史架构列为 `required_evidence`
- 无证据章节标 `supported`
- `sp-diff` 缺失却需要处理参考资料

## A1 / A2 / B

**A1**：每个章节有计划、写作模式合理。  
**A2**：修正 `required_evidence`、降级过度乐观模式、补 `sp-diff`。  
**B**：Step 6 只能基于本步计划去取证与建 TASK。
