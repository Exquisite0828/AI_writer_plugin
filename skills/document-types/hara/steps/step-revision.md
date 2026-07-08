# HARA 子 skill · Step 12 · 修订 (Revision)

本文件是通用骨架 `skills/workflow-steps/step-revision/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 领域补充）

- 依据 HARA 审查/验证结果生成确定性修订计划，逐条修订草稿，不引入未支撑的新 HARA 结论。
- 无法解决的 HARA 开放项（hazard/S-E-C/ASIL/safety goal 等未经 HITL 确认）继续带入最终交付的 open items，保持 pending。
- HITL pending 不得自动改为 confirmed，不输出批准类措辞。
- 修订有据可查：每条修订对应审查/验证指出的问题，变更记录写入 `revised/change_log.md`。
- **底线**：不引入无来源支撑的 HARA 新结论，不把 sample/reference 当作事实证据。

## HARA 报告过程总览（本步定位）

修订须由 Step 10 审查与 Step 11 验证发现的明确问题驱动。本步是 HARA 流程的迭代闭环点。

**HARA 修订核心原则**：

- 修订是**目的驱动**，不是机械重跑脚本
- 禁止把 `NEEDS_USER_CONFIRMATION` 修订成专业批准结论
- 禁止用 sample / reference 内容补 hazard / rating / ASIL / SG 缺口
- 知识缺口型问题：修订只能登记 `knowledge_gap`，不能凭空填值
- 修订完成后回到 Step 10/11 重新审查验证，直到无 P0 或显式 HITL 接受

**本步定位**：把审查 / 验证问题转化为定向 `revision_plan`，限定修改范围与允许操作，可被回放。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（修订后的 `hara_draft.md` + `revised/change_log.md`）将在重跑 Step 10/11 后被以下检查点定位。subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-5-02 | NEEDS_USER_CONFIRMATION 未被移除 | diff 检查：修订前后 pending 标记数量不减少（除非 HITL 已记录确认）|
| VC-2-01/02 | 不引入 sample / 推断作为新证据 | 修订引入的引用 tier ≠ T4 / T5 |
| VC-5-01 | 不引入新的批准措辞 | diff 中无 `approved` / `validated` / `compliant` 新增 |
| 元修订 | change_log 完整 | 每条修订对应 review_findings 或 failures.md 中的具体 issue ID |
| 元修订 | 不引入新的 P0 | 修订后重跑 Step 10 不产生新 P0（结构 / 引导词覆盖 / ASIL 逻辑） |
| 元修订 | 知识缺口型问题以登记代替填值 | 修订后 unresolved_questions / knowledge_gaps 数量可增加，不能凭空填值 |

**自检底线**：修订是**目的驱动**，不是机械重跑；HITL pending 不得自动改为 confirmed；修订完成后必须回到 Step 10/11 重新审查验证，直到无 P0 或显式 HITL 接受。



## ISO 26262-3 标准 Checklist 与 Review 要点（Clause 对照）

本步衔接 Stage Gates：任何 P0 issue 未关闭，本步必须把项目回退到对应 Phase 修订，**不可跳级前进**。

### Stage Gates 回退矩阵

| Gate | 进入条件 | 决策者 | P0 出现时回退到 |
|---|---|---|---|
| G-A · Item Definition 冻结 | A1-A3 OK + Confirmation Review（Item Def）通过 | FSM | Phase A（Step 1/2） |
| G-B · Hazard 清单冻结 | B-C 阶段 review 无 P0 | Safety Team Lead | Phase B-C（Step 5 / 9 SEC-HAZ） |
| G-C · ASIL 表冻结 | E 阶段独立重算通过 | FSM + 独立审核员 | Phase E（Step 6/7/9 SEC-SEC） |
| G-D · Safety Goal 冻结 | F 阶段完整性 + Confirmation Review 通过 | FSM + PM | Phase F（Step 9 SEC-SG） |
| G-E · HARA 报告发布 | Phase G/H 全部通过 | FSM + PO + Confirmation Reviewer | Phase G-H（Step 10/11/13） |

### Checklist（修订动作）

- [ ] 每条修订**对应**具体 issue ID（review_findings 或 failures.md）
- [ ] 修订前后 `NEEDS_USER_CONFIRMATION` 数量**不减少**（除非 HITL 已记录确认）
- [ ] 引入的新引用 tier ≠ T4 / T5
- [ ] diff 无新增 `approved` / `validated` / `compliant` 措辞
- [ ] 知识缺口型问题以**登记**代替凭空填值
- [ ] 修订完成后**必须回到 Step 10/11** 重新审查验证
- [ ] 若涉及 Item Definition / Hazard List / ASIL / SG 变更，对应 Gate 视为重新打开，需重新通过

### Review 要点

| 失效 | 级别 |
|---|---|
| 修订移除 pending 标记（无 HITL 记录） | **P0** |
| 用 sample 内容补 hazard 空白 | **P0** |
| 修订后未回到 Step 10/11 重审 | **P0** |
| 跨 Gate 修订未触发上游 Gate 重新打开 | **P0** |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 常见修订诱惑 | 凭空填 [PENDING] | 偷用 sample 数据补 critical claim 空白 |
| 额外约束 | — | 修订涉及 Δ-Analysis 节时，必须重新核对 Δ 条目独立性 |


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA 修订类型与规则

| 修订类型 | 触发条件 | 允许的修订操作 | 禁止的操作 |
|---|---|---|---|
| 批准语义移除 | P0: 出现"ASIL is D"/"approved"/"已确认" | 替换为"ASIL候选值 D [NEEDS_USER_CONFIRMATION]" | 不得顺带改动该行其他字段 |
| Sample 误引清除 | P0: evidence 指向 T4 sample | 将对应 claim 改为 unsupported/NEEDS_USER_CONFIRMATION，记录 gap | 不得用 sample 中的值替补 |
| 缺失节补充 | P1: mandatory section 缺失 | 新增节，内容标 [PENDING] 或填入已有 T1 source 支撑内容 | 不得用 sample 或推断填充节内容 |
| ASIL 逻辑修正 | P1: S/E/C → ASIL 映射错误 | 按 ISO 26262-3 Table 4 重新查表，结果仍标 NEEDS_USER_CONFIRMATION | 不得改动 S/E/C 值来"凑出"期望 ASIL |
| 安全目标覆盖补全 | P1: ASIL>QM 的 HE 无 SG | 新增 SG 行，使用禁止性措辞，标 NEEDS_USER_CONFIRMATION | 不得从 sample 借用安全目标措辞 |
| 危害覆盖补充 | P1: 某功能引导词覆盖不足 | 对漏失的引导词方向补充 H-xx，标 NEEDS_USER_CONFIRMATION | 不得在无 T1 source 支撑时声明危害"已识别" |
| 格式/措辞修正 | P2: 表格格式、编号不一致 | 统一格式，修正编号连续性 | 不得通过格式调整改变内容含义 |
| NEEDS_USER_CONFIRMATION 保留 | P0: 标记被移除 | 恢复该标记，记录谁/何时移除了它 | 不得以任何理由永久移除该标记 |

### 修订计划生成格式（revised/revision_plan.md）

```
## HARA Revision Plan

### P0 修订（必须完成，阻断继续）

| 修订ID | 触发问题 | 修订操作 | 目标位置 | 完成状态 |
|---|---|---|---|---|
| REV-001 | VC-3-04: 草稿第89行"ASIL D（已批准）" | 替换为"ASIL候选值D [NEEDS_USER_CONFIRMATION]" | draft/hara_draft.md:89 | □ |
| REV-002 | VC-2-01: H-01 source 指向 sample_hara.pdf | 移除 sample 引用，标 unsupported，记录 gap | claim_support_matrix.json:H-01 | □ |

### P1 修订（须完成）

| 修订ID | 触发问题 | 修订操作 | 目标位置 | 完成状态 |
|---|---|---|---|---|
| REV-003 | VC-4-01: HE-005 ASIL应为A而非B | 按 S2+E3+C2 重新查表 → ASIL候选值A [NEEDS_USER_CONFIRMATION] | draft/hara_draft.md:SEC-SEC | □ |
```

### 修订约束（强制）

1. **每条修订对应一个问题 ID**（来自 review_findings 或 verify/failures）
2. **修订后 NEEDS_USER_CONFIRMATION 数量不减少**（若增加说明修订后又发现新 pending 项，应记录）
3. **不引入无来源支撑的新 hazard/rating/ASIL/safety goal**：若修订需要新内容，应标 `[PENDING - 需 HITL 补充]`
4. **change_log.md 必须与 revision_plan 一一对应**：每个 REV-xxx 有对应完成记录
5. **修订完成后重跑 REQUIRED_CHECKS**：验证 P0 失败项已清除（结果记入 revised/reverify_summary.md）

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按修订条目逐条核对。
- 方案C 先扫高风险约束（HARA HITL pending 是否被自动改为 confirmed、是否引入未支撑新 HARA 结论）再补其余。

### 典型审核子任务
1. 核对修订是否严格依据审查/验证结果，未引入未支撑的新 HARA 结论（hazard/rating/ASIL/safety goal）。
2. 核对无法解决的 HARA 开放项是否保留为 open items（保持 pending）。
3. 核对 HITL pending 是否未被自动改为 confirmed。
4. 核对 revision_plan/revised_draft/change_log 是否符合 artifact 契约。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 一任务一修订条目顺序处理。
- 方案B 先处理阻断类（blocking_failures，如 ASIL 无 T0/T1 支撑）再处理一般审查项。
- 方案C 按 HARA 章节聚合修订条目处理（hazard → S-E-C → ASIL → safety goal）。

### 典型修订子任务
1. 汇总 review_report.items 与 verify blocking_failures 建立 HARA 修订任务（RT）。
2. 逐条修订草稿，只依据允许证据（T0/T1），不引入无支撑的 hazard/rating/ASIL/safety goal。
3. 记录 `revised/change_log.md`，逐条对应修订前后变化与依据。
4. 保留 open items 与 HARA HITL pending 状态。

## state.json 示例（HARA）

```json
{
  "step": "revision",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对修订严格依据审查/验证结果，未引入未支撑 HARA 结论", "status": "done"},
      {"id": "rv-2", "desc": "核对 HARA 开放项保留 pending、HITL pending 未被自动 confirmed", "status": "running"},
      {"id": "rv-3", "desc": "核对 revision_plan/revised_draft/change_log 符合 artifact 契约", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "汇总 review_report.items 与 blocking_failures 建 HARA RT", "status": "done"},
      {"id": "rt-2", "desc": "逐条修订草稿（只依据 T0/T1，不引入无支撑 HARA 结论）", "status": "running"},
      {"id": "rt-3", "desc": "记录 change_log（逐条对应修订依据）", "status": "not_run"},
      {"id": "rt-4", "desc": "保留 HARA open items 与 HITL pending 状态", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：修订是否严格依据审查/验证结果、未引入未支撑的新 HARA 结论（hazard/S-E-C/ASIL/safety goal）；无法解决的 HARA 开放项是否保留为 open items（保持 pending）；HARA HITL pending 是否未被自动改为 confirmed；`revised/change_log.md` 是否逐条记录修订依据；sample/reference 是否未被误当作事实证据。
