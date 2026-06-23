# HARA 子 skill · Step 7 · 引用计划 (Citation Plan)

本文件是通用骨架 `skills/workflow-steps/step-citation-plan/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 按 **L1 章 + L2 小节**（`outline_l1.md` + `outline_l2.md`）顺序把研究问题与证据映射归并到各 HARA 章节与小节（group_research_questions / evidence_by_question）。
- 为每节判定 requires_human_confirmation，生成 citation_slots、unsupported_claims、weak_notes。
- 产出 `plans/citation_plan.json`（claim → 来源引用槽）与 `plans/claim_support_matrix.json`（N4 核心溯源矩阵，含 source tier 与 claim 状态）。
- HARA critical claim（hazard、hazardous event、S/E/C、ASIL、safety goal、final acceptability）无 T0/T1 支撑时保持 `NEEDS_USER_CONFIRMATION` / pending / open。
- **底线**：不得为缺证据的 HARA claim 编造引用；不得用 sample/reference 充当 critical claim 的支撑来源。

## HARA 报告过程总览（本步定位）

HARA 报告中每个 critical claim 都需要可见的引用证据。本步把 evidence-map 落到具体 citation_slot，规划「哪段证据 → 哪个章节槽位」。

**HARA citation 规划核心规则**：

- 每条 hazard / HE / S-E-C / ASIL / SG 在草稿中须有显式 `citation_slot` 指向 T0/T1 证据
- `claim_support_matrix` 记录每条 critical claim 的支撑等级与状态
- 未充分支撑的 claim 仍可保留为 candidate + `NEEDS_USER_CONFIRMATION`，**不可省略不写**

**本步定位**：决定每个章节将"看见"哪些证据；草稿撰写时严格遵守 plan，不引入计划外证据，更不引入 sample 作为支撑。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`citation_plan.json`、`claim_support_matrix.json`）将在 Step 10/11 被以下检查点定位。subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-1-04 | claim_support_matrix 存在 | 文件可解析，含每条 critical claim 行 |
| VC-2-01/02/03 | 各 claim 的 tier 字段合规 | 无 H / HE / S / E / C / ASIL / SG 的支撑 tier 为 T4 / T5；评级支撑不为单纯 T3 |
| RD-4 | E 评级有 T1 工况 source 引用 | 遍历 HE 的 E citation_slot，引用 OS-xx + 对应 T1 source |
| RD-6 | 未充分支撑的 claim 不被省略 | claim_support_matrix 中弱支撑 claim 仍以 candidate + `NEEDS_USER_CONFIRMATION` 出现 |

**自检底线**：每条 hazard / HE / S-E-C / ASIL / SG 都应在草稿中有显式 `citation_slot`，**绝不**为缺证据的 HARA claim 编造引用，更不用 sample / reference 充当 critical claim 的支撑来源。



## ISO 26262-3 标准 Checklist 与 Review 要点（Clause 对照）

本步对应 Phase E4（ASIL 确定）的引用编排：每个 ASIL 候选必须可被独立审核员**重算**——这就要求引用槽（citation slot）逐字段（S/E/C）都指向具体 T1 source。

### Checklist（引用计划）

- [ ] `claim_support_matrix.json` 每条 critical claim 含 `tier` 字段
- [ ] 每个 HE 的 S citation_slot 引用 T1 source（item 定义 / 伤害分析）
- [ ] 每个 HE 的 E citation_slot 引用 OS-xx + 对应 T1 工况 source
- [ ] 每个 HE 的 C citation_slot 引用 T1 source（驾驶员响应分析或 ODD）
- [ ] 每个 HE 的 ASIL citation_slot 指向 ISO 26262-3 **Table 4**（T3）+ 上述 S/E/C 的 T1 证据
- [ ] 每个 SG citation_slot 指向其覆盖的 HE 与 Safe State / FTTI 设定依据
- [ ] 弱支撑 claim 不省略，保留 candidate + `NEEDS_USER_CONFIRMATION`
- [ ] 无 sample / reference 进入 critical claim 引用槽

### Review 要点

| 失效 | 级别 |
|---|---|
| 为缺证据 claim 编造引用 | **P0** |
| E 评级引用 sample 而非 T1 工况 source | **P0** |
| ASIL 引用未含 Table 4 与 S/E/C 三方支撑 | **P0** |
| 引用槽 tier 字段缺失 | **P1** |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主要风险 | 引用槽空缺被默认填默认值 | sample 的 critical claim 引用被原样保留 |
| 本步动作 | 缺证据槽保留 candidate + 登记 unresolved | 即使 sample 显示相同 HE 已有评级，本项目 ASIL 引用必须独立查 Table 4；引用计划须为 Step 9 的 **独立重算**预留位 |


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA 章节引用槽（citation_slots）设计

citation_slot 宜对齐 **L2 小节**（`outline_l2.md` / `template_structure` level=2 节点）；同一 L1 下多个 L2 可分别承载不同 claim 类型：

| HARA L1 / L2 | claim 类型 | citation_slot 类型 | 支撑来源 tier | 无支撑时的处理 |
|---|---|---|---|---|
| SEC-ITEM · 功能清单（L2） | item_function | source_citation | T1 | unsupported_claim：F-xx 功能描述无 T1 支撑 |
| SEC-ITEM · 系统边界（L2） | item_boundary | source_citation | T1 | unsupported_claim：系统边界无 T1 支撑 |
| SEC-OPS · OS-xx 工况表（L2）| operational_situation | source_citation | T1 | unsupported_claim：OS-xx 无 T1 source |
| SEC-HAZ · H-xx 危害表（L2）| hazard_identification | source_citation + confirmation_slot | T1 + HITL | NEEDS_USER_CONFIRMATION |
| SEC-HE · HE-xxx 表（L2）| hazardous_event | source_citation + confirmation_slot | T1 + HITL | NEEDS_USER_CONFIRMATION |
| SEC-SEC · S 评级（L2）| severity_rating | confirmation_slot | T0/T1 + HITL | NEEDS_USER_CONFIRMATION；weak_note 若仅 T3 |
| SEC-SEC · E 评级（L2）| exposure_rating | confirmation_slot | T0/T1 + HITL | NEEDS_USER_CONFIRMATION；weak_note 若仅 T3 |
| SEC-SEC · C 评级（L2）| controllability_rating | confirmation_slot | T0/T1 + HITL | NEEDS_USER_CONFIRMATION；weak_note 若仅 T3 |
| SEC-SEC · ASIL 候选（L2）| asil_candidate | confirmation_slot | T3（矩阵方法）+ T0/T1（S/E/C值）+ HITL | NEEDS_USER_CONFIRMATION |
| SEC-SG · SG-xx 表（L2）| safety_goal | confirmation_slot | T0/T1（HE/ASIL）+ HITL | NEEDS_USER_CONFIRMATION |

### claim_support_matrix 核心字段

`plans/claim_support_matrix.json` 每条记录包含：

```
claim_id:           H-01 / HE-001 / HE-001.S / HE-001.E / HE-001.C / HE-001.ASIL / SG-01
claim_type:         hazard / hazardous_event / severity / exposure / controllability / asil / safety_goal
section_id:         L2 小节 id（如 SEC-ITEM-L2-01）；parent_section_id: L1（如 SEC-ITEM）
evidence_ids:       [EVD-001, EVD-002]  ← Step 6；须回溯 L1/L2/L3 + location
provenance_ref:     { file_id, l1_title, l2_title, l3_title, location }
tier:               T1 / T3 / weak / none
status:             supported / weak / unsupported / pending
requires_human_confirmation: true / false
```

### unsupported_claims 与 weak_notes 记录规则

- **unsupported_claim** 示例：`H-01 危害识别：无 T1 source 对应该功能失效模式描述`
- **unsupported_claim** 示例：`HE-003 危害事件：工况 OS-03 无 T1 source 支撑`
- **weak_note** 示例：`HE-001.E：E评级仅由 T3（ISO 26262-3 Table 2 定义）支撑，缺 T1 工况频率 source`
- **不得写**：`SG-01：安全目标由 sample HARA 报告（T4）中的类似案例支撑` ← 这是 P0 违规

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按 artifact/章节逐项核对。
- 方案C 先扫高风险约束（HARA critical claim 的 T0/T1 支撑与未为缺证据 claim 编造引用）再补其余。

### 典型审核子任务
1. 核对 claim_support_matrix 保留 source tier 与 claim 状态。
2. 核对 HARA critical claim 由 T0/T1 支撑或保持 `NEEDS_USER_CONFIRMATION` / pending。
3. 核对未为缺证据 HARA claim 编造引用。
4. 核对 citation_plan/claim_support_matrix 符合 artifact 契约。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 按 outline 顺序逐章节归并。
- 方案B 先按 claim 聚合再回填章节。
- 方案C 先处理 HARA critical claim 再补普通 claim。

### 典型修订子任务
1. 按 outline 顺序归并 research_questions 与 evidence（group_research_questions）。
2. 逐节判定 requires_human_confirmation。
3. 生成 citation_slots/unsupported_claims/weak_notes。
4. 建 claim_support_matrix（N4 溯源，含 tier 与 claim 状态）。

## state.json 示例（HARA）

```json
{
  "step": "citation-plan",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对 claim_support_matrix 保留 tier 与 claim 状态", "status": "done"},
      {"id": "rv-2", "desc": "核对 HARA critical claim 由 T0/T1 支撑或保持 pending", "status": "running"},
      {"id": "rv-3", "desc": "核对未为缺证据 claim 编造引用", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "按 outline 归并 research_questions 与 evidence", "status": "done"},
      {"id": "rt-2", "desc": "逐节判定 requires_human_confirmation", "status": "running"},
      {"id": "rt-3", "desc": "生成 citation_slots/unsupported_claims/weak_notes", "status": "not_run"},
      {"id": "rt-4", "desc": "建 claim_support_matrix（N4 溯源）", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：`claim_support_matrix.json` 是否保留 source tier 与 claim 状态；HARA critical claim 是否有 T0/T1 支撑或保持 `NEEDS_USER_CONFIRMATION` / pending；是否存在为缺证据 HARA claim 编造的引用。
