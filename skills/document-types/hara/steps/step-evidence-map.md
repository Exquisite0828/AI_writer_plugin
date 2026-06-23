# HARA 子 skill · Step 6 · 证据·引用·章节计划（合并原 6–8）

本文件是 `skills/workflow-steps/step-evidence-map/SKILL.md` 在 `task_type: hara` 下的任务专属子 skill。HARA 领域规则以 `skills/document-types/hara/SKILL.md` 为准。

**原 Step 7（引用计划）与 Step 8（章节任务）已合并入本步**，分 Phase A/B/C 顺序执行。

## 本步目的要点（HARA）

- 读取 Step 5 的 `section_writing_plans.json`，对每 L2 小段**顺序完成**：
  - **Phase A**：`required_evidence` → **L1→L2→L3→原文** → `EVD-xxx`；未解决 → `unresolved_questions.md`
  - **Phase B**：claim ↔ `EVD-xxx` → `citation_plan.json`、`claim_support_matrix.json`
  - **Phase C**：`TASK-xxx` + `outline_final.md` + `writing_plan.md`
- critical claim（hazard/HE/S-E-C/ASIL/SG）只接受 T0/T1；无支撑保持 `NEEDS_USER_CONFIRMATION`。
- **底线**：禁止 T4 sample 作事实证据；禁止编造引用；不在此步写正文或预设 hazard/rating/ASIL/SG 结论。

---

## Phase A · 证据映射

### 执行粒度

按 `outline_l2.md` 每 L2 登记一条 `em-*` 子任务（与 Step 5 的 `sp-*` 对齐）。

### HARA 证据映射规则

| tier | 对 critical claim |
|---|---|
| T0（HITL） | 可支撑所有 critical claim |
| T1（项目 source） | 可支撑事实描述；配合 T3 形成评级候选依据 |
| T2 | 仅结构，不支撑 claim 内容 |
| T3 | 方法框架，**不能单独支撑具体评级值** |
| T4（sample） | **绝不进入** critical claim 证据 |
| T5 | 不接受 |

### 各段 required_evidence 导航主题（示例）

| L2 类型 | 可接受 tier | topic_index / L1/L2/L3 主题 |
|---|---|---|
| 功能清单 / 边界 / 接口 | T1 | 功能描述、系统边界、接口、运行约束 |
| OS-xx 工况表 | T1 | 工况、道路、速度、暴露频率 |
| H-xx 危害表 | T1 + HITL | F-xx 失效行为、功能边界 |
| HE-xxx 表 | T1 + HITL | 危害×工况、潜在后果 |
| S / E / C 评级 | T0/T1 + T3 方法 | 伤害场景；工况频率（**非**失效概率）；驾驶员响应 |
| ASIL 候选 | T3 Table 4 + T0/T1 S/E/C | 查表方法 + 三方值依据 |
| SG-xx | T0/T1 + HITL | HE、ASIL 候选、Safe State/FTTI 依据 |

### unresolved_questions.md

登记：无 T0/T1 的 critical 项；E 与失效概率混淆；S/E/C 仅 T3；gap 无法 L3 定位。**不得**写推断性评级结论。

### Phase A 自检

| 检查 | 级别 |
|---|---|
| critical claim evidence 指向 T4 | **P0** |
| E 用 fault rate 而非暴露频率 | **P0** |
| S/E/C 仅 T3 支撑 | **P1** |

---

## Phase B · 引用计划

Phase A 全部 `done` 后执行。按 L1/L2 把 claim 与 `EVD-xxx` 归并。

### citation_slots（对齐 L2）

| HARA L1 / L2 | claim 类型 | 无支撑处理 |
|---|---|---|
| SEC-ITEM · 功能清单 | item_function | unsupported_claim |
| SEC-ITEM · 系统边界 | item_boundary | unsupported_claim |
| SEC-OPS · OS-xx | operational_situation | unsupported_claim |
| SEC-HAZ · H-xx | hazard_identification | NEEDS_USER_CONFIRMATION |
| SEC-HE · HE-xxx | hazardous_event | NEEDS_USER_CONFIRMATION |
| SEC-SEC · S/E/C/ASIL | severity/exposure/controllability/asil | NEEDS_USER_CONFIRMATION |
| SEC-SG · SG-xx | safety_goal | NEEDS_USER_CONFIRMATION |

### claim_support_matrix 字段

```
claim_id, claim_type, section_id, parent_section_id
evidence_ids: [EVD-xxx]  ← Phase A
provenance_ref: { file_id, l1, l2, l3, location }
tier, status, requires_human_confirmation
```

弱支撑 claim 保留 candidate + `NEEDS_USER_CONFIRMATION`，**不可省略**。

### Phase B 自检

| 失效 | 级别 |
|---|---|
| 为缺证据 claim 编造引用 | **P0** |
| E 引用 sample 非 T1 工况 | **P0** |
| ASIL 引用缺 Table 4 + S/E/C 三方 | **P0** |

---

## Phase C · 章节任务

Phase B 全部 `done` 后执行。按 `outline_l2` 生成 `TASK-xxx`（与 Step 5 写作计划一致；冲突以 outline_l2 为准）。

| TASK-ID | L1 / L2 | writing_mode | HITL |
|---|---|---|---|
| TASK-05a–d | SEC-ITEM 各 L2 | conservative_candidate | 部分 |
| TASK-06 | SEC-OPS · OS-xx | conservative_candidate | 是 |
| TASK-07 | SEC-HAZ · H-xx | confirmation_required | ★ |
| TASK-08 | SEC-HE · HE-xxx | confirmation_required | ★ |
| TASK-09–12 | SEC-SEC · S/E/C/ASIL | confirmation_required | ★ |
| TASK-13 | SEC-SG · SG-xx | confirmation_required | ★ |
| TASK-14 | SEC-OPEN | open_issue_list | — |
| TASK-15 | SEC-REVIEW | supported | — |

每条 TASK 须含：`section_id`、`allowed_evidence`（EVD-xxx）、`citation_slots` 引用、 `claim_status`。

`outline_final.md` = Step 4 L1+L2 + 引用计划合并后的可写结构。

With-Reference 须含 **TASK-DIFF**。

### Phase C 自检

| 失效 | 级别 |
|---|---|
| mandatory section 无 TASK | **P0** |
| TASK 预设 hazard/ASIL/SG 结论 | **P0** |
| TASK-SG 未要求 FTTI / Safe State | **P0** |
| allowed_evidence 非本步 EVD | **P1** |

---

## execution_state 示例（HARA）

```json
{
  "step": "evidence-map",
  "execution_state": {
    "phases": [
      {
        "id": "phase-a",
        "name": "证据映射",
        "status": "running",
        "subtasks": [
          {"id": "em-05", "section_id": "SEC-ITEM-L2-01", "desc": "功能清单 EVD 映射", "status": "done"},
          {"id": "em-10", "section_id": "SEC-HAZ-L2-01", "desc": "危害表 EVD 映射", "status": "not_run"}
        ]
      },
      {
        "id": "phase-b",
        "name": "引用计划",
        "status": "not_run",
        "subtasks": [
          {"id": "cp-item", "desc": "SEC-ITEM/OPS citation + matrix", "status": "not_run"},
          {"id": "cp-critical", "desc": "SEC-HAZ/HE/SEC/SG citation + matrix", "status": "not_run"}
        ]
      },
      {
        "id": "phase-c",
        "name": "章节任务",
        "status": "not_run",
        "subtasks": [
          {"id": "st-all", "desc": "TASK-xxx + outline_final + writing_plan", "status": "not_run"}
        ]
      }
    ]
  }
}
```

---

## A1 审核任务（HARA）

1. Phase A/B/C 子任务是否全部 `done`。
2. 七类 artifact 是否齐全且互一致（EVD ↔ matrix ↔ TASK allowed_evidence）。
3. critical claim 是否仅 T0/T1；无证据是否 open/unresolved。
4. 是否未用 sample 当事实、未预设 hazard/rating/ASIL 结论。

## A2 修订任务（HARA）

1. 定位失败 phase，将该 phase 有关子任务置 `not_run`。
2. 从该 phase **顺序重跑**至完成。
3. 重新合并下游 phase artifact（若 Phase A 变更，须重跑 B、C）。

## B 审核检查项（HARA）

subagent 逐项核对：Phase A EVD provenance 完整；Phase B matrix tier 合规、无编造引用；Phase C TASK 覆盖 12 章、writing_mode 保守、allowed_evidence 可追溯；`unresolved_questions.md` 含全部 open 项。
