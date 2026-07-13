# Software Architecture 子 skill · Step 5 · 大纲分析与写作计划

骨架：`skills/workflow-steps/step-research-questions/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点

- 遍历 `outline_l2.md` 每 L2，登记 `research_state.subtasks`（`sp-*`）。
- 产出 `section_writing_plans.json`：**不写正文**；不做 ASPICE 合规结论。
- 为 Step 6 证据映射提供「每节需要什么 T0/T1」的前置规划。

## Software Architecture 方法论（本步定位）

### 5.1 本步在八阶段方法链中的位置

本步对应 **阶段 3：逐段分析与写作计划**。在建立 EVD 之前，先回答：**这一节要从哪份 source 的哪段找证据？缺什么？用什么 writing_mode？**

**方法原则**：计划只列 T0/T1 `required_evidence`；缺证据标 `confirmation_required` 或 `placeholder_only`，**禁止**标 `supported`。

### 5.2 阶段 3 · 写作计划（本步执行）

#### 通用逐 L2 分析方法

对每个 L2 执行四问：

1. **写什么**：对应 SWE.2 哪类架构信息（静态/动态/接口/分配/约束）？
2. **证据从哪来**：哪份 source 的哪个 topic（Step 3 索引）？
3. **缺什么**：无 L3 锚点则记入 `open_questions`。
4. **怎么写**：`writing_mode_hint` 取值。

#### 默认子任务（sp-*）与 SWE.2 映射

| id | L2 | SWE.2 方向 | required_evidence |
|---|---|---|---|
| sp-swctx | SEC-SWCTX | 范围与上下文 | software_context + current_system_architecture |
| sp-uptrace | SEC-UPTRACE | 追溯入口 | swrs_source |
| sp-logarch | SEC-LOGARCH | 静态-逻辑 | software_context / swrs_source |
| sp-physarch | SEC-PHYSARCH | 静态+动态 | rte_bsw_constraints / os_cfg |
| sp-comp | SEC-COMP | 静态-组件 | swrs_source + software_context |
| sp-if | SEC-IF | 接口 | interface_spec / rte_config |
| sp-alloc | SEC-ALLOC | 追溯+分配 | swrs_source（双向） |
| sp-diag | SEC-DIAG | 约束 | diagnostic_constraints |
| sp-safe-arch | SEC-SAFE-ARCH | 安全引用 | tsr_or_safety_sw（仅引用） |
| sp-res | SEC-RES | 资源/实时 | platform_constraints + rte_bsw |
| sp-verif | SEC-VERIF | 验证 | checklist / confirmation_required |
| sp-assump | SEC-ASSUMP | 假设 | gaps + constraints |
| sp-review | SEC-REVIEW | 审查 | checklist coverage |
| sp-diff | SEC-DIFF | Δ-Analysis | **仅 With-Reference**；非 sample 事实 |

#### writing_mode_hint 判定规则

| 模式 | 判定条件 |
|---|---|
| supported | 该 L2 所有 critical 字段均有 T0/T1 锚点 |
| conservative_candidate | 有部分 T1，关键字段仍缺 |
| confirmation_required | 分配/方向/资源预算等关键字段缺 source |
| placeholder_only | 几乎无 source，仅保留表头与 `[PENDING]` |

#### From-Scratch 方法要点

| L2 | 典型 writing_mode | 方法说明 |
|---|---|---|
| SEC-ALLOC | confirmation_required | 逐条规划 SwRS→组件，无依据不填 |
| SEC-IF | confirmation_required | 逐接口规划方向来源 |
| SEC-RES | confirmation_required / placeholder | 资源预算无 source 则 pending |
| SEC-PHYSARCH | conservative_candidate | 任务表可部分来自 BSW/OS 配置 |
| sp-diff | 不创建 | 无 SEC-DIFF 计划 |

#### With-Reference 方法要点

| 动作 | 方法说明 |
|---|---|
| sp-diff 强制 | 必建；子任务覆盖 Added/Removed/Modified/Scope-changed |
| 不得列 sample | 历史 SwAD **不得**出现在任何 `required_evidence` |
| 差异规划 | 每类差异规划「本项目 evidence 从哪来」，不是「参考有什么」 |
| 模式可放宽 | 可有更多 conservative_candidate，但 sp-alloc/sp-if 仍须逐条证据规划 |

### 5.3 计划产出检查（交 Step 6 的输入）

- 每个 `sp-alloc` 子任务应含：SwRS ID 列表、候选组件来源 file_id、rationale 证据点。
- 每个 `sp-if` 子任务应含：Direction 证据点或 `direction_open`。

## 本步 Review / Checklist 要点

### ASPICE SWE.2 写作计划 Checklist（sp-* 与 BP 对齐）

| sp-* | L2 | SWE.2 BP | 计划须含 |
|---|---|---|---|
| sp-uptrace | SEC-UPTRACE | BP5/BP6 | SwRS ID 列表、来源 file_id |
| sp-logarch | SEC-LOGARCH | BP1 | 逻辑块证据点或 placeholder |
| sp-physarch | SEC-PHYSARCH | BP2 | 任务/BSW 证据点或 open |
| sp-comp | SEC-COMP | BP1 | 组件候选来源、Layer 依据 |
| sp-if | SEC-IF | BP1 | Direction 证据点或 direction_open |
| sp-alloc | SEC-ALLOC | BP5/BP6 | 逐条 SwRS→组件规划、rationale 点 |
| sp-diag | SEC-DIAG | BP1/BP2 | 诊断链 source 或 open |
| sp-safe-arch | SEC-SAFE-ARCH | ISO 26262-6 | 仅引用规划，无新分析子任务 |
| sp-res | SEC-RES | BP2 | 资源/时序证据或 pending |
| sp-verif | SEC-VERIF | BP3/BP7 | 验证候选或 confirmation |
| sp-diff | SEC-DIFF | — | **仅 With-Reference**；四类 Δ 子任务 |

### ISO 26262-6 计划 Checklist

- [ ] sp-safe-arch 子任务 **不**含 HARA/ASIL 分析步骤
- [ ] sp-safe-arch 的 `required_evidence` 仅 TSR/软件安全 source
- [ ] 无「推导安全机制」「判定 ASIL」类子任务

### 通用 Checklist（10 项）

- [ ] 每个 L2 有 `section_writing_plans.json` 条目或显式 gap
- [ ] 每条 plan 含：`section_id`、`subtasks[sp-*]`、`required_evidence`、`writing_mode_hint`
- [ ] `required_evidence` **仅** T0/T1 source，不含 T4/T5
- [ ] 无证据段 `writing_mode_hint` ≠ `supported`
- [ ] sp-alloc 每行规划：SwRS ID、组件来源、rationale 证据点
- [ ] sp-if 每接口规划：Direction 来源或 `direction_open`
- [ ] 计划不含 HARA/TSR 新编/详细设计/批准意图
- [ ] `research_state.subtasks` 全部 done 或失败原因记录
- [ ] 计划与 `outline_l2.md` L2 一一对应
- [ ] open_questions 与 gap 一致

### writing_mode 判定 Review

| 模式 | 允许条件 | Review 拒绝条件 |
|---|---|---|
| supported | 该 L2 全部 critical 字段有 T0/T1 | 任一关键字段无 L3 锚点 |
| conservative_candidate | 部分 T1，关键字段仍缺 | 无任一 EVD 规划却标此模式 |
| confirmation_required | 分配/方向/资源缺 source | 有完整 source 却标此模式（浪费） |
| placeholder_only | 几乎无 source | 有 source 却标 placeholder |

### From-Scratch 专属 Checklist

- [ ] sp-alloc / sp-if 多为 `confirmation_required` 或 `placeholder_only`
- [ ] **无** sp-diff 子任务
- [ ] sp-res / sp-physarch 缺 OS 配置时为 placeholder
- [ ] 无证据 L2 不得标 `supported`（**P0**）

### With-Reference 专属 Checklist

- [ ] **sp-diff 必须存在**，含 Added/Removed/Modified/Scope-changed 子任务
- [ ] 历史 SwAD **不得**列入任何 `required_evidence`（**P0**）
- [ ] Δ 子任务规划「本项目 evidence 从哪来」，非「参考有什么」
- [ ] 可更多 conservative_candidate，但 sp-alloc/sp-if 仍逐条规划

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 证据规划 | 多 confirmation/placeholder | 多 conservative_candidate，仍逐条 |
| required_evidence | 仅本项目 source/HITL | 历史 SwAD 绝不列入 |
| sp-diff | 不存在 | 强制且四类齐全 |
| 安全计划 | sp-safe-arch 为引用或 placeholder | 不可规划「抄参考安全架构」 |

### P0 失效项

| 失效 | 后果 |
|---|---|
| 无证据标 supported | Step 7 静默填值 |
| sample/历史 SwAD 作 required_evidence | 事实来源违规 |
| With-Reference 缺 sp-diff | Δ 分析缺失 |
| sp-safe-arch 含新安全分析步骤 | 文档边界破坏 |

### P1 失效项

- sp-* 与 L2 漏映射
- writing_mode 与 required_evidence 矛盾
- open_questions 未回写 knowledge_gaps

### 一句话归纳

**Checklist 核心**：每 L2 有计划、证据仅 T0/T1、writing_mode 与证据匹配、无 supported 造假。  
**Review 核心**：From-Scratch 查 confirmation 密度；With-Reference 查 sp-diff 与 sample 未入 required_evidence。

## A1 / A2 / B

**A1**：research_state 完成；每 L2 有计划；模式与证据匹配。  
**A2**：重做失败 sp-*；修正 writing_mode。  
**B**：计划与 Step 3 topic_index 一致，可驱动 Step 6。
