# HARA 子 skill · Step 8 · 章节任务 (Section Tasks)

本文件是通用骨架 `skills/workflow-steps/step-section-tasks/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 把 citation_plan 各 HARA **L1 章与 L2 小节**转为逐节写作任务 `TASK-xxx`，确定 writing_mode（supported / conservative_candidate / confirmation_required / open_issue_list / unsupported_stub）。
- 为每个任务登记来源支撑、claim 状态（needs_confirmation/supported/…）、`section_id`（L2）/ `parent_section_id`（L1）与 future_output_path。
- 渲染最终大纲 `plans/outline_final.md`（合并 Step 4 的 L1+L2 与引用计划后的可写结构）与写作计划 `plans/writing_plan.md`（含 supported/mixed/unsupported/需确认任务统计）。
- HARA critical claim（hazard/S-E-C/ASIL/safety goal/final acceptability）相关章节无 T0/T1 支撑时 writing_mode 取 confirmation_required / open_issue_list，保持 open/pending。
- 保留 strict_template 强制章节，只规划"写什么、用哪些来源"，不在此步生成正文。
- **底线**：不得为缺证据的 HARA 章节预设 hazard/rating/ASIL/safety goal 结论。

## HARA 报告过程总览（本步定位）

12 节 HARA 报告每 L1 章对应一个或多个写作任务；章内 **L2 小节**（来自 `outline_l2.md`）可拆为子任务。本步把章节 + citation_plan 拆解为可执行的 TASK-xxx 列表。

**HARA 写作任务与章节映射**：

| 章节 ID | 主要任务类型 | 是否依赖 HITL |
|---|---|---|
| SEC-ITEM | 提取 item 功能 / 边界 / 接口 / 约束 | 部分 |
| SEC-OPS | 列出运行工况表 | 部分 |
| SEC-HAZ | 引导词法识别危害（候选） | ★ |
| SEC-HE | 危害 × 工况组合分析 | ★ |
| SEC-SEC | S/E/C 评级 + ASIL 查表 | ★ |
| SEC-SG | ASIL>QM 的 HE 生成安全目标 | ★ |
| SEC-OPEN | 汇总所有 NEEDS_USER_CONFIRMATION | — |
| SEC-REVIEW | 覆盖范围 / 开放项 / 状态声明 | — |

**本步定位**：固化任务粒度与 `writing_mode`；HITL 依赖任务的 critical claim 默认保持 pending。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`section_tasks.json`）将在 Step 10/11 被以下检查点定位。subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| RD-1 | 任务覆盖 12 个 mandatory section | 每个 section_id 至少有 1 条 TASK-xxx |
| RD-3 | SEC-HAZ 任务驱动引导词覆盖 | TASK-HAZ-xx 引用 Q-HAZ 问题集，覆盖 ≥ 2 种引导词 |
| RD-5 | SEC-SG 任务仅覆盖 ASIL>QM 的 HE | TASK-SG-xx 关联 ASIL > QM 的 HE 列表 |
| RD-6 | SEC-OPEN 任务存在 | 必有 TASK-OPEN-xx 汇总 `NEEDS_USER_CONFIRMATION` |
| 根 skill | writing_mode 标 confirmation_required 时不预设结论 | 缺证据章节的 writing_mode 为 `confirmation_required` / `open_issue_list` |

**自检底线**：本步只规划"写什么、用哪些来源"，不在此步生成正文；HITL 依赖任务的 critical claim 默认保持 pending。



## ISO 26262-3 标准 Checklist 与 Review 要点（Clause 对照）

本步对应 Phase F1/F2/F3（Safety Goal 推导与聚合）任务编排，同时为 Phase C/D/E 的写作任务确定边界。

### Checklist（任务编排）

- [ ] 12 个 mandatory section 均有 ≥ 1 条 TASK-xxx
- [ ] TASK-HAZ-xx 覆盖 ≥ 2 种 HAZOP 引导词（与 Step 5 问题集一致）
- [ ] **TASK-SG-xx 仅关联 ASIL > QM 的 HE**（ISO 26262-3 §6.4.4）
- [ ] 每条 TASK-SG-xx 任务输出含：SG 文本（禁止性表述）+ Safe State + **FTTI**（§7.4.2.4 强制）+ Emergency Operation（若无法立即达 safe state）
- [ ] TASK-SG 聚合任务存在（合并相似 SG，ASIL 取最高，§7.4.4）
- [ ] 必有 TASK-OPEN-xx 汇总 `NEEDS_USER_CONFIRMATION`
- [ ] 缺证据章节的 `writing_mode` 为 `confirmation_required` / `open_issue_list`
- [ ] With-Reference 情景：必有 TASK-DIFF-xx（Δ-Analysis 章节写作任务）

### Review 要点

| 失效 | 级别 |
|---|---|
| 任一 mandatory section 无任务 | **P0** |
| TASK 含 hazard / ASIL / SG 结论预设 | **P0** |
| ASIL > QM 的 HE 无 TASK-SG-xx 覆盖 | **P0** |
| TASK-SG 未要求 FTTI / Safe State 字段 | **P0** |
| SG 聚合任务缺失（多个相似 SG 散乱） | **P1** |
| With-Reference 情景缺 TASK-DIFF | **P0** |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 任务来源 | 严格按 Step 4 大纲展开 | 在 From-Scratch 任务上叠加 TASK-DIFF（差异分析章节写作） |


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA 章节写作任务清单

按 `outline_l2.md` 与 `template_structure`（L1 + level=2 节点）顺序生成 TASK-xxx；**SEC-ITEM 等多 L2 章宜按 L2 拆任务**：

| TASK-ID | L1 / L2 | writing_mode | 产出描述 | HITL 依赖 |
|---|---|---|---|---|
| TASK-01 | SEC-DOC | supported | 文档信息表（标题/版本/日期/作者/状态）+ 修订历史表格 | 否 |
| TASK-02 | SEC-SCOPE | supported | item 名称确认、分析目的、适用标准（ISO 26262-3）、范围声明（包含/不包含）| 否 |
| TASK-03 | SEC-REF | supported | 参考文件清单（来自 manifest 中的输入材料）+ ISO 26262 条款引用列表 | 否 |
| TASK-04 | SEC-TERMS | supported | HARA 术语定义表：Hazard/HE/S/E/C/ASIL/SG/HITL/NEEDS_USER_CONFIRMATION 等 | 否 |
| TASK-05a | SEC-ITEM · 功能清单（L2） | conservative_candidate | F-xx 功能清单；缺失项标 NEEDS_USER_CONFIRMATION | 是 |
| TASK-05b | SEC-ITEM · 系统边界（L2） | conservative_candidate | In/Out of scope 边界表 | 是 |
| TASK-05c | SEC-ITEM · 外部接口（L2） | conservative_candidate | IF-xx 外部接口表 | 是 |
| TASK-05d | SEC-ITEM · 运行约束（L2） | conservative_candidate | 速度/环境/车型等运行约束 | 是 |
| TASK-06 | SEC-OPS · OS-xx 工况表（L2） | conservative_candidate | 运行工况表（OS-xx）：每行含 ID/描述/道路类型/速度/交通/天气/驾驶员状态；来自 T1 source | 是 |
| TASK-07 | SEC-HAZ · H-xx 危害表（L2） | confirmation_required | 危害识别表（H-xx）：对每个功能 F-xx 用引导词法分析 | 是 |
| TASK-08 | SEC-HE · HE-xxx 表（L2） | confirmation_required | 危害事件表（HE-xxx）：H×OS 组合 | 是 |
| TASK-09 | SEC-SEC · S 评级（L2） | confirmation_required | 每个 HE 的 S 候选值及文字依据 | 是 |
| TASK-10 | SEC-SEC · E 评级（L2） | confirmation_required | 每个 HE 的 E 候选值及文字依据 | 是 |
| TASK-11 | SEC-SEC · C 评级（L2） | confirmation_required | 每个 HE 的 C 候选值及文字依据 | 是 |
| TASK-12 | SEC-SEC · ASIL 候选（L2） | confirmation_required | 由 S/E/C 依 ISO 26262-3 Table 4 查表 | 是 |
| TASK-13 | SEC-SG · SG-xx 表（L2） | confirmation_required | 安全目标表：仅对 ASIL候选 > QM 的 HE 生成 | 是 |
| TASK-14 | SEC-OPEN | open_issue_list | 开放问题清单：汇总所有 NEEDS_USER_CONFIRMATION 项 | 否 |
| TASK-15 | SEC-REVIEW | supported | 审查总结（保守措辞）：分析覆盖范围、已支撑项统计、开放项数量 | 否 |

若 Step 4 的 `outline_l2.md` 与上表 L2 划分不一致，**以 outline_l2 为准**映射 TASK，上表作 HARA 默认参考。

### TASK-07~12 的关联关系说明

- TASK-07（危害 H-xx）是 TASK-08（危害事件 HE-xxx）的前置输入
- TASK-08（HE-xxx）是 TASK-09/10/11（S/E/C 评级）的前置输入
- TASK-09/10/11 结果组合后通过查表生成 TASK-12（ASIL 候选）
- TASK-12（ASIL > QM 的 HE）决定 TASK-13（哪些 HE 需要安全目标）

每个 TASK 的 `claim_status` 字段取值：`supported` / `needs_confirmation` / `open`

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按 artifact/章节逐项核对。
- 方案C 先扫高风险约束（strict_template 强制章节保留与无证据章节标 open/pending）再补其余。

### 典型审核子任务
1. 核对章节任务是否只规划"写什么、用哪些来源"而未生成正文。
2. 核对 strict_template 强制章节是否保留。
3. 核对无证据 HARA 章节是否标注 open/pending、critical claim 章节 writing_mode 是否保守。
4. 核对 section_tasks/writing_plan 是否符合 artifact 契约。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 一节一任务直接映射。
- 方案B 按章节复杂度拆粗/细粒度任务。
- 方案C 按证据充分度分组（充分/待证）排序任务。

### 典型修订子任务
1. 遍历 `outline_final.md` 各 L1 章与 L2 小节。
2. 为每节建写作任务（含引用槽与约束、确定 writing_mode）。
3. 标注依赖与 HITL pending（critical claim 章节）。
4. 汇总 writing_plan 并校验章节覆盖完整。

## state.json 示例（HARA）

```json
{
  "step": "section-tasks",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对章节任务只规划而未生成正文", "status": "done"},
      {"id": "rv-2", "desc": "核对 strict_template 强制章节保留", "status": "running"},
      {"id": "rv-3", "desc": "核对无证据 HARA 章节标注 open/pending", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "遍历 outline_final 各章节", "status": "done"},
      {"id": "rt-2", "desc": "为每节建写作任务并确定 writing_mode", "status": "running"},
      {"id": "rt-3", "desc": "标注依赖与 critical claim HITL pending", "status": "not_run"},
      {"id": "rt-4", "desc": "汇总 writing_plan 并校验覆盖完整", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：章节任务是否只规划"写什么、用哪些来源"而未生成正文；strict_template 强制章节是否保留；无证据 HARA 章节是否标注 open/pending，critical claim 章节的 writing_mode 是否取保守值（confirmation_required / open_issue_list）。
