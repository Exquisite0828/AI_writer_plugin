# HARA 子 skill · Step 5 · 研究问题 (Research Questions)

本文件是通用骨架 `skills/workflow-steps/step-research-questions/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 遍历 HARA 模板大纲章节（hazard identification、hazardous event 分析、S/E/C rating、ASIL candidate、safety goals、open issues 等），构造需由来源回答的研究问题。
- 为每个问题分配 question_id、推断 question_type，并标注 requires_human_confirmation。
- HARA critical claims（hazard、hazardous event、S/E/C、ASIL、safety goal、final acceptability）对应的问题必须明确，等待 T0/T1 证据或 HITL，否则保持 open。
- 依证据候选判定 status（supported/weak/unsupported），写入 `plans/research_questions.json`。
- 只描述待答问题、不预设结论；不引入 RAG/向量库/复杂 agent 框架来"自动回答"。
- **底线**：不得由 sample HARA 报告或 reference 方法学直接生成 hazard/rating/ASIL/safety goal 的"已确认"问题答案。

## HARA 报告过程总览（本步定位）

HARA 危害识别的核心是引导词法（HAZOP-style）：对每个功能逐一应用 6 种失效引导词，系统识别潜在危害行为。本步为该方法生成驱动性问题。

**HARA 6 种危害识别引导词**：

| 引导词 | 失效类型 | 分析提问 |
|---|---|---|
| No Function | 无功能 / 完全失效 | 该功能完全不工作时会发生什么？|
| More Function | 功能过强 | 输出超过预期（力度 / 速度 / 幅度）时会发生什么？|
| Less Function | 功能过弱 | 输出低于预期时会发生什么？|
| Wrong Direction | 错误方向 | 方向相反（如制动变加速）时会发生什么？|
| Unintended Function | 非预期激活 | 未被指令时意外激活会发生什么？|
| Too Early / Too Late | 时序错误 | 激活时机不对时会发生什么？|

**本步定位**：把章节意图与知识缺口转译为 Q-ITEM / Q-OPS / Q-HAZ / Q-HE / Q-SEC / Q-SG 等问题，供 evidence-map 检索证据。问题本身不预设答案。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`research_questions.json`）将在 Step 10/11 被以下检查点定位。subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| RD-3 | 每个功能 F-xx 至少覆盖 ≥ 2 种引导词 | 遍历 F-xx，确认 Q-HAZ 中对应该功能的引导词数 ≥ 2 |
| RD-3 | 引导词覆盖度均衡 | 不仅有 No Function，应同时考虑 Unintended / Wrong Direction 等 |
| RD-6 | 知识缺口可见 | 问题 status 为 `weak / unsupported` 的条目登记到 unresolved |
| 根 skill | 问题不预设答案 | Q-xx 中无 hazard / rating / ASIL / SG 的结论性措辞 |

**自检底线**：本步只描述待答问题、不预设结论；不得由 sample HARA 报告或 reference 方法学直接给出 hazard / rating / ASIL / SG 的"已确认"答案。


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA 标准研究问题模板

按大纲章节构造以下研究问题，为每个问题分配 question_id、推断 question_type：

#### Item 定义类（Q-ITEM）
| question_id | 问题 | question_type | requires_human_confirmation |
|---|---|---|---|
| Q-ITEM-01 | Item 的名称与版本号是什么？ | item_info | false |
| Q-ITEM-02 | Item 执行哪些主要功能（功能 F-xx 清单）？ | item_function | true |
| Q-ITEM-03 | Item 的系统边界如何界定（包含/排除哪些子系统）？ | item_boundary | true |
| Q-ITEM-04 | Item 有哪些关键外部接口（传感器/执行器/CAN信号/机械接口）？ | item_interface | true |
| Q-ITEM-05 | Item 的运行约束是什么（速度范围、环境温度、应用车型）？ | item_constraint | false |

#### 运行工况类（Q-OPS）
| question_id | 问题 | question_type | requires_human_confirmation |
|---|---|---|---|
| Q-OPS-01 | 与本 item 相关的典型运行工况有哪些（道路类型、车速、交通）？ | operational_situation | true |
| Q-OPS-02 | 每个运行工况的暴露频率/概率如何（对应 E0-E4 判定依据）？ | exposure_basis | true |
| Q-OPS-03 | 是否存在特殊工况（恶劣天气、紧急情况、驾驶员分心等）？ | operational_situation | true |

#### 危害识别类（Q-HAZ，对每个功能 F-xx 逐一展开）
| question_id | 问题 | question_type | requires_human_confirmation |
|---|---|---|---|
| Q-HAZ-01 | 功能 [F-xx] 发生"无功能（No Function）"时产生何种危害？ | hazard_no_function | true |
| Q-HAZ-02 | 功能 [F-xx] 发生"功能过强（More Function）"时产生何种危害？ | hazard_more | true |
| Q-HAZ-03 | 功能 [F-xx] 发生"功能过弱（Less Function）"时产生何种危害？ | hazard_less | true |
| Q-HAZ-04 | 功能 [F-xx] 发生"错误方向（Wrong Direction）"时产生何种危害？ | hazard_wrong_dir | true |
| Q-HAZ-05 | 功能 [F-xx] 发生"非预期功能（Unintended Function）"时产生何种危害？ | hazard_unintended | true |
| Q-HAZ-06 | 功能 [F-xx] 发生"时序错误（Too Early/Too Late）"时产生何种危害？ | hazard_timing | true |

#### 危害事件类（Q-HE，对每个 H-xx × OS-xx 组合）
| question_id | 问题 | question_type | requires_human_confirmation |
|---|---|---|---|
| Q-HE-01 | 危害 [H-xx] 在工况 [OS-xx] 下是否构成危害事件？具体场景如何？ | hazardous_event | true |
| Q-HE-02 | 危害事件 [HE-xxx] 最严重的潜在后果是什么（伤亡类型/程度）？ | harm_consequence | true |

#### S/E/C 评级类（Q-SEC）
| question_id | 问题 | question_type | requires_human_confirmation |
|---|---|---|---|
| Q-SEV-01 | 危害事件 [HE-xxx] 最坏情况下的伤亡程度如何（S0/S1/S2/S3 判定依据）？ | severity | true |
| Q-EXP-01 | 工况 [OS-xx] 在车辆生命周期中出现的概率/时间比例如何（E0/E1/E2/E3/E4 依据）？ | exposure | true |
| Q-CTR-01 | 危害事件 [HE-xxx] 发生时驾驶员或其他使用者能否有效规避（C0/C1/C2/C3 依据）？ | controllability | true |

#### ASIL 与安全目标类（Q-ASIL / Q-SG）
| question_id | 问题 | question_type | requires_human_confirmation |
|---|---|---|---|
| Q-ASIL-01 | 根据 S/E/C 候选值，危害事件 [HE-xxx] 对应的 ASIL 候选等级是什么（ISO 26262-3 Table 4）？ | asil | true |
| Q-SG-01 | 危害事件 [HE-xxx]（ASIL候选 > QM）对应的安全目标描述是什么？ | safety_goal | true |
| Q-SG-02 | 是否所有 ASIL候选 > QM 的危害事件均已生成对应安全目标？ | safety_goal_coverage | true |

#### 开放问题类（Q-OPEN）
| question_id | 问题 | question_type | requires_human_confirmation |
|---|---|---|---|
| Q-OPEN-01 | 哪些危害/评级/安全目标无法由现有 source 支撑，需要 HITL 确认？ | open_item | true |
| Q-OPEN-02 | 是否存在需要进一步工程调查才能确定的危害场景或工况？ | open_item | true |

### 问题 status 判定规则
- `supported`：有 T0/T1 source 直接对应内容支撑
- `weak`：仅有 T3（reference方法）或 T4（sample）支撑，不能单独成立 critical claim
- `unsupported`：无任何 source 支撑，保持 open，写入 unresolved_questions.md
- HARA critical claim 类问题（Q-HAZ/Q-HE/Q-SEV/Q-EXP/Q-CTR/Q-ASIL/Q-SG）一律 `requires_human_confirmation: true`

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按 artifact/章节逐项核对。
- 方案C 先扫高风险约束（HARA critical claim 相关问题是否明确、无证据问题是否标 open）再补其余。

### 典型审核子任务
1. 核对问题是否覆盖 HARA 大纲与 critical claims（S/E/C、ASIL、safety goal 等）。
2. 核对是否只描述待答问题而未预设 hazard/rating/ASIL 结论。
3. 核对 critical claim 相关问题是否标 requires_human_confirmation、无证据问题是否标 open。
4. 核对 research_questions 是否符合 artifact 契约。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 逐章节遍历生成问题。
- 方案B 先聚合 HARA critical claims（hazard/S-E-C/ASIL/safety goal）再补普通章节。
- 方案C 按 question_type 分组生成。

### 典型修订子任务
1. 遍历 template_structure 大纲章节构造问题草稿（build_question_drafts）。
2. 为每个问题分配 question_id 并推断 question_type。
3. 判定 requires_human_confirmation 与 status（supported/weak/unsupported）。
4. HARA critical claim 无证据问题保持 open。

## state.json 示例（HARA）

```json
{
  "step": "research-questions",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对问题覆盖 HARA 大纲与 critical claims", "status": "done"},
      {"id": "rv-2", "desc": "核对未预设 hazard/rating/ASIL 结论", "status": "running"},
      {"id": "rv-3", "desc": "核对 critical claim 无证据问题标 open", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "遍历大纲章节构造问题草稿", "status": "done"},
      {"id": "rt-2", "desc": "分配 question_id 并推断 question_type", "status": "running"},
      {"id": "rt-3", "desc": "判定 requires_human_confirmation 与 status", "status": "not_run"},
      {"id": "rt-4", "desc": "HARA critical claim 无证据问题保持 open", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：问题是否覆盖 HARA 大纲与 critical claims（S/E/C、ASIL、safety goal 等）；是否只描述待答问题而未预设 hazard/rating/ASIL 结论；HARA critical claim 相关问题是否标 requires_human_confirmation、无证据问题是否保持 open。
