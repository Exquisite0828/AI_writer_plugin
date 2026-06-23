---
name: step-evidence-map
description: 中文优先指导 workflow 第 6 步「证据映射」：由 evidence-run 生成 evidence_map.json 与 unresolved_questions.md；须按 L1→L2→L3 定位原文后摘录 EVD 证据，把研究问题映射到具体文档位置。
---

# Step 6 · 证据映射 (Evidence Map)

工作流第 6 步。把研究问题映射到**具体文档位置**上的来源证据：须遵守 **L1 → L2 → L3 → 原文** 访问协议，在 L3（或 gap 说明下的 L2 叶子）精读并生成 `EVD-xxx`，标记哪些有支撑、哪些仍未解决。

## 何时使用

- 已完成 Step 5（研究问题）。
- 需要在写作前确认每个关键问题是否有可回溯的文档位置与摘录支撑。

## 输入

- `plans/research_questions.json`
- `knowledge/source_index.json`（`topic_index`）
- `knowledge/provenance_index.json`（L1→L2→L3 目录树与 L3 `location`）
- `knowledge/document_tocs/`
- `knowledge/knowledge_gaps.md`
- 已解析材料的原文或抽取文本（按 provenance 定位后读取）

## 输入文档访问约定（强制，见 writing-core）

对每个 research question：

1. （可选）`topic_index` 命中 `file_id` + L1/L2/L3 候选路径
2. 打开 `document_tocs/<file_id>.md`，**按 L1 → L2 → L3 逐级**选定目标叶子
3. 从 `provenance_index` 取该 L3 的 `location`，**仅此时**打开原文
4. 摘录生成 `EVD-xxx`：provenance = `file_id` + L1/L2/L3 + `location` + `snippet`（摘自原文）
5. 无 L3 入口或 gap 已登记 → `unresolved_questions.md`

**禁止**：不经过三级目录直接打开输入文件；使用 `SRC-xxx` / `sources[]` chunk；把目录 `brief` 当作 EVD 正文。

## 产出 artifacts

- `plans/evidence_map.json`
- `plans/unresolved_questions.md`

## 边界与约束

- 证据候选必须经 **L1→L2→L3→阅读原文** 产生；`EVD-xxx` provenance 须含 `file_id` + L1/L2/L3 + `location`，禁止旧版 chunk/SRC 或直接全文盲搜。
- 只允许用 T0/T1 来源支撑 critical claim；T3/T4/T5 不能单独支撑。
- 没有证据或无法定位原文的问题写入 `unresolved_questions.md`，保持 open，不得推断填补。
- sample/reference 不能作为事实证据进入证据映射；sample 目录（T4）仅用于结构参考，不得从中摘录 hazard/rating 等作为 EVD。

## 加载任务专属子 skill（必做）

本步是**通用骨架**，只定义流程、artifact 契约与角色边界。执行前，subagent 必须按 `task_type` 加载对应的任务专属子 skill：

- 路径：`skills/document-types/<task_type>/steps/step-evidence-map.md`
- 例：`task_type: hara` → `skills/document-types/hara/steps/step-evidence-map.md`，并配合根 skill `skills/document-types/<task_type>/SKILL.md`。

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
2. **分解与执行（第一性原理：以本步的自然工作单元为单位）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。**本步任务专属的典型修订子任务见所加载子 skill 的「A2 修订任务 · 典型修订子任务」。**
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

进入 **Step 7 · 引用计划**（`citation_plan.json` + `claim_support_matrix.json`）。
