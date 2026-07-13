# HARA 子 skill · Step 5 · 大纲分析与写作计划

本文件是通用骨架 `skills/workflow-steps/step-research-questions/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA）

- 对 Step 4 的 **L1 章 + L2 小节**（`outline_l1.md` + `outline_l2.md`）**逐段分析研究**，为 HARA 报告每一小段产出**写作计划**。
- 按 L2 登记分析子任务（`sp-*`）于 `research_state.subtasks`，**顺序执行**：读该段 intent → 读 T0/T1 材料（L1→L2→L3）→ 结合 ISO 26262-3 / HARA 经验 → 写出该段写作计划。
- 每完成一段，追加到 `section_writing_plans.json`，子任务 `done` 并**立即更新worker内部进度**。
- **底线**：计划可描述表格形状、引导词扫描步骤、需 HITL 的 critical 项；**不得**在计划中写入已确认的 hazard/rating/ASIL/SG 结论；不得用 T4 sample 当事实依据。

## HARA 默认分析子任务（初始化 research_state）

按 `outline_l2.md` 顺序生成 `sp-*`；与下表不一致时**以 outline_l2 为准**。

| id | section_id（L2 示例） | parent | desc |
|---|---|---|---|
| sp-01 | SEC-DOC L2 | SEC-DOC | 分析文档元信息/修订历史段，产出表格写作计划 |
| sp-02 | SEC-SCOPE L2 | SEC-SCOPE | 分析范围与目的段，产出范围声明写作计划 |
| sp-03 | SEC-REF L2 | SEC-REF | 分析参考文件段，产出引用清单写作计划 |
| sp-04 | SEC-TERMS L2 | SEC-TERMS | 分析术语段，产出术语表写作计划 |
| sp-05 | 功能清单 L2 | SEC-ITEM | 读 item T1 材料，产出 F-xx 功能表写作计划 |
| sp-06 | 系统边界 L2 | SEC-ITEM | 读边界材料，产出 In/Out scope 表写作计划 |
| sp-07 | 外部接口 L2 | SEC-ITEM | 读接口材料，产出 IF-xx 表写作计划 |
| sp-08 | 运行约束 L2 | SEC-ITEM | 读 ODD/约束材料，产出约束表写作计划 |
| sp-09 | OS-xx 工况表 L2 | SEC-OPS | 读工况 T1 材料，产出 OS-xx 表与暴露基础写作计划 |
| sp-10 | H-xx 危害表 L2 | SEC-HAZ | 读功能/失效材料，产出引导词法危害表写作计划 |
| sp-11 | HE-xxx 表 L2 | SEC-HE | 产出 H×OS 危害事件表写作计划 |
| sp-12 | S 评级 L2 | SEC-SEC | 产出 S 评级列写作计划（Table 1 框架 + T1 依据位） |
| sp-13 | E 评级 L2 | SEC-SEC | 产出 E 评级列写作计划（Table 2 + T1 工况频率位） |
| sp-14 | C 评级 L2 | SEC-SEC | 产出 C 评级列写作计划（Table 3 + 驾驶员响应位） |
| sp-15 | ASIL 候选 L2 | SEC-SEC | 产出 ASIL 查表列写作计划（Table 4，全部 HITL） |
| sp-16 | SG-xx 表 L2 | SEC-SG | 产出安全目标表写作计划（含 Safe State / FTTI 列） |
| sp-17 | SEC-OPEN | SEC-OPEN | 产出开放项汇总段写作计划 |
| sp-18 | SEC-REVIEW | SEC-REVIEW | 产出审查总结段写作计划 |

With-Reference 须增 **sp-DIFF**：差异分析段写作计划（sample 只借结构）。

## 单子任务执行指引

### 通用步骤（每个 sp-*）

1. 读 `outline_l2.md` 该节 `intent`、`evidence` 预期。
2. `topic_index` → `document_tocs` L1→L2→L3 → 读 T0/T1/T3 原文。
3. 填写该段写作计划字段（见主 skill）；HARA critical 段 `requires_human_confirmation: true`。
4. 可选写 `plans/section_plans/<section_id>.md`；子任务 `done`；更新worker内部进度。

### SEC-HAZ（sp-10）· 危害表写作计划要点

计划须包含：

- `content_outline`：H-xx 表列（ID / 危害描述 / 相关功能 F-xx / 失效类型 / 状态）
- `writing_steps`：对每个 F-xx 按 **≥2 种** HAZOP 引导词组织行（必含 Unintended / Spurious 之一）
- `required_evidence`：每项 H-xx 需 T1 功能/失效描述或 HITL
- `writing_mode_hint`：`confirmation_required`

| 引导词 | 失效类型 |
|---|---|
| No Function | 功能缺失 |
| More Function | 功能过强 |
| Less Function | 功能过弱 |
| Wrong Direction | 错误方向 |
| Unintended Function | 非预期激活 |
| Too Early / Too Late | 时序错误 |

## HARA 各 L2 写作计划参考（content_outline 示例）

#### SEC-ITEM · 功能清单（sp-05）

- `writing_intent`：列出 item 全部主要功能 F-xx
- `content_outline`：表格列 ID / 功能名称 / 功能描述 / 来源 / 状态
- `writing_steps`：① 从 T1 提取功能名 ② 逐行填描述 ③ 缺项标 NEEDS_USER_CONFIRMATION
- `writing_mode_hint`：`conservative_candidate`

#### SEC-OPS · OS-xx 工况表（sp-09）

- `content_outline`：OS-xx 表：ID / 描述 / 道路 / 速度 / 交通 / 天气 / 驾驶员 / 暴露说明
- `required_evidence`：T1 工况定义、ODD、场景分析
- Checklist：道路类型、速度分段、交通、环境、路面、驾驶员、载重、维护、降级（B1）

#### SEC-SEC · S/E/C/ASIL（sp-12–15）

- 各列独立计划；ASIL 计划须引用 Table 4 查表步骤，**不写最终 ASIL 值**
- SG（sp-16）：仅 ASIL>QM 的 HE；禁止性表述；Safe State + FTTI 列（§7.4.2.4）

#### SEC-OPEN / SEC-REVIEW（sp-17–18）

- OPEN：按 item/危害/评级/SG 分类汇总 NEEDS_USER_CONFIRMATION
- REVIEW：覆盖度统计、开放项数量、Confirmation Review 占位

### 计划 status 规则

- `ready`：T0/T1 材料足以按计划成稿（非 critical 或已有充分 T1）
- `partial`：有部分材料，critical 或部分行须 HITL
- `blocked`：gap 或无 L3 入口，仅能写 stub / open 列表

## 本步将被审查的关键点

| 检查 | 方法 |
|---|---|
| 流程 | research_state 全部 `done` |
| 覆盖 | 每个 outline_l2 有对应计划条目 |
| RD-3 | sp-10 计划含 ≥2 引导词步骤 / F-xx |
| 根 skill | 计划无 hazard/ASIL/SG **结论性**措辞 |
| sample | source_hints 无 T4 作事实 |

## ISO 26262-3 覆盖（写入各段计划）

- **A3**（sp-02/04）：方法声明、团队组成 → 写入 SCOPE/TERMS 或独立 L2 计划
- **B1/B2**（sp-09）：工况与模式 → OS 表计划 Checklist
- **C1**（sp-10）：HAZOP 引导词 → H 表 writing_steps
- **E/F**（sp-12–16）：S/E/C/ASIL/SG 表形状与 HITL 要求

| 失效 | 级别 |
|---|---|
| 某 F-xx 计划仅 No Function 一种引导词 | **P0** |
| 计划写入已确认 ASIL/SG | **P0** |
| outline_l2 缺对应计划 | **P0** |

## A1 审核任务（HARA）

### 典型审核子任务

1. `research_state` 全部 `done` 且与 outline_l2 一一对应。
2. 每段计划含 `writing_intent`、`content_outline`、`writing_steps`、`required_evidence`。
3. critical 段标 `requires_human_confirmation`；blocked/partial 有 `gaps`。
4. `section_writing_plans.json` 字段完整、无预设 hazard/rating/ASIL 结论。

## A2 修订任务（HARA）

1. 失败 `sp-*` 置 `not_run`，顺序重跑。
2. 重读材料 L1→L2→L3，更新该段计划条目。
3. 合并 `section_writing_plans.json`。

## section_writing_plans.json 单条示例（HARA · SEC-ITEM 功能清单）

```json
{
  "section_id": "SEC-ITEM-L2-01",
  "parent_section_id": "SEC-ITEM",
  "title": "功能清单",
  "writing_intent": "列出 item 全部主要功能 F-xx，供后续 HAZOP 使用",
  "content_outline": ["表格：F-ID", "功能名称", "功能描述", "T1 来源", "状态"],
  "writing_steps": [
    "从 item 定义 T1 材料提取功能列表",
    "为每功能分配 F-xx ID",
    "缺描述行标 NEEDS_USER_CONFIRMATION"
  ],
  "required_evidence": ["item 功能定义", "系统规格中的功能章节"],
  "source_hints": [
    {"file_id": "item-spec-01", "l1": "系统功能", "l2": "功能列表", "l3": "EPS 功能", "purpose": "提取 F-xx 名称与描述"}
  ],
  "research_notes": "材料含 5 项功能，第 3 项描述不完整",
  "gaps": ["F-03 详细行为描述缺失"],
  "writing_mode_hint": "conservative_candidate",
  "requires_human_confirmation": true,
  "status": "partial"
}
```

## B 审核检查项（HARA）

Stage review worker 核对：outline_l2 每段是否有计划；计划是否只描述「怎么写」而未写 hazard/rating/ASIL/SG 结论；critical 段是否标 HITL；是否未用 T4 sample 作事实；sp-10 是否含充分引导词写作步骤。
