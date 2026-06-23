# HARA 子 skill · Step 3 · 来源索引 (Source Index)

本文件是通用骨架 `skills/workflow-steps/step-source-index/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与 N4 source tier 语义以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 对已解析的 source/reference 材料分块（chunk_text），逐块生成 `SRC-xxx` 来源记录写入 `knowledge/source_index.json`。
- 依材料 role 判定 source tier 与 support_capabilities：HITL=T0、item definition 等项目 source=T1、HARA 模板/checklist=T2、functional safety 方法学=T3、既有 HARA 报告 sample=T4、生成/未知推断=T5。
- 生成 `knowledge/provenance_index.json`，建立 source → file → path 的溯源链。
- 把未覆盖的知识点（如缺少支撑 hazard/rating 的项目证据）写入 `knowledge/knowledge_gaps.md`。
- **底线**：sample=T4 仅风格、reference=T3 仅方法学，绝不升格为 hazard/S-E-C/ASIL/safety goal 的事实证据；T3/T4/T5 不能单独支撑 HARA critical claim。

## HARA 报告过程总览（本步定位）

HARA 报告须做到「每个 critical claim 可追溯到一条 T0/T1 证据」。本步建立 source 与 chunk 的索引，使后续 evidence-map / citation-plan 能精确引用。

**HARA 索引要点**：

- chunk 按语义边界切分（功能 / 工况 / 接口 / 约束 / 失效模式段落各自独立）
- 索引记录 source role；sample chunk 仅供格式参考，不会被后续 evidence-map 用于支撑 hazard / rating / ASIL
- 缺失关键信息（功能清单 / 系统边界 / 工况频率 / 接口方向）显式登记为 `knowledge_gap`，**不推断填值**

**本步定位**：为「Item 定义摘要 / 运行工况 / 危害识别 / 危害事件 / S-E-C / ASIL / 安全目标」7 个强制章节准备可追溯的证据来源。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`source_index.json`、`provenance_index.json`、`knowledge_gaps.md`）将在 Step 10/11 被以下检查点定位。subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-1-02 | source_index 存在 | `artifacts/source_index.json` 可解析 |
| VC-2-04 | 每条 SRC-xxx 含 provenance | file_id + 章节 / 行号 / 段落位置完整 |
| RD-6 | knowledge_gap 已登记 | 缺失功能清单 / 边界 / 工况频率 / 接口方向均有对应 gap 条目 |
| 根 skill | source ≠ sample 边界 | sample chunk 标记不会被 evidence-map 当作 hazard / rating 证据 |

**自检底线**：每条 chunk 都能回溯到具体 file 的具体位置；任何 sample / reference chunk 不得越级为后续 hazard / 评级 / ASIL / SG 的支撑。


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA 来源分块策略（chunk 语义边界）

HARA source index 应沿以下语义边界切分，便于后续证据检索与引用槽匹配：

| 分块主题 | 来源 role | tier | 分块粒度 | 典型 support_capabilities |
|---|---|---|---|---|
| 每条 item 功能（F-xx） | source | T1 | 段落/条目 | 支撑 hazard 识别（失效类型分析） |
| 系统边界描述 | source | T1 | 段落 | 支撑 item 范围界定、hazard 归属判断 |
| 每个外部接口（IF-xx） | source | T1 | 条目 | 支撑危害来源判断（接口失效危害）|
| 每个运行工况（OS-xx） | source | T1 | 条目 | 支撑 E 评级依据、工况描述 |
| 每条安全假设 | source | T1 | 条目 | 支撑 C 评级依据（可控性假设）|
| S/E/C 等级定义（每级） | reference | T3 | 表格行 | 提供评级方法框架（不支撑具体评级值）|
| ASIL 矩阵 | reference | T3 | 表格 | 支撑 ASIL 确定方法（不支撑具体 ASIL 值）|
| 检查条目（每条） | checklist | T2 | 条目 | 支撑审查/验证覆盖度检查 |

### 典型 knowledge_gaps（HARA 场景）

以下情况应写入 `knowledge/knowledge_gaps.md`：
- **缺少 item 功能描述**：无法用引导词法系统识别危害（H-xx 将全部 unsupported）
- **缺少运行工况 source**：E 评级无法由 T1 支撑（weak 或 unsupported）
- **缺少系统边界说明**：无法判断危害归属范围（属于 item 还是外部系统）
- **仅有 sample HARA（T4）**：不能支撑任何 critical claim（hazard/rating/ASIL/SG）
- **接口描述不完整**：可能遗漏接口失效类危害

### source_index SRC 记录核心字段

每条 `SRC-xxx` 记录须包含：
- `file_id`：对应 manifest 中的材料 ID
- `tier`：T0/T1/T2/T3/T4/T5
- `chunk_text`：原文片段（或结构化摘要）
- `support_capabilities`：该块能支撑的 HARA 主张类型列表
- `provenance`：file_id + 章节/行号/段落位置

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按 artifact/章节逐项核对。
- 方案C 先扫高风险约束（sample=T4 / reference=T3 未被升格、T0/T1 与 critical claim 边界）再补其余。

### 典型审核子任务
1. 逐条核对 SRC 的 tier（T0–T5）标注是否准确。
2. 核对 sample/reference 未被升格为事实证据。
3. 核对 T0/T1 与 HARA critical claim 边界是否成立。
4. 核对 knowledge_gaps.md 是否完整。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 按材料逐份分块建 SRC 记录。
- 方案B 按章节主题聚合分块。
- 方案C 先建 tier 分层骨架再回填来源块。

### 典型修订子任务
1. 对 source/reference 分块（chunk_text）。
2. 逐块生成 SRC-xxx 记录并判定 tier（T0–T5）与 support_capabilities。
3. 建立 provenance_index 溯源链。
4. 汇总未覆盖知识点写 knowledge_gaps.md。

## state.json 示例（HARA）

```json
{
  "step": "source-index",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "逐条核对 SRC tier 标注", "status": "done"},
      {"id": "rv-2", "desc": "核对 sample=T4/reference=T3 未升格", "status": "running"},
      {"id": "rv-3", "desc": "核对 knowledge_gaps 完整", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "对 source/reference 分块（chunk_text）", "status": "done"},
      {"id": "rt-2", "desc": "逐块生成 SRC 记录并判定 tier", "status": "running"},
      {"id": "rt-3", "desc": "建立 provenance_index 溯源链", "status": "not_run"},
      {"id": "rt-4", "desc": "汇总知识缺口写 knowledge_gaps.md", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：source tier（T0–T5）标注是否准确；sample=T4 / reference=T3 是否未被升格为 hazard/rating 事实证据；T0/T1 与 HARA critical claim 边界是否成立；知识缺口是否完整写入 `knowledge_gaps.md`。
