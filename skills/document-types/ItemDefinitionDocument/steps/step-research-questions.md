# IDD 子 skill · Step 5 · 大纲分析与写作计划

骨架：`skills/workflow-steps/step-research-questions/SKILL.md`。领域规则：`skills/document-types/ItemDefinitionDocument/SKILL.md`。

## 本步目的要点

- 遍历 `outline_l2.md` 每 L2，登记 `research_state.subtasks`（`sp-*`），状态 `not_run|running|done`。
- 顺序执行：读 L2 intent → L1→L2→L3 读 T0/T1/T3 → 产出该段**写作计划** → 合并 `section_writing_plans.json`。
- 计划字段：`writing_intent`、`content_outline`、`writing_steps`、`required_evidence`、`source_hints`、`gaps`、`writing_mode_hint`。
- **不写正文**；不写 hazard/ASIL。

## IDD 方法论（本步定位）

本步对应 **阶段 3：逐段分析与写作计划**——对大纲每一小节制定「写什么、用什么证据、缺什么」的计划。

### 阶段 3 · 逐段分析与写作计划（本步执行）

对每一 L2 小节：

1. 明确本节 **要写什么、表格长什么样**。
2. 明确需要哪些 **T0/T1 证据**（来自哪份 SyRS/架构/接口文档的哪一段）。
3. 经 Step 3 索引 **L1→L2→L3→原文** 阅读来源，记录 **已有 / 缺失**。
4. 输出该节的 **写作计划**（先写什么、后写什么、缺什么标 open）。

**产出**：`section_writing_plans.json`（对应 workflow Step 5）。

### 成功标准（审查视角，本步须预判）

- 功能、边界、接口、环境、工况、假设、误用各段均有计划或显式 gap。
- 接口段计划 **强制含方向列**。
- 边界段计划 **In 与 Out 双向**。
- 误用段计划 **单独成节**，不藏在假设段。
- 全文计划 **无危害分析结论**。

## 默认子任务（与 outline_l2 对齐，示例）

| id | L2 示例 | desc | required_evidence 要点 |
|---|---|---|---|
| sp-ident | SEC-IDENT | Item 名称/版本/变型写作计划 | 项目 charter、SyRS 封面 |
| sp-func | SEC-FUNC · F-xx 表 | 功能清单计划 | SyRS/SRS 功能描述（§5.4.2） |
| sp-bound-in | SEC-BOUNDARY · In | In scope 计划 | 架构 scope 图/说明（§5.4.3） |
| sp-bound-out | SEC-BOUNDARY · Out | Out scope 计划 | 架构 scope 图/说明（§5.4.3） |
| sp-if | SEC-IF · IF-xx | 接口表计划（**含方向**） | 接口规范、信号方向 |
| sp-env | SEC-ENV | 环境约束计划 | ODD、环境规范（§5.4.4） |
| sp-ops | SEC-OPS · OS-xx | 工况/模式计划 | 场景说明（事实性，非 E 评级） |
| sp-assump | SEC-ASSUMP | 假设依赖计划 | 假设清单（§5.4.4） |
| sp-misuse | SEC-MISUSE | 误用场景计划 | §5.4.4 b 相关材料 |
| sp-dep | SEC-DEP | Item 交互计划 | 系统架构、接口依赖 |
| sp-open | SEC-OPEN | 开放项框架 | 前述各段 gaps 汇总 |
| sp-review | SEC-REVIEW | 审查总结计划 | checklist 覆盖度 |

### writing_mode_hint 指引

| 模式 | 适用 |
|---|---|
| supported | T0/T1 证据充分 |
| conservative_candidate | 有部分证据，表述保守 |
| confirmation_required | 关键 claim 缺 T0/T1 |
| placeholder_only | 仅结构占位 |

## 本步 Review / Checklist 要点

本步产出 `section_writing_plans.json` 将在 Step 8「证据匹配」与 Step 9 VC-1 artifact 链检查时被回溯。

### 与本步相关的写作计划检查

- [ ] 每强制 L2（IDENT/FUNC/BOUNDARY/IF/ENV/OPS/ASSUMP/MISUSE）均有计划或 gap
- [ ] `required_evidence` 仅引用 T0/T1/T3，**不引用 T4 sample**
- [ ] 边界计划拆分为 In + Out（sp-bound-in / sp-bound-out）
- [ ] IF 计划含方向列与对端字段规划
- [ ] 误用计划（sp-misuse）独立，未合并进假设计划
- [ ] 缺 T0/T1 段标 `confirmation_required` 或 `placeholder_only`，非 `supported`
- [ ] 计划中无 hazard/ASIL/SG 写作意图

### 本步 Review 要点

| 维度 | 检查项 | 级别 |
|---|---|---|
| 与需求对齐 | F-xx 计划引用 SyRS/SRS 证据 | P1 |
| 与架构对齐 | 边界计划引用架构 scope | P1 |
| 接口完整性 | IF 计划含方向、对端 | P0 |
| 误用独立性 | MISUSE 独立计划 | P0 |
| 工况事实性 | OPS 计划无 E 评级意图 | P0 |
| 缺口诚实性 | gaps 字段已填写 | P0 |
| 证据 tier | 无 sample 作 required_evidence | P0 |

### 本步自检（交付前）

- [ ] `research_state` 全部 `sp-*` 为 done
- [ ] 每 L2 的 `writing_mode_hint` 与证据充分性一致
- [ ] SEC-OPEN 计划汇总了前述各段 gaps

## 常见错误（本步重点防）

| 错误 | 后果 | 级别 |
|---|---|---|
| 计划引用 sample 作 required_evidence | 事实来源违规 | P0 |
| 误用段合并进假设段计划 | §5.4.4 b 不满足 | P0 |
| 无证据段标 supported | 后续静默填值 | P0 |
| 计划中含 hazard/ASIL 写作意图 | 文档类型漂移 | P0 |

## A1 / A2 / B

**A1**：research_state 全 done；每 L2 有计划；无 sample 事实；critical 段标 HITL。  
**A2**：重做失败 `sp-*`，合并 JSON。  
**B**：计划覆盖 Clause 5 全部强制章；接口含方向；边界 In/Out 双向。
