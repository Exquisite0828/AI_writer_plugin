# HARA 子 skill · Step 11 · 验证 (Verification)

本文件是通用骨架 `skills/workflow-steps/step-verification/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 对 HARA 草稿与审查结果做确定性验证检查，把未通过项显式列出。
- HARA REQUIRED_CHECKS 覆盖：required artifacts 齐全、citation integrity、source tier 与 provenance、sample/reference 非事实来源、critical claims 确认状态、`NEEDS_USER_CONFIRMATION` 保留、candidate update inactive。
- 失败项如实写入 `verify/failures.md`，不得静默通过。
- 验证 `status` 保守，不输出 `validated` 等批准措辞。
- 验证是确定性检查，不替代专业判断或最终批准。

## HARA 报告过程总览（本步定位）

审查关注内容质量，验证关注最终交付前的合规检查。本步运行机器化检查，证明输出符合 HARA artifact 契约与硬约束。

**HARA 验证必过项**：

| 类别 | 核心检查 |
|---|---|
| 产物齐全 | manifest / source index / 草稿 / 审查记录 / 开放项汇总 全部存在 |
| Source Tier 合规 | 无 T4（sample）或 T5（推断）作为 critical claim 证据 |
| Critical Claim 状态 | 全部 H-xx / HE-xxx / S/E/C / ASIL / SG 标 `NEEDS_USER_CONFIRMATION` |
| ASIL 逻辑 | ASIL 候选由 S/E/C 经 Table 4 查表得出，逻辑一致 |
| 禁止操作 | 无「ASIL is approved」/「risk is acceptable」/「已确认」等批准语义 |

**本步定位**：失败立即记入 `failures.md`，阻断进入 Step 13；通过则进入最终报告打包。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`verify/failures.md`、`verify_report.json`）将在 Step 13 最终报告打包前被使用。subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| 元验证 | 5 类 REQUIRED_CHECKS 逐项有结论 | VC-1 / VC-2 / VC-3 / VC-4 / VC-5 每个 CHECK-ID 均有 pass / fail 判定 |
| 元验证 | 失败项如实写入 failures.md | 任何 fail 都进入 failures.md，不静默通过 |
| 元验证 | status 保守 | verify_report.status ∈ `passed_with_open_items` / `failed` / `blocked`，无 `validated` |
| 元验证 | 阻断项可见 | P0 fail 在 failures.md 中以 `### P0 (Blocking)` 节列出 |
| 元验证 | 通过项可追溯 | passed 项在 failures.md 末尾的 `### Passed` 节列出 CHECK-ID |

**自检底线**：验证是确定性检查，不替代专业判断或最终批准；任何 P0 失败必须阻断进入 Step 13。


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA REQUIRED_CHECKS（验证检查清单）

以下检查逐条执行，结果写入 `verify/failures.md`，失败项不得静默跳过：

#### VC-1 必要产物齐全性
| CHECK-ID | 检查项 | 通过条件 | 失败处理 |
|---|---|---|---|
| VC-1-01 | manifest.yaml 存在且可解析 | 文件存在，role/tier/is_fact_source 字段完整 | FAIL: manifest 缺失或字段不完整 |
| VC-1-02 | source_index 存在 | `artifacts/source_index.json` 存在 | FAIL: source index 缺失 |
| VC-1-03 | template_structure 存在 | `artifacts/template_structure.json` 存在，含 12 个 section_id | FAIL: 模板结构缺失 |
| VC-1-04 | claim_support_matrix 存在 | `plans/claim_support_matrix.json` 存在 | FAIL: 引用矩阵缺失 |
| VC-1-05 | draft 草稿存在 | `draft/hara_draft.md` 存在且非空 | FAIL: 草稿缺失 |
| VC-1-06 | review 记录存在 | `review/review_findings.md` 存在 | FAIL: 未经审查 |
| VC-1-07 | unresolved_questions 存在 | `plans/unresolved_questions.md` 存在（可为空列表） | FAIL: 未确认项汇总缺失 |

#### VC-2 source tier 合规性（Citation Integrity）
| CHECK-ID | 检查项 | 通过条件 | 失败处理 |
|---|---|---|---|
| VC-2-01 | 无 T4（sample）作为 critical claim 支撑 | claim_support_matrix 中无任何 H-xx/HE-xxx/S/E/C/ASIL/SG 的 evidence_ids 指向 tier=T4 | P0 FAIL: sample 被用作事实 source |
| VC-2-02 | 无 T5（推断）作为任何 claim 支撑 | 无 tier=T5 的 evidence 进入 claim_support_matrix | P0 FAIL: 推断作为 source |
| VC-2-03 | reference（T3）不单独支撑具体评级值 | claim_support_matrix 中 S/E/C 的 tier 字段不为单纯 T3 | P1 FAIL: 评级仅由方法框架支撑 |
| VC-2-04 | 每条 SRC-xxx 记录含 provenance | source_index 每条有 file_id + 章节/行号/段落位置 | P1 FAIL: provenance 为空 |

#### VC-3 Critical Claims 状态检查
| CHECK-ID | 检查项 | 通过条件 | 失败处理 |
|---|---|---|---|
| VC-3-01 | 所有 H-xx 状态含 NEEDS_USER_CONFIRMATION | draft 中无 H-xx 的状态字段写成"已确认"/"approved" | P0 FAIL: 危害状态被提前确认 |
| VC-3-02 | 所有 HE-xxx 状态含 NEEDS_USER_CONFIRMATION | draft 中无 HE-xxx 的状态字段写成"已确认" | P0 FAIL: 危害事件被提前确认 |
| VC-3-03 | 所有 S/E/C 值含 NEEDS_USER_CONFIRMATION | 评级表状态列无批准措辞 | P0 FAIL: 评级被提前确认 |
| VC-3-04 | 所有 ASIL 值为候选值 | 无"ASIL is D"/"ASIL D（已批准）"等措辞 | P0 FAIL: ASIL 被断言为最终值 |
| VC-3-05 | 所有 SG 描述使用禁止性表述 | 无"保证"/"确保正常工作"/"ensure" | P1 FAIL: 安全目标措辞违反保守原则 |

#### VC-4 ASIL 逻辑一致性
| CHECK-ID | 检查项 | 通过条件 | 失败处理 |
|---|---|---|---|
| VC-4-01 | S/E/C → ASIL 映射逻辑正确 | 每条 HE 的 ASIL 候选值与 S×E×C 按 ISO 26262-3 Table 4 查表结果一致 | P1 FAIL: ASIL 候选值与 S/E/C 不一致 |
| VC-4-02 | ASIL>QM 的 HE 均有 SG | SG 数量 ≥ ASIL 候选值 > QM 的 HE 数量 | P1 FAIL: 缺少安全目标覆盖 |
| VC-4-03 | ASIL=QM 的 HE 无 SG | SG 表无对应 QM HE 的行 | P2 FAIL: QM 事件被错误生成安全目标 |

#### VC-5 禁止操作检查
| CHECK-ID | 检查项 | 禁止措辞/操作 | 失败处理 |
|---|---|---|---|
| VC-5-01 | 无专业批准措辞 | "ASIL is approved"/"risk is acceptable"/"safety goal approved"/"HARA完成" | P0 FAIL |
| VC-5-02 | NEEDS_USER_CONFIRMATION 标记保留 | 审查/验证步骤未移除任何草稿中的 NEEDS_USER_CONFIRMATION | P0 FAIL |
| VC-5-03 | candidate update 处于 proposed/inactive | state.json candidate_update.status ≠ "active"/"promoted" | P0 FAIL |
| VC-5-04 | 无静默解析失败 | manifest 中声明的每个 file_id 均有 parse_status 记录（非空） | P1 FAIL |

### verify/failures.md 格式规范

```
## HARA Verification Failures

### P0 (Blocking)
- [VC-2-01] H-01 危害描述的 source EVD-003 指向 tier=T4（sample_hara.pdf），不得用作事实支撑
- [VC-3-04] 草稿第89行出现"ASIL D（已批准）"——禁止出现最终批准措辞

### P1 (Must Fix)
- [VC-4-01] HE-005：S2+E3+C2 按 Table 4 应为 A，但草稿写 B
- [VC-1-05] claim_support_matrix 中 SG-03 无对应 evidence_ids

### P2 (Recommended)
- [VC-4-03] SG 表中 HE-007（ASIL=QM）被错误生成 SG-06

### Passed
- VC-1-01 ~ VC-1-07：所有必要产物存在
- VC-5-01：草稿无专业批准措辞
```

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按 HARA artifact 逐项核对。
- 方案C 先扫高风险约束（失败项是否静默通过、是否出现 `validated` 等批准措辞）再补其余。

### 典型审核子任务
1. 核对失败项是否如实写入 `failures.md` 而非静默通过。
2. 核对 `status` 是否保守、未输出 `validated` 等批准措辞。
3. 核对 HARA REQUIRED_CHECKS 是否逐项均有结论（含 `NEEDS_USER_CONFIRMATION` 保留、sample 非事实）。
4. 核对 verify_report/failures 是否符合 artifact 契约。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 按 REQUIRED_CHECKS 顺序逐项执行。
- 方案B 先跑阻断类检查（ASIL 无支撑、safety goal 未确认）再补其余。
- 方案C 按 artifact 维度分组检查（citation/tier/confirmation/sample）。

### 典型修订子任务
1. 遍历 HARA REQUIRED_CHECKS 逐项执行确定性检查（required artifacts、citation integrity、source tier、sample 非事实、critical claims、NEEDS_USER_CONFIRMATION 保留、candidate inactive）。
2. 为每项判定 status，收集 blocking_failures。
3. 把失败项如实写入 `verify/failures.md`，不得静默通过。
4. 汇总 `verify/verify_report.json`，status 保持保守。

## state.json 示例（HARA）

```json
{
  "step": "verification",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对失败项如实写入 failures.md 而非静默通过", "status": "done"},
      {"id": "rv-2", "desc": "核对 status 保守、未输出 validated 等措辞", "status": "running"},
      {"id": "rv-3", "desc": "核对 HARA REQUIRED_CHECKS 逐项均有结论", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "遍历 HARA REQUIRED_CHECKS 逐项执行确定性检查", "status": "done"},
      {"id": "rt-2", "desc": "为每项判定 status，收集 blocking_failures", "status": "running"},
      {"id": "rt-3", "desc": "把失败项如实写入 failures.md", "status": "not_run"},
      {"id": "rt-4", "desc": "汇总 verify_report.json 保持保守 status", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：失败项是否如实写入 `failures.md` 而非静默通过；`status` 是否保守（未输出 `validated` 等批准措辞）；HARA REQUIRED_CHECKS（required artifacts、citation integrity、source tier/provenance、sample/reference 非事实来源、critical claims 确认状态、`NEEDS_USER_CONFIRMATION` 保留、candidate update inactive）是否逐项均有明确结论。
