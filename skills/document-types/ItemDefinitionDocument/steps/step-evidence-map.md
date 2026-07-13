# IDD 子 skill · Step 6 · 证据·引用·章节计划

骨架：`skills/workflow-steps/step-evidence-map/SKILL.md`。领域规则：`skills/document-types/ItemDefinitionDocument/SKILL.md`。

## 本步目的要点（三阶段顺序）

### Phase A · 证据映射

- 按 `section_writing_plans.json` 每段 `required_evidence`：**L1→L2→L3→原文** → `EVD-xxx`。
- 未解决 → `unresolved_questions.md`。
- critical claim（功能/边界/接口/误用等）仅 T0/T1；T4 sample **禁止**。

### Phase B · 引用计划

- claim ↔ EVD → `citation_plan.json`、`claim_support_matrix.json`。
- claim 类型：`item_function`、`system_boundary`、`external_interface`、`environment_constraint`、`operational_situation`、`assumption`、`foreseeable_misuse`、`item_dependency`。
- 缺证据 → `NEEDS_USER_CONFIRMATION`，不编造引用。

### Phase C · 章节任务

- `TASK-xxx`：`writing_mode`、`allowed_evidence`（EVD）、`section_id`。
- `outline_final.md`、`section_tasks.json`、`writing_plan.md`。
- 只规划不写正文。

## IDD 方法论（本步定位）

本步对应 **阶段 4：证据映射 → 引用计划 → 章节任务**，是 IDD 可追溯性的核心环节。

### 阶段 4a · 证据映射

把每条功能、边界、接口、误用等 **追溯到具体来源位置**（文档 + L1/L2/L3 + 摘录）：

- 有来源：标 **已支撑**，生成 `EVD-xxx`。
- 无来源：标 **未解决 / open**，写入 `unresolved_questions.md`。

### 阶段 4b · 引用计划

为每个 critical 陈述规划 **引用槽**：

- 哪条 F-xx 引用哪份 SyRS 哪段。
- 哪条 IF-xx 引用哪份接口规范哪张表。
- 缺证据的 claim 保留 **NEEDS_USER_CONFIRMATION**，**不编造引用**。

### 阶段 4c · 章节任务

把大纲拆成 **逐节写作任务**：

| writing_mode | 含义 |
|---|---|
| supported | 证据充分，可支撑表述 |
| conservative_candidate | 保守候选，措辞受限 |
| confirmation_required | 须 HITL 确认 |
| placeholder_only | 仅占位 |

**产出**：`evidence_map`、`citation_plan`、`claim_support_matrix`、`section_tasks`（对应 workflow Step 6 三阶段）。

### critical claims（须 T0/T1 或 open）

- item 功能描述（F-xx）的准确性与完整性
- 系统边界（In / Out of scope）
- 外部接口定义（信号/机械/人机，**含方向**）
- 运行环境与操作约束
- 运行工况与模式描述（事实性，非危害结论）
- 假设与依赖
- 合理可预见误用场景
- Item 间交互与依赖关系

## IDD 证据 tier

| tier | 用途 |
|---|---|
| T0 | HITL 确认 |
| T1 | 项目 source（SyRS、架构、接口规范等） |
| T2 | template / checklist（结构） |
| T3 | reference（Clause 5 方法框架，不单独证明本项目事实） |
| T4 | sample（**禁止**作 critical claim 事实） |
| T5 | 推断（不支撑 critical claim） |

## TASK 映射示例

| TASK | L2 | writing_mode |
|---|---|---|
| TASK-FUNC | F-xx 表 | conservative_candidate |
| TASK-BOUND-IN | In scope | conservative_candidate |
| TASK-BOUND-OUT | Out scope | conservative_candidate |
| TASK-IF | IF-xx（含方向） | conservative_candidate |
| TASK-ENV | 环境约束 | conservative_candidate |
| TASK-OPS | OS-xx / 模式 | conservative_candidate |
| TASK-ASSUMP | 假设依赖 | confirmation_required |
| TASK-MISUSE | 误用表 | confirmation_required |
| TASK-OPEN | 开放项 | open_issue_list |

## execution_state 示例

```json
{
  "step": "evidence-map",
  "execution_state": {
    "phases": [
      {"id": "phase-a", "name": "证据映射", "subtasks": [{"id": "em-func", "section_id": "SEC-FUNC-L2-01", "status": "not_run"}]},
      {"id": "phase-b", "name": "引用计划", "subtasks": [{"id": "cp-core", "desc": "FUNC/BOUNDARY/IF matrix", "status": "not_run"}]},
      {"id": "phase-c", "name": "章节任务", "subtasks": [{"id": "st-all", "status": "not_run"}]}
    ]
  }
}
```

## 本步 Review / Checklist 要点

本步产出是 Step 9 **VC-2**（tier 合规、L1/L2/L3 provenance）的核心检查对象。

### Critical Claims 与证据要求（本步须落实）

以下内容属于 critical claim，须有 **T0/T1** 支撑，或保持 `NEEDS_USER_CONFIRMATION`：

- F-xx 功能描述的准确性与完整性
- 系统边界（In / Out of scope）
- 外部接口（**含方向**）
- 运行环境与操作约束
- 运行工况与模式（事实性，非危害结论）
- 假设与依赖
- 合理可预见误用场景
- Item 间交互与依赖关系

### 证据 tier 规则（审查对照）

| Tier | 用途 | critical claim |
|---|---|---|
| T0 | HITL 确认 | 允许 |
| T1 | 项目 source | 允许 |
| T2 | template / checklist | 仅结构 |
| T3 | reference（Clause 5 框架） | 不单独证明项目事实 |
| T4 | sample | **禁止** |
| T5 | 推断 | **禁止** |

### 与本步相关的 artifact 检查

- [ ] 每条 F/IF/边界 EVD 含 L1/L2/L3 provenance
- [ ] `claim_support_matrix` 中 critical claim 无 T4/T5 支撑
- [ ] 缺证据 claim 标 `NEEDS_USER_CONFIRMATION`，未编造 citation
- [ ] 误用 claim 有 EVD 或进入 `unresolved_questions.md`
- [ ] `section_tasks.json` 的 `allowed_evidence` 与 matrix 一致
- [ ] claim 类型无 hazard/ASIL/SG

### 本步 Review 要点

| 维度 | 检查项 | 级别 |
|---|---|---|
| 证据匹配 | claim ↔ EVD 一一对应 | P0 |
| tier 合规 | critical claim 无 T4/T5 | P0 |
| 接口方向 | IF EVD 含方向信息 | P0 |
| 缺口诚实性 | 无 EVD 的 claim 标 open | P0 |
| 边界双向 | In/Out 均有 TASK 与 EVD 或 open | P1 |
| IDD 纯净性 | matrix 无 hazard 类 claim | P0 |

## 常见错误（本步重点防）

| 错误 | 后果 | 级别 |
|---|---|---|
| sample 支撑 F-xx/边界 EVD | 事实来源违规 | P0 |
| 接口 EVD 无方向信息 | 后续 IF-xx 缺方向 | P0 |
| 误用无 EVD 且无 open | §5.4.4 b 不满足 | P0 |
| 编造 citation 填补缺口 | 不可追溯 | P0 |
| claim 类型含 hazard/ASIL | 文档类型漂移 | P0 |

## A1 / A2 / B

**A1**：七类 artifact 齐全；EVD↔matrix↔TASK 一致；无 hazard 内容；sample 未入 matrix。  
**A2**：失败 phase 重跑。  
**B**：接口含方向；误用节有来源或 open；边界 In/Out 均有 TASK。
