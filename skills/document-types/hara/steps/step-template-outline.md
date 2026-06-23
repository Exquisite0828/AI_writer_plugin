# HARA 子 skill · Step 4 · 模板大纲 (Template Outline)

本文件是通用骨架 `skills/workflow-steps/step-template-outline/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 从 inventory 选取 template 材料（select_template），结合 HARA `DocumentTypeRules` 建立 `plans/template_structure.json`。
- 生成带 order/section_id/title/intent 的结构化章节，并标注 needs_human_confirmation；渲染一级大纲 `plans/outline_l1.md`。
- HARA 期望章节（缺失须补全）：文档目的与范围、输入材料与假设、item definition 摘要、operational situations 与 modes、hazard identification、hazardous event 分析、S/E/C rating 表、ASIL candidate、safety goals candidate、open issues 与 required confirmations、review summary。
- 保留 strict_template 的强制章节（mandatory sections），不删减或改名。
- 只定义结构与章节意图，不写正文、不预设 hazard/rating/ASIL/safety goal 结论。
- **底线**：保留 HARA 术语（hazard、S/E/C、ASIL、safety goal），但本步不得填入未经证据支撑的专业判断。

## HARA 报告过程总览（本步定位）

HARA 报告在 ISO 26262-3 约束下有标准 12 节结构。本步从 HARA 模板（T2）建立大纲，进入「报告结构定义」阶段。

**HARA 报告标准 12 节结构**（★ 为强制章节，须 HITL 确认）：

| 节序 | 章节 ID | 标题 | 强制 |
|---|---|---|---|
| 1 | SEC-DOC | 文档信息与修订历史 |  |
| 2 | SEC-SCOPE | 文档目的与范围 |  |
| 3 | SEC-REF | 参考文件 |  |
| 4 | SEC-TERMS | 术语与缩略语 |  |
| 5 | SEC-ITEM | Item 定义摘要 | ★ |
| 6 | SEC-OPS | 运行工况与模式 | ★ |
| 7 | SEC-HAZ | 危害识别 | ★ |
| 8 | SEC-HE | 危害事件分析 | ★ |
| 9 | SEC-SEC | S/E/C 评级与 ASIL 候选 | ★ |
| 10 | SEC-SG | 安全目标候选 | ★ |
| 11 | SEC-OPEN | 开放问题与待确认项 |  |
| 12 | SEC-REVIEW | 审查总结 | ★ |

**本步定位**：固化 12 节骨架、章节意图、强制章节标记，**不写正文、不预设 hazard / rating / ASIL / SG 结论**。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`template_structure.json`、`outline_l1.md`）将在 Step 10/11 被以下检查点定位。subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-1-03 | template_structure 含 12 个 section_id | 遍历 SEC-DOC / SCOPE / REF / TERMS / ITEM / OPS / HAZ / HE / SEC / SG / OPEN / REVIEW |
| RD-1 | 12 个 mandatory section 全部存在 | 缺一即 P0 |
| RD-1 | 元数据字段就位 | 标题 / 版本 / 日期 / 作者 / 状态字段已留位 |
| RD-1 | 修订历史预留位 | 至少 1 条修订记录占位（初版即为 v0.1） |
| 根 skill | 强制章节不删减不改名 | mandatory section 的 section_id 与标题与契约一致 |

**自检底线**：本步只定义结构与章节意图，**不写正文、不预设 hazard / rating / ASIL / SG 结论**；模板章节缺失会在 Step 10 直接 P0 阻断。


## ISO 26262 HARA 方法论（本步专属执行指引）

### ISO 26262-3 HARA 报告标准章节结构

生成 `template_structure.json` 时，必须包含以下章节（`*` 为强制章节，`needs_human_confirmation=true`）：

| order | section_id | title | intent | needs_human_confirmation |
|---|---|---|---|---|
| 1 | SEC-DOC | 文档信息与修订历史 | 标题、版本、日期、作者、状态、修订记录表 | false |
| 2 | SEC-SCOPE* | 文档目的与范围 | 分析的 item 名称、适用标准（ISO 26262-3）、分析范围（包含/不包含）、预期用途 | false |
| 3 | SEC-REF | 参考文件 | 引用的项目文件清单（来自 manifest）+ ISO 26262 条款引用 | false |
| 4 | SEC-TERMS | 术语与缩略语 | HARA/ASIL/S/E/C/SG/HE/HITL 等术语定义，保留英文缩写 | false |
| 5 | SEC-ITEM* | Item 定义摘要 | item 名称、功能列表（F-xx）、系统边界表（In/Out of scope）、外部接口表（IF-xx）、运行约束；来自 T1 source | true |
| 6 | SEC-OPS* | 运行工况与模式 | 运行工况表（OS-xx）：ID/描述/道路类型/速度范围/交通密度/天气/驾驶员状态；来自 T1 source | true |
| 7 | SEC-HAZ* | 危害识别 | 引导词法对每个功能分析失效模式；危害清单（H-xx）：ID/危害描述/相关功能/失效类型 | true |
| 8 | SEC-HE* | 危害事件分析 | 危害×工况组合分析，危害事件表（HE-xxx）：ID/H-ID/OS-ID/危害事件描述 | true |
| 9 | SEC-SEC* | S/E/C 评级与 ASIL 候选 | 每个 HE 的 Severity/Exposure/Controllability 评级及文字依据；ASIL 候选（依 ISO 26262-3 Table 4）；全部标 NEEDS_USER_CONFIRMATION | true |
| 10 | SEC-SG* | 安全目标候选 | 对 ASIL 候选 > QM 的每个 HE 生成安全目标（SG-xx）：ID/描述/ASIL候选/相关HE-ID/状态 | true |
| 11 | SEC-OPEN | 开放问题与待确认项 | 汇总所有 NEEDS_USER_CONFIRMATION 项；分类：item定义待确认/危害待确认/评级待确认/安全目标待确认 | false |
| 12 | SEC-REVIEW | 审查总结 | 保守措辞：分析覆盖范围、已支撑项摘要、开放项数量；状态：finalized_with_open_items / blocked_pending_confirmation | false |

### 各强制章节内容结构说明

**SEC-ITEM 内部结构：**
- 功能清单：`F-01 [功能名称]：[描述]`（≥3 条）
- 系统边界表：两列（系统内 In scope / 系统外 Out of scope）
- 外部接口表：IF-ID / 接口名 / 类型（CAN/电气/机械）/ 信号方向 / 说明
- 运行约束：速度范围、温度范围、应用车型/场景限制

**SEC-OPS 内部结构（表格列）：**
OS-ID | 工况描述 | 道路类型 | 速度范围 | 交通密度 | 天气/能见度 | 驾驶员状态
至少覆盖：高速行驶 / 城市驾驶 / 低速机动（停车场）/ 恶劣天气或紧急工况

**SEC-HAZ 内部结构（表格列）：**
H-ID | 危害描述 | 相关功能（F-xx）| 失效类型 | 失效来源 | 状态

失效类型引导词（对每个功能逐一检查）：
- 无功能（No Function）/ 功能过强（More Function）/ 功能过弱（Less Function）
- 错误方向（Wrong Direction）/ 非预期功能（Unintended Function）
- 时序过早/过晚（Too Early / Too Late）

**SEC-HE 内部结构（表格列）：**
HE-ID | H-ID | OS-ID | 危害事件描述 | 是否成立 | 说明

**SEC-SEC 内部结构（表格列）：**
HE-ID | 危害事件描述（简） | S候选 | S依据 | E候选 | E依据 | C候选 | C依据 | ASIL候选 | 状态

**SEC-SG 内部结构（表格列）：**
SG-ID | 安全目标描述 | ASIL候选 | 相关HE-ID | 来自H-ID | 状态

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按 artifact/章节逐项核对。
- 方案C 先扫高风险约束（strict_template 强制章节保留与 HARA 期望章节覆盖）再补其余。

### 典型审核子任务
1. 核对 HARA 期望章节覆盖是否完整（S/E/C、ASIL、safety goals、open issues 等）。
2. 核对 strict_template 强制章节是否保留。
3. 核对大纲是否非空且非敷衍、未预设结论。
4. 核对 template_structure/outline_l1 是否符合 artifact 契约。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 直接套用 HARA 内置模板骨架。
- 方案B 从 inventory 选取的 template 材料提取章节结构。
- 方案C 二者合并去重（strict_template 强制章节优先）。

### 典型修订子任务
1. 选取 template 材料并解析其章节。
2. 与 HARA 规则合并建 template_structure。
3. 逐节生成 order/section_id/title/intent。
4. 标注 strict_template 强制章节与 needs_human_confirmation。

## state.json 示例（HARA）

```json
{
  "step": "template-outline",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对 HARA 期望章节覆盖完整", "status": "done"},
      {"id": "rv-2", "desc": "核对 strict_template 强制章节保留", "status": "running"},
      {"id": "rv-3", "desc": "核对大纲非空且未预设结论", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "选取 template 材料并解析章节", "status": "done"},
      {"id": "rt-2", "desc": "与 HARA 规则合并建 template_structure", "status": "running"},
      {"id": "rt-3", "desc": "逐节生成 order/section_id/title/intent", "status": "not_run"},
      {"id": "rt-4", "desc": "标注强制章节与 needs_human_confirmation", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：HARA 期望章节覆盖是否完整（含 S/E/C rating 表、ASIL candidate、safety goals candidate、open issues 与 required confirmations）；`strict_template` 强制章节是否保留；大纲是否非空且非敷衍、是否未预设 hazard/rating/ASIL/safety goal 结论。
