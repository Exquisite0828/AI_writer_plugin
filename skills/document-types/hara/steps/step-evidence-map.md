# HARA 子 skill · Step 6 · 证据映射 (Evidence Map)

本文件是通用骨架 `skills/workflow-steps/step-evidence-map/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 对每个研究问题：**L1 → L2 → L3 → 原文**（可先经 `topic_index` 命中路径），在 L3 叶子精读后生成 `EVD-xxx`（provenance：`file_id` + L1/L2/L3 + `location` + `snippet`）。
- 依 tier 判定 status，写入 `plans/evidence_map.json`；weak/unsupported 汇入 `unresolved_questions.md`。
- **底线**：禁止不经过 L1/L2/L3 直接打开输入文件；禁止 `SRC-xxx` / chunk；禁止把目录 brief 当 EVD 正文。

## HARA 报告过程总览（本步定位）

HARA critical claim 须可追溯到 T0/T1 及 **L1/L2/L3 原文位置**。本步把 research-questions 与三级目录导航衔接为 `EVD-xxx`。

**HARA 证据映射规则**：

- hazard / hazardous event / S/E/C / ASIL / safety goal：**只接受 T0（HITL）或 T1（项目源）证据**
- T2（模板 / checklist）只支撑结构合规，不支撑 hazard 内容
- T3（方法学）只支撑评级方法论，不为具体评级背书
- T4（sample）**绝不可作为 hazard / rating / ASIL / SG 证据**；T5（推断）不支撑 critical claim
- 匹配失败的问题登记到 `unresolved_questions`，对应 claim 保持 `NEEDS_USER_CONFIRMATION`

**本步定位**：建立 evidence map 与 unresolved 清单，决定后续哪些章节有支撑、哪些必须保持 pending。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`evidence_map.json`、`unresolved_questions.md`）将在 Step 10/11 被以下检查点定位。subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-1-07 | unresolved_questions 存在 | 文件存在（即使为空列表）|
| VC-2-01 | 无 T4（sample）支撑 critical claim | 遍历 hazard / HE / S / E / C / ASIL / SG 的 evidence_ids，tier ≠ T4 |
| VC-2-02 | 无 T5（推断）支撑任何 claim | evidence tier ≠ T5 |
| VC-2-03 | S / E / C 不仅由 T3 支撑 | 评级 evidence 至少含 T0 或 T1 |
| RD-6 | knowledge_gap 完整 | 弱支撑 / 无支撑问题均登记到 unresolved |

**自检底线**：HARA critical claim 只接受 T0（HITL）或 T1（项目源）证据；匹配失败的问题对应 claim 保持 `NEEDS_USER_CONFIRMATION`，**不得**用 sample / reference 补位。



## ISO 26262-3 标准 Checklist 与 Review 要点（Clause 对照）

本步对应 Phase D1（HE 证据基础）+ Phase E1/E2/E3（S/E/C 评级证据基础）。
所有 critical claim 的事实证据**只能**指向 T0/T1，sample（T4）严禁进入。

### Checklist（证据映射）

- [ ] hazard（H-xx）evidence_ids 仅指向 T0/T1
- [ ] 危害事件（HE-xxx）的工况组合证据来自 T1 工况 source
- [ ] **Severity（S，ISO 26262-3 Table 1）** 证据含：伤害类型 / AIS / 碰撞速度 / 被撞对象 / 保护装置 等具体依据
- [ ] **Exposure（E，ISO 26262-3 Table 2）** 证据基于**工况出现频率**（**非**失效概率）；含时间占比或公里数占比，引用 T1 工况 source 或 ISO 26262-3 Annex B
- [ ] **Controllability（C，ISO 26262-3 Table 3）** 证据基于**典型驾驶员**响应能力、警示信号可用性，含具体推理
- [ ] T2 仅支撑结构合规，不支撑评级
- [ ] T3 不为具体评级数值背书
- [ ] T4 / T5 不进入任何 critical claim 的支撑
- [ ] 匹配失败的问题登入 `unresolved_questions`

### Review 要点

| 失效 | 级别 |
|---|---|
| 任何 critical claim evidence 指向 T4 | **P0** |
| E 与失效概率混淆（把 fault rate 当 E） | **P0**（ISO 26262 概念错误） |
| E 缺时间占比 / 公里数占比依据 | **P1** |
| S 仅有数字无伤害类型依据 | **P1** |
| C 用专家驾驶员假设 | **P0** |
| 自动驾驶场景 C 默认 C3 但无依据 | **P1** |
| S/E/C 支撑仅有 T3 | **P1** |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主要风险 | 缺基线数据时倾向推断填值 | sample 评级数值作为"现成证据"被引入（**最大诱惑点**） |
| 本步动作 | 缺数据 claim 保持 candidate；登记 `unresolved_questions` | 显式列出"sample 中的 hazard / S/E/C / ASIL / SG 已剔除，不作为本项目证据"；E 评级因目标市场 / 车型 / ODD 差异最大，必须独立重新取证 |


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA 证据映射规则

各研究问题类型可接受的证据 tier 与匹配关键词：

| 问题类型 | 可接受的证据 tier | topic_index / L1/L2/L3 导航主题 |
|---|---|---|
| Q-ITEM（item 功能/边界/接口） | T1（item definition source）| 功能描述、系统边界、接口清单、运行约束 |
| Q-OPS（运行工况描述） | T1（operational situations source）| 工况描述、道路类型、速度范围、驾驶场景 |
| Q-HAZ（危害识别，各失效类型） | T1（item 功能描述 source）| 对应功能 F-xx 名称、失效行为、功能边界 |
| Q-HE（危害事件成立性） | T1（item def + operational situations）| 危害行为 + 工况组合、潜在后果 |
| Q-SEV（S 评级依据） | T1（source 中伤害场景描述）+ T3（ISO 26262-3 Table 1 方法）| 伤亡类型、伤害程度描述 |
| Q-EXP（E 评级依据） | T1（工况 source 中暴露频率数据）+ T3（ISO 26262-3 Table 2 方法）| 工况频率、时间比例、暴露场景 |
| Q-CTR（C 评级依据） | T1（source 中驾驶员行为假设/可控性分析）+ T3（ISO 26262-3 Table 3 方法）| 控制时间、反应可能性 |
| Q-ASIL（ASIL 候选） | T3（ISO 26262-3 Table 4 方法）用于查表方法；T0/T1 用于 S/E/C 值 | ASIL 矩阵 |
| Q-SG（安全目标） | T0（已记录 HITL）/ T1（已支撑的 HE + ASIL 候选）| 危害事件描述、ASIL 等级 |

### 证据支撑能力判定

| 证据 tier | 对 HARA critical claim 的支撑能力 |
|---|---|
| T0（HITL 确认）| 可支撑所有 HARA critical claim，包括最终评级与安全目标 |
| T1（项目 source）| 可支撑事实性描述（功能/危害/工况/接口），配合 T3 方法可形成候选值依据 |
| T2（模板/checklist）| 仅约束结构，不支撑具体 claim |
| T3（reference 方法）| 提供评级方法框架（S/E/C 定义、ASIL 矩阵），**不能单独支撑具体评级值** |
| T4（sample）| 仅格式/风格参考，**绝不进入 HARA critical claim 证据映射** |
| T5（推断/未知）| 不接受，需标 unsupported |

### unresolved_questions.md 应包含的内容

对以下类型问题保持 open 并写入 `plans/unresolved_questions.md`：
- 无任何 T0/T1 证据命中的 Q-HAZ/Q-HE 问题（危害识别无法支撑）
- Q-SEV/Q-EXP/Q-CTR 仅有 T3 方法支撑、缺 T1 事实依据的评级问题
- Q-SG 中安全目标措辞或 ASIL 尚未经 HITL 确认的问题
- 不记录"我推断这个评级应该是..."，只记录"该问题当前无法由现有来源支撑"

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按 artifact/问题逐项核对。
- 方案C 先扫高风险约束（HARA critical claim 的 T0/T1 支撑与 open 标记）再补其余。

### 典型审核子任务
1. 核对 HARA critical claim 是否仅由 T0/T1 支撑。
2. 核对无证据问题是否进入 unresolved_questions.md 并保持 open。
3. 核对 sample HARA 报告/reference 方法学未被误当事实证据。
4. 核对 evidence_map 是否符合 artifact 契约。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 逐题经 topic_index 得 L1/L2/L3 路径，再 L1→L2→L3→读原文生成 EVD。
- 方案B 先按 tier 过滤文档（优先 T1 source），再在 provenance_index 的 L2 中匹配主题。
- 方案C 按章节分组批量定位 L2 后逐题精读原文。

### 典型修订子任务
1. 遍历 research_questions 逐题。
2. 在 `document_tocs` 按 L1→L2→L3 选定叶子，读原文生成 EVD-xxx。
3. 建立 question→evidence 映射并记 tier + L1/L2/L3 provenance。
4. 建立 question→evidence 映射并判定 status。
5. 未命中/弱证据/HARA critical claim 缺 T0/T1 的问题标 open。

## state.json 示例（HARA）

```json
{
  "step": "evidence-map",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对 HARA critical claim 仅由 T0/T1 支撑", "status": "done"},
      {"id": "rv-2", "desc": "核对无证据问题进入 unresolved 并保持 open", "status": "running"},
      {"id": "rv-3", "desc": "核对 sample/reference 未被误当事实证据", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "遍历 research_questions 逐题", "status": "done"},
      {"id": "rt-2", "desc": "L1→L2→L3→读原文生成 EVD", "status": "running"},
      {"id": "rt-3", "desc": "建立 question→evidence 映射并判定 status", "status": "not_run"},
      {"id": "rt-4", "desc": "缺 T0/T1 的 critical claim 问题标 open", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：HARA critical claim 是否仅由 T0/T1 支撑（T3/T4/T5 不能单独支撑）；无证据问题是否进入 `unresolved_questions.md` 并保持 open；sample HARA 报告与 reference 方法学是否被误当事实证据。
