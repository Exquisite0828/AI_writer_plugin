---
name: step-source-index
description: 中文优先指导 workflow 第 3 步「文档目录索引」：遍历阅读已解析输入文档，按语义与实际结构为每份文档建立一级/二级/三级目录，生成跨文档导航索引与单文档目录树，供 Agent 经 L1→L2→L3 定位后访问原文。
---

# Step 3 · 文档目录索引 (Document Navigation Index)

工作流第 3 步。基于材料清单，**逐份阅读**已解析的输入文档，像为一本书建立目录那样，根据文档实际结构与语义划分**一级目录（L1）**、**二级目录（L2）**、**三级目录（L3）**，并产出可被 Agent **按 L1→L2→L3 顺序**逐级浏览的导航索引，以便后续步骤定位「内容在哪几份文档、经哪三级目录、在原文的具体位置」。

本步**不做**草稿、审查、专业判断或 claim 结论；也**不在此步**把 sample/reference 当作项目事实证据。

## 何时使用

- 已完成 Step 2（材料清单）。
- 需要为后续研究问题、证据检索、引用计划提供「先读索引、再读原文」的文档导航基础。

## 输入

- `inputs/input_inventory.json`
- 已解析材料的原文或抽取文本（按 `file_id` / `path` 读取）

## 执行方法（必做）

1. **遍历文档**：对 `input_inventory.json` 中 `parse_status=parsed` 的每一份输入材料，完整阅读（或分段阅读并汇总），不得跳过。
2. **识别三级结构**：结合文档自身标题层级、章节编号、表格/附录边界与语义主题，判断 L1（章/大主题）、L2（节/子主题）、L3（可独立定位的最细单元，如小节、表格块、条目组）；名称须反映实际内容，不得硬套固定模板。
3. **记录位置**：**`location` 挂在 L3 叶子节点**（若某分支确实无法分出 L3，则 L2 作叶子并在 `knowledge_gaps.md` 说明；仍须先走 L1→L2 再读该 L2）。
4. **撰写摘要**：为每个 L1/L2/L3 写简短 `brief`（L3 必填，L1/L2 可选），便于 Agent 逐级筛选而不打开全文。
5. **建立跨文档主题索引**：在 `source_index.json` 的 `topic_index` 汇总跨文档主题，每条指向 `file_id` + L1/L2/L3 + 位置锚点。
6. **产出可读目录**：为每份已索引文档生成 `knowledge/document_tocs/<file_id>.md`，采用 **L1 → L2 → L3** 书籍目录风格，供 Agent **首先且必须**按此顺序浏览。

## 产出 artifacts

| 路径 | 用途 |
|---|---|
| `knowledge/source_index.json` | **跨文档导航总索引**：文档清单 + 主题/关键词 → 文档与 L1/L2/L3 位置 |
| `knowledge/provenance_index.json` | **各文档三级语义目录树**：L1→L2→L3 层级、L3 位置锚点、role/tier 元数据 |
| `knowledge/document_tocs/<file_id>.md` | **单文档可读目录**（每份已解析文档一份），Agent 优先访问 |
| `knowledge/knowledge_gaps.md` | 未能建立目录的材料、结构不清的章节、解析/定位失败说明 |

## source_index.json（跨文档导航总索引）

Top-level 建议字段：

1. `run_id`
2. `generated_at`
3. `documents` — 已建立目录的文档摘要列表
4. `topic_index` — 跨文档主题检索入口
5. `summary`

`documents[]` 每项建议字段：

1. `file_id`
2. `path`
3. `role`
4. `title`
5. `parse_status`
6. `toc_ref` — 对应 `knowledge/document_tocs/<file_id>.md`
7. `l1_count` / `l2_count` / `l3_count`
8. `document_brief` — 全文一句话概述

`topic_index[]` 每项建议字段：

1. `topic_id`
2. `topic` — 主题名称（中文优先）
3. `keywords` — 检索关键词
4. `locations[]` — 命中位置列表，每项含 `file_id`、`l1_title`、`l2_title`、`l3_title`、`anchor`、`line_start`、`line_end`（可用则填）

## provenance_index.json（各文档语义目录树）

Top-level 建议字段：

1. `schema_version` — 建议 `document_toc.v1`
2. `run_id`
3. `generated_at`
4. `task_type`
5. `documents` — 每份文档的完整 L1→L2→L3 树

每份 `documents[]` 建议字段：

1. `file_id`
2. `path`
3. `title`
4. `role`
5. `source_tier` — 保留 N4 tier 元数据（见下），供后续步骤识别材料性质
6. `is_fact_source`
7. `parse_status`
8. `toc` — L1→L2→L3 目录树

`toc[]`（L1）每项建议字段：

1. `l1_id`
2. `l1_title`
3. `l2_entries[]`

`l2_entries[]` 每项建议字段：

1. `l2_id`
2. `l2_title`
3. `l3_entries[]`

`l3_entries[]` 每项建议字段（**叶子节点，原文定位挂在此**）：

1. `l3_id`
2. `l3_title`
3. `brief` — 本单元内容摘要（1–2 句）
4. `location` — `{ section, anchor, page, line_start, line_end, char_start, char_end }`（按文档实际情况填写，缺失字段留空/null，不得伪造）

## document_tocs/<file_id>.md（单文档可读目录）

每份文档一份，建议结构：

```markdown
# 文档目录 · {title}
- file_id: {file_id}
- path: {path}
- role: {role}

## 一级目录 · {l1_title}
### 二级目录 · {l2_title}
- **三级目录 · {l3_title}** → {path} · {section/anchor} · L{line_start}–{line_end}
  - 摘要：{brief}
```

Agent 访问任何原始输入文档时，**必须**按 **L1 → L2 → L3** 顺序浏览本文件（或 `provenance_index.json` 中等价树），**仅在最末 L3（或 gap 说明下的 L2 叶子）** 才按 `location` 打开原文。**禁止**跳过目录层级直接打开全文。

## N4 Source Tier（元数据，非本步主任务）

目录索引须保留每份材料的 role/tier 元数据，供后续步骤区分材料性质；**建立目录不等于把材料升格为事实证据**：

- `T0`：HITL / 人工确认
- `T1`：项目 source
- `T2`：template / checklist
- `T3`：reference 方法学
- `T4`：sample 风格
- `T5`：生成 / 未知 / 不支持推断

`sample` / `expected_output_shape` 可以建立**导航目录**（便于看结构与写法），但必须在元数据中标记 `is_fact_source=false`，且不得在此步写入任何项目事实结论。

## 边界与约束

- 目录必须来自**实际阅读**后的结构与语义，不得用固定章节模板硬套所有文档。
- L1/L2/L3 划分应「像一本书的目录」：L1=章，L2=节，L3=可独立定位的最细单元（段落组/表格/条目）；若文档结构不足三级，在 `knowledge_gaps.md` 说明，且 Agent 仍须先读已有 L1/L2 再读 L2 叶子原文。
- 每个 L3（或 gap 下的 L2 叶子）必须能回溯到具体 `file_id` 与 `location`；provenance 为空视为 P1 缺陷。
- `missing` / `unsupported` / `failed` 的材料不得假装已索引；写入 `knowledge_gaps.md`。
- 解析失败、结构无法识别、位置无法确定时必须显式报告，禁止静默跳过。
- 本步只建索引与目录，不填充 hazard/rating/ASIL/测试结论等专业判断。

## 加载任务专属子 skill（必做）

本步是**通用骨架**，只定义流程、artifact 契约与角色边界。执行前，subagent 必须按 `task_type` 加载对应的任务专属子 skill：

- 路径：`skills/document-types/<task_type>/steps/step-source-index.md`
- 例：`task_type: hara` → `skills/document-types/hara/steps/step-source-index.md`，并配合根 skill `skills/document-types/<task_type>/SKILL.md`。

从子 skill 获取本步的：本步目的要点、A1/A2 候选方案示例与典型子任务、state.json 子任务文案、B 审核检查项及领域规则。若该子 skill 文件缺失，必须显式报告并停下确认，不得用通用占位静默推进。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。**本步任务专属候选方案见所加载子 skill 的「A1 审核任务」。**
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。**本步任务专属的典型审核子任务见所加载子 skill 的「A1 审核任务 · 典型审核子任务」。**
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步要完成的目的（见所加载子 skill 的「本步目的要点」）自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。**本步任务专属候选方案见所加载子 skill 的「A2 修订任务」。**
2. **分解与执行（第一性原理：以「单份文档 / 一个 L1 章节」为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。**本步任务专属的典型修订子任务见所加载子 skill 的「A2 修订任务 · 典型修订子任务」。**
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构（本步通用 schema；子任务 `desc` 文案见所加载子 skill 的「state.json 示例」）：

```json
{
  "step": "<step-id>",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "<本步审核子任务，见子 skill>", "status": "done"},
      {"id": "rv-2", "desc": "<本步审核子任务，见子 skill>", "status": "running"},
      {"id": "rv-3", "desc": "<本步审核子任务，见子 skill>", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "<本步修订子任务，见子 skill>", "status": "done"},
      {"id": "rt-2", "desc": "<本步修订子任务，见子 skill>", "status": "running"},
      {"id": "rt-3", "desc": "<本步修订子任务，见子 skill>", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（见上「产出 artifacts」）与本文「边界与约束」+ 所加载子 skill 的「B 审核检查项」作为审核标准。
2. subagent 按所加载子 skill 的「B 审核检查项」逐项核对本步产出。
3. **发现问题时修订（提取本步目的、自主重新驱动）**：先从所加载子 skill 的「本步目的要点」读取本步要达成的目的，再由 subagent 围绕这些目的自主重新驱动完成本步任务。**底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 4 · 模板大纲**（`template_structure.json` + `outline_l1.md` + `outline_l2.md`）。**Step 4 及以后**读 template/sample/reference 原文须 **L1→L2→L3→原文**（见 writing-core），不得 chunk/SRC/全文盲搜。
