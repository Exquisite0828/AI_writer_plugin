# HARA 子 skill · Step 2 · 材料清单 (Material Inventory)

本文件是通用骨架 `skills/workflow-steps/step-material-inventory/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 对每份材料按格式选择 reader 抽取文本，生成结构化清单 `inputs/input_inventory.json`。
- 为每条记录登记 `role` / `parse_status`（parsed/failed/unsupported/missing）/ `is_fact_source`。
- HARA 角色判定：item definition、operational situations、assumptions 等 `source` 标 `is_fact_source=true`；HARA 模板（template）、safety/review checklist、functional safety 方法学（reference）、既有 HARA 报告样例（sample）一律 `is_fact_source=false`。
- 仅对 parsed 且 role ∈ {source, reference} 的材料保留可供后续索引的抽取文本。
- 如实标记 missing/unsupported/failed，不静默吞掉解析问题。
- **底线**：sample HARA 报告即使解析成功也绝不是 hazard/rating/ASIL/safety goal 的事实来源。

## HARA 报告过程总览（本步定位）

HARA 流程把各类输入材料拆解为可索引的 inventory 记录。本步承接 Step 1 登记，进入「输入材料解析」阶段。

**HARA 材料解析要点**：

- source 材料（item 定义 / 工况 / 架构）须提取功能、边界、接口、运行约束等关键信息
- sample 报告只可提取格式 / 表格形状 / 措辞风格，**绝不抽取其中的 hazard / rating / ASIL / SG 作为本项目内容**
- reference 方法学可抽取 S/E/C/ASIL 评定方法，但不能为本项目事实背书

**本步定位**：把每份材料解析为可被后续 source-index / evidence-map / citation-plan 引用的 chunk 与字段，保持 role 与事实边界。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（material inventory、各 role 提取要点、parse_status）将在 Step 10/11 被以下检查点定位。subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-5-04 | 无静默解析失败 | 每个材料含 `parse_status: parsed / failed / unsupported / pending` |
| RD-2 | source 解析支撑 SEC-ITEM | item 定义 source 提取出功能、边界、接口、约束 |
| RD-2 | sample 内容隔离 | sample 解析结果未进入 hazard / rating / ASIL / SG 字段 |
| RD-3 | reference 不替代 source | 方法学不被用作具体危害条目的来源 |

**自检底线**：sample / reference 即使解析成功，其内容也不可作为后续 critical claim 的事实依据；解析失败应如实标记，不可静默吞掉。


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA 材料解析重点：各 role 材料需提取的内容

| 材料 role | 需提取的 HARA 关键内容 | 无法提取时的处理 |
|---|---|---|
| source (item definition) | ① item 名称与版本；② 功能列表（每条：编号 + 描述）；③ 系统边界（包含/排除子系统）；④ 外部接口（信号名、类型、方向）；⑤ 运行约束（速度/温度/应用场景）| 登记 parse_status=parsed，标注 knowledge_gap，不静默跳过 |
| source (operational situations) | ① 工况 ID 与文字描述；② 道路类型（高速/城市/停车场）；③ 速度范围；④ 交通密度；⑤ 天气/能见度；⑥ 驾驶员状态 | 登记缺失项，E 评级后续将 weak/unsupported |
| source (assumptions / constraints) | ① 安全假设清单；② 接口假设；③ 不包含在 item 内的功能说明 | 登记，影响 C 评级依据 |
| template | ① 强制章节清单（mandatory sections）；② 表格格式（hazard 表/HE 表/S-E-C 表/SG 表的列定义）；③ 文档版本控制字段 | 使用 HARA 内置默认结构 |
| checklist | ① ISO 26262-3 检查条目列表；② 每条检查项的检查点描述 | 使用内置 HARA checklist |
| reference | ① S/E/C 等级定义（S0-S3 / E0-E4 / C0-C3）；② ASIL 确定矩阵（S×E×C → ASIL/QM）；③ 安全目标写法指导 | 登记 tier=T3，只提供方法框架 |
| sample | **仅提取**：① 章节层级结构；② 表格列名；③ 措辞风格。**绝不提取**：任何具体 hazard / rating / ASIL / safety goal 内容 | is_fact_source=false，降级警告 |

### parse_status 判定规则
- `parsed`：成功提取到上表对应内容
- `failed`：文件存在但解析失败（格式不支持、损坏等）
- `unsupported`：文件格式不在当前支持范围内
- `missing`：task.yaml 声明但文件不存在

失败/缺失项须显式写入清单并标记，绝不静默吞掉。

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按 artifact/章节逐项核对。
- 方案C 先扫高风险约束（failed/unsupported/missing 如实登记与 sample 报告 is_fact_source=false 判定）再补其余。

### 典型审核子任务
1. 逐条核对 role/parse_status/is_fact_source 是否正确。
2. 核对 sample HARA 报告与 reference 方法学 `is_fact_source=false`。
3. 核对 missing/unsupported/failed 是否如实登记、summary 计数是否一致。
4. 核对清单是否符合 artifact 契约。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 按文件格式分组（PDF/DOCX/MD…）分别选 reader 批处理。
- 方案B 逐份材料串行解析并即时登记。
- 方案C 先快速探测格式与可解析性，再对可解析项深解析、对失败项单独登记。

### 典型修订子任务
1. 枚举待解析材料并探测格式。
2. 逐份抽取文本生成清单记录。
3. 标注 role/parse_status/is_fact_source（HARA 样例/reference 标 false）。
4. 校验 summary 计数一致、failed/unsupported/missing 如实登记。

## state.json 示例（HARA）

```json
{
  "step": "material-inventory",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "逐条核对 role/parse_status/is_fact_source", "status": "done"},
      {"id": "rv-2", "desc": "核对 sample HARA 报告 is_fact_source=false", "status": "running"},
      {"id": "rv-3", "desc": "核对 summary 计数一致、失败/缺失如实登记", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "枚举待解析材料并探测格式", "status": "done"},
      {"id": "rt-2", "desc": "逐份抽取文本生成清单记录", "status": "running"},
      {"id": "rt-3", "desc": "标注 role/parse_status/is_fact_source", "status": "not_run"},
      {"id": "rt-4", "desc": "校验 summary 计数、失败/缺失如实登记", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：每条记录的 `role` / `parse_status` / `is_fact_source` 是否正确（HARA sample 报告与 reference 方法学必须 `is_fact_source=false`）；`missing` / `unsupported` / `failed` 是否如实登记；`summary` 计数是否一致。
