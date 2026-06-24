# Software Architecture 子 skill · Step 6 · 证据·引用·章节计划

骨架：`skills/workflow-steps/step-evidence-map/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点（三阶段顺序，**必须按序执行**）

### Phase A · 证据映射

- **L1→L2→L3→原文** → `EVD-xxx`；critical claim 仅 T0/T1。
- 每条 EVD 对应一个可审查的架构断言（组件定义、接口方向、分配理由等）。

### Phase B · 引用计划

- 建立 `claim_support_matrix.json`：claim 类型 ↔ EVD ↔ tier。
- 缺证据 → `NEEDS_USER_CONFIRMATION`，写入 `unresolved_questions.md`。

### Phase C · 章节任务

- `TASK-xxx` + `outline_final.md`、`section_tasks.json`、`writing_plan.md`。
- 每个 TASK 声明 `allowed_evidence` 列表，供 Step 9 严格使用。

## Software Architecture 方法论（本步定位）

### 6.1 本步在八阶段方法链中的位置

本步对应 **阶段 4：证据映射 → 引用计划 → 章节任务**。这是 **从计划到可写草稿** 的关键桥梁：Step 9 只能使用本步批准的 EVD。

**方法原则**：一条架构事实 = 一条 claim = 零或一条/multiple EVD（T0/T1）或 explicit open。禁止 blanket EVD 支撑整表。

### 6.2 Phase A · 证据映射方法

#### 通用 EVD 建立流程

```text
1. 从 section_writing_plans 取 sp-* 清单
2. 按 topic_index 定位 L3
3. 摘录原文 → 创建 EVD（含 excerpt、tier、claim_tags）
4. 无 L3 可引用 → unresolved_questions.md
```

#### claim 类型与 SWE.2 对齐

| claim_type | 含义 | 典型章节 |
|---|---|---|
| architecture_wording | 架构表述 | 各章 |
| upstream_swrs_linkage | SwRS 追溯 | SEC-UPTRACE、SEC-ALLOC |
| system_architecture_context | 系统架构上下文 | SEC-SWCTX |
| component_definition | 组件定义 | SEC-COMP |
| software_interface_architecture | 软件接口 | SEC-IF |
| allocation_rationale | 分配理由 | SEC-ALLOC |
| task_scheduling_architecture | 任务/调度 | SEC-PHYSARCH、SEC-RES |
| diagnostic_architecture | 诊断链路 | SEC-DIAG |
| resource_timing_budget | 资源/时序 | SEC-RES |
| safety_architecture_linkage | 安全引用 | SEC-SAFE-ARCH |
| verification_method | 验证方法 | SEC-VERIF |
| architecture_completeness_consistency | 完整性/一致性 | SEC-REVIEW |

#### From-Scratch 方法要点

- 预期大量 unresolved；**正常**。
- 分配矩阵：每行至少 1 个 `upstream_swrs_linkage` EVD 或该行 status=open。
- 接口：无 direction EVD 则 Direction 列=NEEDS_USER_CONFIRMATION。
- SEC-SAFE-ARCH：无 TSR source 则整节 placeholder。

#### With-Reference 方法要点

- 历史 SwAD file_id **禁止**出现在任何 EVD 的 `source_file_id`。
- Δ 相关 claim 的 EVD 只能来自本项目 SwRS/架构/平台 source。
- 可建 `claim_type=reference_shape_only` 且 tier=T4，但 **不得** 进入 critical claim matrix。

### 6.3 Phase B · 引用计划方法

- 同一 SwRS ID 的分配理由应引用 SwRS 原文 EVD，而非二次 paraphrase 无来源。
- 接口 Direction 应有 interface_spec 或 rte_config 的 L3 摘录支撑。
- SEC-SAFE-ARCH：每个引用约束独立 EVD，禁止一条 FSR 摘录支撑全部安全架构。

### 6.4 Phase C · 章节任务方法

#### TASK 映射（默认）

| TASK | L2 | 典型 writing_mode |
|---|---|---|
| TASK-SWCTX | SEC-SWCTX | conservative_candidate |
| TASK-UPTRACE | SEC-UPTRACE | conservative_candidate |
| TASK-LOGARCH | SEC-LOGARCH | conservative_candidate |
| TASK-PHYSARCH | SEC-PHYSARCH | conservative_candidate |
| TASK-COMP | SEC-COMP | conservative_candidate |
| TASK-IF | SEC-IF | confirmation_required |
| TASK-ALLOC | SEC-ALLOC | confirmation_required |
| TASK-DIAG | SEC-DIAG | conservative_candidate |
| TASK-SAFE-ARCH | SEC-SAFE-ARCH | confirmation_required / placeholder |
| TASK-RES | SEC-RES | confirmation_required |
| TASK-VERIF | SEC-VERIF | confirmation_required |
| TASK-OPEN | SEC-OPEN | open_issue_list |
| TASK-DIFF | SEC-DIFF | **仅 With-Reference** |

#### allowed_evidence 规则

- Step 9 正文 **只能**引用 TASK 的 `allowed_evidence` 中的 EVD ID。
- open 项以 `NEEDS_USER_CONFIRMATION` 关键字写入正文，也算显式输出。

## 本步 Review / Checklist 要点

### ASPICE SWE.2 证据链 Checklist（三阶段总览）

| Phase | SWE.2 支撑 | 通过条件 |
|---|---|---|
| **A 证据映射** | BP1/BP2/BP5 事实基础 | 组件/接口/分配/资源 claim 有 EVD 或 unresolved |
| **B 引用计划** | BP5/BP6 追溯与一致性 | matrix 覆盖 claim_type；缺证据→open |
| **C 章节任务** | BP4/BP7 可成稿 | TASK↔matrix 一致；allowed_evidence 明确 |

### Phase A · 证据映射 Checklist（12 项）

- [ ] 每条组件定义 claim 有 `EVD-xxx` 或 `unresolved_questions.md`
- [ ] 每条接口架构 claim（含 **Direction**）有 EVD 或 unresolved
- [ ] 每条分配 rationale claim 有 EVD 或 unresolved
- [ ] 每条资源/时序预算 claim 有 EVD 或 unresolved
- [ ] 每条诊断架构 claim 有 EVD 或 unresolved
- [ ] 每个 EVD 含：`source_file_id`、L1、L2、L3、`location`、`excerpt`、`tier`
- [ ] critical claim 的 tier **仅** T0/T1
- [ ] T4/T5 **不支撑** critical claim
- [ ] **当前项目** System Architecture 可作 `system_architecture_context` EVD
- [ ] **历史 SwAD** 不出现在任何 EVD `source_file_id`（**P0**）
- [ ] SEC-SAFE-ARCH 的 EVD **不超出**显式 TSR/软件安全引用范围
- [ ] 无编造 citation / 无虚假 L3 锚点

### Phase B · 引用计划 Checklist（claim_support_matrix）

- [ ] 覆盖 claim_type：`architecture_wording`、`upstream_swrs_linkage`、`component_definition`、`software_interface_architecture`、`allocation_rationale`、`task_scheduling_architecture`、`diagnostic_architecture`、`resource_timing_budget`、`safety_architecture_linkage`、`verification_method`、`architecture_completeness_consistency`
- [ ] 每条 claim 有 EVD 或 `NEEDS_USER_CONFIRMATION`
- [ ] 同一 EVD 不 blanket 支撑无关 claim
- [ ] 接口 claim 的 matrix 行含 direction 字段或 open 标记
- [ ] SwRS 分配 claim 可追溯到 SWR-F/IF 的 L3 摘录

### Phase C · 章节任务 Checklist

- [ ] `section_tasks.json` 与 matrix、outline_final 一致
- [ ] 每个 TASK 有 `allowed_evidence` 列表
- [ ] TASK-ALLOC / TASK-IF 的 writing_mode 与证据匹配
- [ ] TASK-OPEN 汇总 unresolved
- [ ] **With-Reference**：含 **TASK-DIFF**，allowed_evidence **不含**历史 SwAD 事实

### ISO 26262-6 证据 Checklist

- [ ] `safety_architecture_linkage` claim 仅有 TSR/软件安全 source 的 EVD
- [ ] 无 EVD 支撑「安全机制已实现」「故障探测已覆盖」类断言
- [ ] 无 HARA/ASIL 字段进入 matrix

### From-Scratch 专属 Checklist

- [ ] 大量 `confirmation_required` / `placeholder_only` TASK 属正常
- [ ] unresolved 数量与 Step 5 预测一致，未为减少而删 open
- [ ] 分配矩阵每行至少 1 个上游 EVD 或显式 unresolved

### With-Reference 专属 Checklist

- [ ] matrix 中**无**「历史 SwAD 支撑组件/接口/分配/资源」行（**P0**）
- [ ] TASK-DIFF 的 `allowed_evidence` 仅本项目 source
- [ ] 可存在 tier=T4 的 `reference_shape_only` 记录，但 **不进入** critical matrix

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| EVD 密度 | 低 + 多 unresolved 正常 | 可略高，但仍逐条 |
| 编造风险 | 无 L3 却建 EVD → P0 | 历史 SwAD 进 EVD → P0 |
| SEC-SAFE-ARCH | 多 placeholder | 不抄参考安全 EVD |
| TASK 可执行性 | allowed_evidence 窄而明确 | TASK-DIFF 证据范围清楚 |

### P0 失效项

| 失效 | 后果 |
|---|---|
| 历史 SwAD 进 evidence_map/matrix | 事实来源违规 |
| 编造上游链接/citation | 不可追溯 |
| TASK-ALLOC 标 supported 但无 allowed_evidence | 草稿编造分配 |
| SEC-SAFE-ARCH blanket 支撑全部架构 | 安全边界错误 |
| T4 支撑 critical claim | tier 违规 |

### P1 失效项

- EVD excerpt 与 L3 原文不一致
- matrix 缺 claim_type 枚举
- section_tasks 与 outline_final 章节 ID 不一致

### 一句话归纳

**Checklist 核心**：三 phase 齐全、EVD↔matrix↔TASK 一致、tier 合规、无 sample 支撑 critical claim。  
**Review 核心**：From-Scratch 查 unresolved 诚实；With-Reference 查历史 SwAD 未进 EVD/matrix。

## A1 / A2 / B

**A1**：三 phase 产物齐全；EVD↔matrix↔TASK 一致。  
**A2**：失败 phase 重跑；修正 tier。  
**B**：Step 9 可仅凭 allowed_evidence 成稿。
