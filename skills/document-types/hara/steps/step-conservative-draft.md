# HARA 子 skill · Step 9 · 保守草稿 (Conservative Draft)

本文件是通用骨架 `skills/workflow-steps/step-conservative-draft/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 遍历 section_tasks 逐任务，匹配 citation_plan 章节并校验任务证据（只用任务携带的 allowed evidence ids）。
- 逐节渲染保守草稿（来源支持、草稿正文、限制与开放问题、确认标记），汇编 `draft/full_draft.md`。
- HARA critical claim（hazard/hazardous event/S-E-C rating/ASIL/safety goal/final acceptability）无 T0/T1 支撑时保持 `NEEDS_USER_CONFIRMATION` / pending，不写未支撑结论。
- 不写 `final ASIL is approved`/`risk is acceptable`/`the rating is S1` 等 forbidden final claims（见根 skill）。
- 保留 source tier、claim 状态与人工确认状态；不把 sample/reference 当作事实证据。
- **底线**：缺证据的 HARA 章节只成稿可支撑内容，hazard/rating/ASIL/safety goal 结论保持 open/pending。

## HARA 报告过程总览（本步定位）

本步是 HARA 6 步核心分析过程的执行落点：把 Item 定义 → 工况 → 危害识别（引导词法）→ 危害事件 → S/E/C/ASIL → 安全目标 完整成稿。

**HARA 6 步核心分析过程**：

1. **界定 Item 定义（SEC-ITEM）**：提取功能清单 F-xx、系统边界表、外部接口表 IF-xx，全部来自 T1 source。
2. **列出运行工况（SEC-OPS）**：OS-xx 表覆盖典型工况（高速 / 城市 / 停车场 / 恶劣天气），速度与频率来自 T1 source。
3. **危害识别（SEC-HAZ）**：对每功能 F-xx 应用 6 引导词得到 H-xx 危害清单；H-xx 只描述**危害行为本身**，不描述工况。
4. **危害事件（SEC-HE）**：HE = H-xx × OS-xx 组合，描述「在工况下、危害行为可能导致何种后果」。
5. **S/E/C 评级与 ASIL 候选（SEC-SEC）**：分别评 S0–S3 / E0–E4 / C0–C3，查 ISO 26262-3 Table 4 得 ASIL 候选；**全部标 `NEEDS_USER_CONFIRMATION`**。
6. **安全目标候选（SEC-SG）**：仅对 ASIL>QM 的 HE 生成 SG；采用禁止性表述「item 不应在…条件下…，以防止…」。

**本步定位**：成稿可被 T0/T1 支撑的内容；缺证据章节保持 pending；不写 forbidden final claim。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`hara_draft.md` / `full_draft.md`）是 HARA 报告主体，将在 Step 10/11 被以下检查点全方位定位。subagent 交付前必须逐项自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-1-05 | 草稿存在且非空 | `draft/hara_draft.md` 非空 |
| RD-2 | SEC-ITEM 完整 | 功能清单 F-xx ≥ 1、边界表非空、接口表 IF-xx 含信号方向、无 sample 来源 |
| RD-3 | SEC-HAZ 引导词覆盖 | 每个 F-xx 至少 2 种引导词；H-xx 描述**行为**而非后果；全部标 `NEEDS_USER_CONFIRMATION` |
| RD-4 | SEC-HE / SEC-SEC 证据 | 每个 HE 有 S/E/C 候选 + 文字依据；E 引用 T1 工况 source；S 含伤害类型描述 |
| VC-3-01~05 | critical claim 状态正确 | 所有 H / HE / S / E / C / ASIL / SG 状态含 `NEEDS_USER_CONFIRMATION` |
| VC-4-01 | ASIL 逻辑一致 | 每条 HE 的 ASIL 候选 = S × E × C 按 ISO 26262-3 Table 4 查表结果 |
| VC-4-02 | ASIL>QM 的 HE 均有 SG | SG 数 ≥ ASIL > QM 的 HE 数 |
| VC-4-03 | ASIL=QM 的 HE 无 SG | SG 表无 QM HE 对应行 |
| RD-5 | SG 措辞合规 | 使用「不应在…条件下…，以防止…」禁止性表述；无「保证」「确保」「ensure」 |
| RD-6 | SEC-OPEN 汇总完整 | OPEN 条目数 ≥ 草稿中 `NEEDS_USER_CONFIRMATION` 数 |
| VC-5-01 | 无专业批准措辞 | 无 `ASIL is approved` / `risk is acceptable` / `safety goal approved` / `HARA 完成` |
| VC-5-02 | NEEDS_USER_CONFIRMATION 保留 | 草稿未移除任何 pending 标记 |

**自检底线**：缺证据的 HARA 章节只成稿可支撑内容，hazard / rating / ASIL / SG 结论保持 open / pending；任何 forbidden final claim 出现即 P0 阻断。


## ISO 26262 HARA 方法论（本步专属执行指引）

### 各章节写作指引与标准表格格式

---

#### SEC-ITEM（Item 定义摘要）

**功能清单（每条一行）：**
```
| 功能 ID | 功能描述 | 来源 |
| F-01 | [功能名称]：[详细功能描述，说明 item 执行什么操作、向谁提供什么] | [source file_id，章节] |
| F-02 | ... | ... |
```
若功能描述不完整或缺失：写 `[PENDING - NEEDS_USER_CONFIRMATION: 功能描述未在 source 中找到]`

**系统边界表：**
```
| 类别 | 组件/子系统 | 说明 |
| 系统内（In scope） | [组件名] | [描述] |
| 系统外（Out of scope） | [组件名] | [描述；说明由哪个外部系统负责] |
```

**外部接口表：**
```
| IF-ID | 接口名称 | 类型 | 信号方向 | 说明 |
| IF-01 | [接口名] | CAN/LIN/PWM/电气/机械 | 输入/输出/双向 | [描述] |
```

---

#### SEC-OPS（运行工况表）

```
| OS-ID | 工况描述 | 道路类型 | 速度范围 | 交通密度 | 天气/能见度 | 驾驶员状态 |
| OS-01 | 高速公路稳定行驶 | 高速公路 | 80～130 km/h | 中等 | 正常/晴天 | 正常 |
| OS-02 | 城市复杂交通行驶 | 城市道路 | 0～60 km/h | 高 | 正常 | 正常 |
| OS-03 | 停车场低速机动 | 停车场 | 0～15 km/h | 低 | 正常 | 正常 |
| OS-04 | 恶劣天气行驶（雨/雪/雾）| 各类道路 | 0～80 km/h | 中/高 | 雨/雪/雾 | 正常 |
```
注：具体工况描述及速度值须来自 T1 source；若 source 不足，在对应格中写 `[PENDING]`

---

#### SEC-HAZ（危害识别表）

**分析步骤：**对功能列表（F-01, F-02, ...）中的每个功能，逐一应用 6 种引导词：

| 引导词 | 失效类型 | 分析提问 |
|---|---|---|
| No Function | 无功能/完全失效 | 该功能完全不工作时会发生什么？ |
| More Function | 功能过强 | 该功能输出超出预期（幅度/速度/力度）时会发生什么？ |
| Less Function | 功能过弱 | 该功能输出低于预期时会发生什么？ |
| Wrong Direction | 错误方向 | 该功能方向相反（如：制动变加速）时会发生什么？ |
| Unintended Function | 非预期激活 | 该功能在未被指令的情况下激活时会发生什么？ |
| Too Early / Too Late | 时序错误 | 该功能激活时机不对时会发生什么？ |

**危害清单表格：**
```
| H-ID | 危害描述 | 相关功能 | 失效类型 | 失效来源 | 状态 |
| H-01 | 意外施加正向驱动力（车辆非预期加速）| F-01 | Unintended Function | item 输出端 | NEEDS_USER_CONFIRMATION |
| H-02 | 驱动力完全丧失（动力中断）| F-01 | No Function | item 内部 | NEEDS_USER_CONFIRMATION |
| H-03 | 制动力意外施加（车辆非预期减速/制动）| F-02 | Unintended Function | item 输出端 | NEEDS_USER_CONFIRMATION |
```
注：H-ID 描述危害行为本身，不描述"在什么工况下"——工况在 HE 中描述。

---

#### SEC-HE（危害事件表）

**分析步骤：**对每个危害 H-xx，与每个工况 OS-xx 组合，判断该组合是否构成危害事件（并非所有组合均需列出，不成立的组合可注明原因省略）。

**危害事件描述格式：**`在[工况描述]（OS-xx）中，[危害行为]（H-xx），可能导致[潜在后果]`

```
| HE-ID | H-ID | OS-ID | 危害事件描述 | 是否成立 | 说明/状态 |
| HE-001 | H-01 | OS-01 | 在高速公路行驶中（OS-01），车辆非预期加速（H-01），可能导致追尾或冲出道路 | 是 | NEEDS_USER_CONFIRMATION |
| HE-002 | H-01 | OS-03 | 在停车场低速机动中（OS-03），车辆非预期加速（H-01），可能撞击障碍物或行人 | 是 | NEEDS_USER_CONFIRMATION |
| HE-003 | H-02 | OS-01 | 在高速公路行驶中（OS-01），驱动力完全丧失（H-02），可能导致追尾（后方车辆）| 是 | NEEDS_USER_CONFIRMATION |
| HE-004 | H-01 | OS-04 | 在恶劣天气行驶中（OS-04），车辆非预期加速（H-01），危害加剧 | 是 | NEEDS_USER_CONFIRMATION |
```

---

#### SEC-SEC（S/E/C 评级与 ASIL 候选表）

**S/E/C 定义速查（ISO 26262-3）：**

| 等级 | Severity | Exposure | Controllability |
|---|---|---|---|
| 0 | 无伤亡 | 极低（<1%，几乎不可能）| 总是可控 |
| 1 | 轻/中度伤 | 很低（<1%/操作，罕见）| 简单可控（≥99%驾驶员）|
| 2 | 重伤，存活可能 | 低（偶尔发生，驾驶条件特定）| 通常可控（≥90%驾驶员）|
| 3 | 危及生命/死亡 | 中等（城市日常驾驶中可能）| 难控（<90%驾驶员）|
| 4 | — | 高（几乎所有驾驶时间均存在）| — |

**ASIL 候选查表（ISO 26262-3 Table 4 简化）：**

| S/E | C1 | C2 | C3 |
|---|---|---|---|
| S1+E1 | QM | QM | QM |
| S1+E2 | QM | QM | QM |
| S1+E3 | QM | QM | A |
| S1+E4 | QM | A | B |
| S2+E1 | QM | QM | QM |
| S2+E2 | QM | QM | A |
| S2+E3 | QM | A | B |
| S2+E4 | A | B | C |
| S3+E1 | QM | QM | A |
| S3+E2 | QM | A | B |
| S3+E3 | A | B | C |
| S3+E4 | B | C | D |

**评级表格：**
```
| HE-ID | 危害事件描述（简）| S候选 | S依据摘要 | E候选 | E依据摘要 | C候选 | C依据摘要 | ASIL候选 | 状态 |
| HE-001 | 高速公路非预期加速 | S3 | 高速追尾可能致命 | E4 | 高速行驶占大量驾驶时间 | C3 | 非预期加速响应时间极短，难以控制 | D | NEEDS_USER_CONFIRMATION |
| HE-002 | 停车场非预期加速 | S2 | 低速撞击可能重伤（行人/老人）| E2 | 停车场驾驶场景为偶发 | C2 | 低速下驾驶员有一定反应时间 | A | NEEDS_USER_CONFIRMATION |
```
所有评级值均为**候选值**，必须加注 `NEEDS_USER_CONFIRMATION`，不得写成最终确认值。

---

#### SEC-SG（安全目标候选表）

**适用范围：** 仅为 ASIL 候选 > QM（即 ASIL A/B/C/D）的危害事件生成安全目标。

**安全目标措辞规则：**
- 采用**禁止性表述**：`[item名称]不应在[工况/运行条件]下[危害行为]，以防止[后果]`
- 不使用"应该"或"保证"等正面义务表述
- 不断言 ASIL 已确认

**安全目标表格：**
```
| SG-ID | 安全目标描述 | ASIL候选 | 相关HE-ID | 来自H-ID | 状态 |
| SG-01 | 在正常行驶工况下，[item名称]不应意外施加驱动力，以防止车辆失控、追尾或碰撞造成人员伤亡 | ASIL D | HE-001, HE-004 | H-01 | NEEDS_USER_CONFIRMATION |
| SG-02 | 在停车场低速机动工况下，[item名称]不应意外施加驱动力，以防止撞击行人或障碍物造成人员伤害 | ASIL A | HE-002 | H-01 | NEEDS_USER_CONFIRMATION |
```

---

#### 通用保守写作原则

1. 所有 HARA critical claim（H-xx 存在性、HE 成立性、S/E/C 值、ASIL 等级、SG 措辞）在缺乏 HITL 确认时，统一标注 `[NEEDS_USER_CONFIRMATION]`
2. 缺乏 T1 source 支撑的内容，写 `[依据现有材料无法确认，待工程师确认]`，不推断填值
3. 严禁使用：`ASIL is D`、`ASIL D（已确认）`、`risk is acceptable`、`safety goal approved`、`the rating is S3` 等最终批准措辞
4. 表格中无法确定的值用 `[PENDING]` 填充，并在对应 SEC-OPEN 中汇总

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按章节逐节核对。
- 方案C 先扫高风险约束（HARA critical claim 支撑与 forbidden final claims）再补其余。

### 典型审核子任务
1. 核对草稿是否超出证据范围。
2. 核对 HARA critical claim 无 T0/T1 时是否保持 `NEEDS_USER_CONFIRMATION` / pending。
3. 核对是否出现 `final ASIL is approved`/`risk is acceptable`/`the rating is S/E/C` 等批准或评级断言。
4. 核对 source tier 与 claim 状态是否保留、sample/reference 是否未被当事实。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 一任务一章节顺序成稿。
- 方案B 先成稿证据充分章节再处理待证章节。
- 方案C 按写作模式分组成稿。

### 典型修订子任务
1. 遍历 section_tasks 逐任务并匹配 citation_plan 章节。
2. 校验任务证据只用 allowed evidence ids。
3. 逐节渲染保守草稿（HARA critical claim 章节保守措辞）。
4. 汇编 full_draft.md 并保留 tier/claim/HITL 状态。

## state.json 示例（HARA）

```json
{
  "step": "conservative-draft",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对草稿未超出证据范围", "status": "done"},
      {"id": "rv-2", "desc": "核对 HARA critical claim 无 T0/T1 时保持 pending", "status": "running"},
      {"id": "rv-3", "desc": "核对未出现批准/评级断言、保留 tier/claim 状态", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "遍历 section_tasks 并匹配 citation_plan 章节", "status": "done"},
      {"id": "rt-2", "desc": "校验任务证据只用 allowed evidence ids", "status": "running"},
      {"id": "rt-3", "desc": "逐节渲染保守草稿", "status": "not_run"},
      {"id": "rt-4", "desc": "汇编 full_draft.md 并保留 tier/claim/HITL 状态", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：草稿是否超出证据范围；HARA critical claim（hazard/hazardous event/S-E-C/ASIL/safety goal/final acceptability）无 T0/T1 时是否保持 `NEEDS_USER_CONFIRMATION` / pending；是否出现 `final ASIL is approved`/`risk is acceptable`/`the rating is S1/S2/S3/E1/E2/E3/C1/C2/C3` 等 forbidden final claims；source tier 与 claim 状态是否保留；sample/reference 是否未被当作事实证据。
