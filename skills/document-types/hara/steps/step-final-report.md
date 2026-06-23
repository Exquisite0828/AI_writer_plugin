# HARA 子 skill · Step 13 · 最终报告 (Final Report)

本文件是通用骨架 `skills/workflow-steps/step-final-report/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 把修订后 HARA 草稿、审查、验证与溯源汇编为最终交付包，供合格人工审查。
- 状态保守：`finalized_with_open_items` / `ready_for_human_review` / `blocked_pending_confirmation`；未解决 HARA 条目保持 open。
- HARA critical claim（hazard/S-E-C/ASIL/safety goal/final acceptability）与 open items 保持 pending，禁止输出最终批准类结论。
- final report 是 review-ready artifact，不替代合格人工审查或专业 HARA sign-off。
- 明确标注：本报告不等于 HARA 专业批准或合规认证。

## HARA 报告过程总览（本步定位）

HARA 报告完成时只能使用**保守状态声明**，不输出「合规 / 批准」语义。本步打包最终交付物。

**HARA 允许的最终状态**：

| 状态 | 适用条件 |
|---|---|
| `ready_for_human_review` | 无 P0 问题，产物齐全，开放项已汇总 |
| `finalized_with_open_items` | P0 全部清除，仍有 `NEEDS_USER_CONFIRMATION` 项 |
| `blocked_pending_confirmation` | 存在未修复阻断性问题 |

**严格禁止的状态 / 措辞**：`approved` / `validated` / `compliant` / `HARA 已完成` / `ASIL D（已批准）`

**本步定位**：组装 `final_report.md` + `open_items_registry` + `evidence_traceability` + 免责声明，**不替工程师宣告合规**。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`final_report.md`、`open_items_registry.json`、`evidence_traceability.json`、免责声明）是交付给人工审查的最终包。subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-5-01 | 无专业批准措辞 | 全文 grep 无 `approved` / `validated` / `compliant` / `HARA 完成` / `ASIL D（已批准）` |
| 元交付 | document_status 取保守值 | status ∈ `ready_for_human_review` / `finalized_with_open_items` / `blocked_pending_confirmation` |
| 元交付 | open_items_registry 汇总完整 | 注册项数 ≥ 草稿中 `NEEDS_USER_CONFIRMATION` 数 |
| 元交付 | evidence_traceability 可回溯 | claim → EVD → file_id + L1/L2/L3 + location |
| 元交付 | 免责声明强制文本就位 | 含「本报告不等于 HARA 专业批准或 ISO 26262 合规认证」 |
| VC-3-04 | ASIL 仅为候选 | 全文无 `ASIL is D` / `ASIL D（已批准）` 等最终断言 |

**自检底线**：final report 是 review-ready artifact，不替代合格人工审查或 HARA 专业 sign-off；任何批准语义出现即 P0 阻断打包。



## ISO 26262-3 标准 Checklist 与 Review 要点（Clause 对照）

本步对应 Phase H1（Documentation Completeness）+ Phase H2（Sign-off）+ Stage Gate G-E（HARA 报告发布）。

### H1 · 最终报告强制内容 Checklist

最终 HARA 报告必须含以下章节（任一缺失即 **P0**）：

- [ ] 文档信息（标题 / 版本 / 日期 / 作者 / 修订历史 / 状态）
- [ ] 范围与适用标准（含 ISO 26262-3:2018 版本声明）
- [ ] 参考文档与术语
- [ ] Item Definition 摘要
- [ ] 运行工况与模式
- [ ] 危害识别（H-xx 表）
- [ ] 危害事件（HE-xxx 表）
- [ ] S/E/C 评级表
- [ ] ASIL 候选表
- [ ] 安全目标（SG-xx 表，含 **Safe State / FTTI**）
- [ ] 开放问题（Open Issues）
- [ ] 验证记录
- [ ] **Confirmation Review 记录占位**（ASIL ≥ B 强制）
- [ ] **追溯矩阵**（F → H → HE → S/E/C → ASIL → SG，双向可追溯）
- [ ] 签字栏占位（作者 / 评审人 / Confirmation Reviewer / FSM / PM）
- [ ] With-Reference 情景：**Differences from Reference HARA** 节

### 交付包（5 件）

- [ ] `final_report.md`（或对应导出格式）
- [ ] `open_items_registry.json`
- [ ] `evidence_traceability.json`
- [ ] `disclaimer`（含强制文本，见下）
- [ ] `run_summary`

### 强制免责声明文本（必须含）

> 「本报告由 AI 辅助工具生成，是供具备资质工程师审查的准备材料。不等于 ISO 26262 合规认证，不等于 HARA 专业批准，不等于 Confirmation Review。所有 critical claim 在签字前保持 pending。」

### document_status 取值规则

仅允许：
- `ready_for_human_review`（无 P0、产物齐全、开放项已汇总）
- `finalized_with_open_items`（P0 全部清除、仍有待确认项）
- `blocked_pending_confirmation`（存在未修复的阻断性问题）

**严格禁止**：`approved` / `validated` / `compliant` / `HARA 已完成` / `ASIL D（已批准）`

### H2 · 签字 Checklist

- [ ] 作者签字位
- [ ] 评审人签字位
- [ ] **Confirmation Reviewer 签字位**（ASIL ≥ B 强制）
- [ ] Functional Safety Manager 签字位
- [ ] 项目经理 / 产品负责人签字位
- [ ] 文档进入受控状态字段（PLM / CMS 入库标记）

### Review 要点

| 失效 | 级别 |
|---|---|
| 任一强制章节缺失 | **P0** |
| `document_status` 取 `approved` / `validated` / `compliant` | **P0** |
| 缺免责声明 | **P0** |
| 追溯矩阵不可双向追溯 | **P1** |
| 任一必要签字位缺失 | **P0** |
| With-Reference 情景缺 "Differences from Reference HARA" | **P0** |
| 全文 grep 命中 `approved` / `validated` / `compliant` / `HARA 完成` | **P0** |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 额外章节 | — | "Differences from Reference HARA" 必备节 |
| 额外签字考量 | — | Δ-Analysis 节单独列出审核责任人 |


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA 最终交付包结构

最终报告包含以下文件，均位于 `runs/<run_id>/final/`：

| 文件 | 内容 | 状态字段 |
|---|---|---|
| `hara_report.md` | 修订后完整 HARA 报告正文（12 节结构） | 见下 |
| `open_items_registry.md` | 所有 NEEDS_USER_CONFIRMATION 条目汇总，含类别/影响/等待什么 | 随报告交付 |
| `evidence_traceability.md` | claim → EVD → file_id + L1/L2/L3 + location | 随报告交付 |
| `review_verification_summary.md` | 审查（Step 10）+ 验证（Step 11）+ 修订（Step 12）的摘要与状态 | 随报告交付 |
| `delivery_note.md` | 交付说明：本报告限制、未解决项数量、建议下一步 | 随报告交付 |

### hara_report.md 状态声明规则

最终报告首页**必须**包含以下免责声明块（逐字保留，不得删减）：

```
## 重要声明

本报告由 AI Writing Agent 辅助生成，基于所提供的输入材料（见参考文件节）进行分析。

**本报告不等于 HARA 专业批准或 ISO 26262 合规认证。**

- 所有危害（H-xx）、危害事件（HE-xxx）、S/E/C 评级、ASIL 候选值及安全目标均为候选结果，
  标注 [NEEDS_USER_CONFIRMATION]，须经具备资质的功能安全工程师审查确认方可使用。
- 本报告中未解决的开放项数量见 open_items_registry.md。
- 分析结果的质量取决于输入材料的完整性；已识别的知识缺口见 knowledge_gaps.md。

报告状态：[见下方 document_status 字段]
```

### document_status 字段取值规则

| 状态值 | 适用条件 |
|---|---|
| `ready_for_human_review` | 无 P0 验证失败，所有 mandatory section 存在，open items 已汇总 |
| `finalized_with_open_items` | P0 全部清除，但仍有 P1/P2 问题或 NEEDS_USER_CONFIRMATION 项 |
| `blocked_pending_confirmation` | 存在未修复的 P0 验证失败（review 或 verify 阻断项未完成） |

**禁止使用的状态值**：`approved` / `validated` / `compliant` / `completed` / `HARA已完成`

### open_items_registry.md 格式

```
## Open Items Registry（HARA 开放项汇总）

| OI-ID | 类别 | 相关 ID | 描述 | 等待什么 | 优先级 |
|---|---|---|---|---|---|
| OI-001 | 危害确认 | H-01, H-02 | 危害识别候选结果待功能安全工程师审查 | 功能安全工程师 HITL 确认 | P0 |
| OI-002 | S/E/C 评级 | HE-001 ~ HE-004 | 所有 S/E/C 候选值及 ASIL 候选值待确认 | 功能安全工程师基于项目实际工况确认 | P0 |
| OI-003 | 知识缺口 | OS-02 工况描述 | T1 source 中未提供城市工况的具体车速分布数据 | 项目组补充 operational situations source | P1 |
| OI-004 | 安全目标 | SG-01 ~ SG-02 | 安全目标措辞与 ASIL 候选值待工程师确认 | 功能安全工程师确认措辞与 ASIL 等级 | P0 |
```

### evidence_traceability.md 格式

```
## Evidence Traceability Matrix

| Claim ID | Claim 类型 | Evidence EVD-xxx | Source · L1/L2/L3 · location | tier | 状态 |
|---|---|---|---|---|---|
| H-01 | hazard | EVD-012 | item_definition.docx · 系统概述 / 3.2 功能 / F-01 段落 · §3.2 L45–78 | T1 | needs_confirmation |
| HE-001.E | exposure | EVD-021 | operational_situations.xlsx · 工况 / OS-01 / 城市工况 · OS-01 行 | T1 | needs_confirmation |
```

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按 HARA artifact/章节逐项核对。
- 方案C 先扫高风险约束（是否被误写为 HARA 批准、critical claim/open items 是否保持 pending）再补其余。

### 典型审核子任务
1. 核对最终报告是否未被误写为 HARA 批准（不得出现 `approved`/`validated`/`compliant` 等批准措辞）。
2. 核对状态是否保守（`finalized_with_open_items` / `ready_for_human_review` / `blocked_pending_confirmation`）。
3. 核对 HARA critical claim 与 open items 是否保持 pending。
4. 核对 final_report/delivery_summary 是否符合 artifact 契约。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 直接由修订稿汇编 HARA 最终报告。
- 方案B 先建交付清单再逐项组装（hazard list / S-E-C table / ASIL summary / safety goals / open items）。
- 方案C 按章节装配 + 全局一致性回扫（检查批准措辞与 pending 状态）。

### 典型修订子任务
1. 汇编 `final/final_report.md` 正文，含 HARA 核心证据边界声明（hazard/S-E-C/ASIL/safety goal 均为 candidate，待合格人工确认）。
2. 生成 `final/delivery_summary.md` 交付摘要（含 HARA open items 清单与各 critical claim 状态）。
3. 汇总 HARA open items 与 critical claims 的 pending 状态。
4. 校验状态保守、未替代 HARA 人工批准、无伪造结论。

## state.json 示例（HARA）

```json
{
  "step": "final-report",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对最终报告未被误写为 HARA 批准", "status": "done"},
      {"id": "rv-2", "desc": "核对状态保守（finalized_with_open_items）", "status": "running"},
      {"id": "rv-3", "desc": "核对 HARA critical claim 与 open items 保持 pending", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "汇编 final_report 正文与 HARA 证据边界声明", "status": "done"},
      {"id": "rt-2", "desc": "生成 delivery_summary（含 HARA open items 与 critical claim 状态）", "status": "running"},
      {"id": "rt-3", "desc": "汇总 HARA open items 与 critical claims pending", "status": "not_run"},
      {"id": "rt-4", "desc": "校验状态保守、未替代 HARA 人工批准", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：最终报告是否被误写为 HARA 批准（不得有 `approved`/`validated`/`compliant`/`risk accepted` 等）；状态是否保守（`finalized_with_open_items` / `ready_for_human_review` / `blocked_pending_confirmation`）；HARA critical claim（hazard/S-E-C/ASIL/safety goal/final acceptability）与 open items 是否保持 pending；是否明确标注本报告不等于专业 HARA 批准或合规认证。
