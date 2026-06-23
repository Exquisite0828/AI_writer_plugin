# HARA 子 skill · Step 8 · 章节任务 (Section Tasks)

本文件是通用骨架 `skills/workflow-steps/step-section-tasks/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 把 citation_plan 各 HARA 章节转为逐章节写作任务 `TASK-xxx`，确定 writing_mode（supported / conservative_candidate / confirmation_required / open_issue_list / unsupported_stub）。
- 为每个任务登记来源支撑、claim 状态（needs_confirmation/supported/…）与 future_output_path。
- 渲染最终大纲 `plans/outline_final.md` 与写作计划 `plans/writing_plan.md`（含 supported/mixed/unsupported/需确认任务统计）。
- HARA critical claim（hazard/S-E-C/ASIL/safety goal/final acceptability）相关章节无 T0/T1 支撑时 writing_mode 取 confirmation_required / open_issue_list，保持 open/pending。
- 保留 strict_template 强制章节，只规划"写什么、用哪些来源"，不在此步生成正文。
- **底线**：不得为缺证据的 HARA 章节预设 hazard/rating/ASIL/safety goal 结论。

## HARA 报告过程总览（本步定位）

12 节 HARA 报告每节对应一个或多个写作任务。本步把章节 + citation_plan 拆解为可执行的 TASK-xxx 列表。

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


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA 章节写作任务清单

按 template_structure 章节顺序，应生成以下 TASK-xxx 写作任务：

| TASK-ID | 章节 | writing_mode | 产出描述 | HITL 依赖 |
|---|---|---|---|---|
| TASK-01 | SEC-DOC | supported | 文档信息表（标题/版本/日期/作者/状态）+ 修订历史表格 | 否 |
| TASK-02 | SEC-SCOPE | supported | item 名称确认、分析目的、适用标准（ISO 26262-3）、范围声明（包含/不包含）| 否 |
| TASK-03 | SEC-REF | supported | 参考文件清单（来自 manifest 中的输入材料）+ ISO 26262 条款引用列表 | 否 |
| TASK-04 | SEC-TERMS | supported | HARA 术语定义表：Hazard/HE/S/E/C/ASIL/SG/HITL/NEEDS_USER_CONFIRMATION 等 | 否 |
| TASK-05 | SEC-ITEM | conservative_candidate | item 功能清单（F-xx）+ 系统边界表（In/Out of scope）+ 外部接口表（IF-xx）+ 运行约束；缺失项标 NEEDS_USER_CONFIRMATION | 是 |
| TASK-06 | SEC-OPS | conservative_candidate | 运行工况表（OS-xx）：每行含 ID/描述/道路类型/速度/交通/天气/驾驶员状态；来自 T1 source；覆盖高速/城市/停车场/恶劣天气 | 是 |
| TASK-07 | SEC-HAZ | confirmation_required | 危害识别表（H-xx）：对每个功能 F-xx 用引导词法分析；每行含 ID/危害描述/相关功能/失效类型/状态；缺 T1 支撑则 NEEDS_USER_CONFIRMATION | 是 |
| TASK-08 | SEC-HE | confirmation_required | 危害事件表（HE-xxx）：H×OS 组合，每行含 ID/H-ID/OS-ID/危害事件描述/成立性；不成立组合注明理由 | 是 |
| TASK-09 | SEC-SEC-S | confirmation_required | S 评级列：每个 HE 的 S 候选值及文字依据（ISO 26262-3 Table 1 框架 + T1 source 支撑）；标 NEEDS_USER_CONFIRMATION | 是 |
| TASK-10 | SEC-SEC-E | confirmation_required | E 评级列：每个 HE 的 E 候选值及文字依据（ISO 26262-3 Table 2 框架 + T1 source 支撑）| 是 |
| TASK-11 | SEC-SEC-C | confirmation_required | C 评级列：每个 HE 的 C 候选值及文字依据（ISO 26262-3 Table 3 框架 + T1 source 支撑）| 是 |
| TASK-12 | SEC-ASIL | confirmation_required | ASIL 候选列：由 S/E/C 候选值依 ISO 26262-3 Table 4 查表；所有值标 NEEDS_USER_CONFIRMATION | 是 |
| TASK-13 | SEC-SG | confirmation_required | 安全目标表（SG-xx）：仅对 ASIL候选 > QM 的 HE 生成；每行含 ID/描述/ASIL候选/相关HE-ID/状态 | 是 |
| TASK-14 | SEC-OPEN | open_issue_list | 开放问题清单：汇总所有 NEEDS_USER_CONFIRMATION 项，分类（item定义/危害/评级/安全目标）| 否 |
| TASK-15 | SEC-REVIEW | supported | 审查总结（保守措辞）：分析覆盖范围、已支撑项统计、开放项数量、状态声明 | 否 |

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
1. 遍历 outline_final 各章节。
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
