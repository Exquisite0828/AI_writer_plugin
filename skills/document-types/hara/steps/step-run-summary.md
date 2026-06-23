# HARA 子 skill · Step 14 · 运行总结 (Run Summary)

本文件是通用骨架 `skills/workflow-steps/step-run-summary/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 重建本次 HARA run 各阶段会话轨迹与 HITL 决策记录，如实描述发生了什么，不重下 HARA 专业结论。
- 抽取 HARA HITL 决策（hazard/S-E-C/ASIL/safety goal 等记录确认点）与 open items。
- 生成中性 run_summary：只描述流程与决策，不把 `completed` 当作 HARA 专业批准，不把未确认的 HITL 写成已确认。
- 提炼 HARA 场景下可复用的流程/结构模式（仅记录模式，不掺入 HARA 事实结论）。
- 非交互 run 不伪造 HITL 确认。

## HARA 报告过程总览（本步定位）

`run_summary` 记录本次 HARA 执行过程的事实——材料处理、HITL 决策、开放项统计、状态声明，**不做专业结论的重新判断**。

**HARA run_summary 关注点**：

- 5 大节：输入摘要 / HITL 决策记录 / 知识缺口 / 可复用流程模式 / 状态总结
- 未确认的 critical claim 在 summary 中保持 pending 标记
- 非交互 run 不得伪造 HITL；如有缺失须显式记录「无 HITL」

**本步定位**：为审计与下一次 HARA run 提供可追溯叙事，避免 critical claim 被反复推断。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`run_summary.md`）是本次 HARA run 的中性叙事，subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-5-01 | 不写专业批准语义 | summary 中无 `completed` / `approved` / `compliant` 作为 HARA 专业批准 |
| VC-5-02 | 未确认 critical claim 保持 pending | summary 中提及的 hazard / HE / S/E/C / ASIL / SG 保留 `NEEDS_USER_CONFIRMATION` 状态 |
| 元总结 | 非交互 run 不伪造 HITL | 如无人工决策，显式记录「无 HITL 决策（non-interactive run）」 |
| 元总结 | knowledge_gap 列入总结 | 输入摘要 / 知识缺口节列出本次 run 的所有 gap |
| 元总结 | 可复用模式不含事实 | "可复用流程模式"节仅记录流程 / 结构信号，不含具体 hazard / ASIL 值 |

**自检底线**：summary 只描述流程事实，不做专业结论的重新判断；非交互 run 不得伪造 HITL 确认。



## ISO 26262-3 标准 Checklist 与 Review 要点（Clause 对照）

本步记录本次 run 经过的 Stage Gates、HITL 决策与开放项，作为后续 Confirmation Review 与 PLM 入库的工作记录。

### Checklist（Run Summary 5 节）

- [ ] **输入摘要**：含 role 分类（source/template/checklist/reference/sample 各计数）、缺失材料数、是否含既有 HARA 报告参考
- [ ] **HITL 决策记录**：列出每条 HITL 输入与影响的 critical claim；非交互 run 显式记 "no HITL in this run"
- [ ] **知识缺口**：从 `knowledge_gaps.md` / `unresolved_questions` 汇总，按 Phase 分类
- [ ] **Stage Gate 状态**：本次 run 是否触达 G-A / G-B / G-C / G-D / G-E；尚未通过的 Gate 列出阻断原因
- [ ] **可复用流程模式**：仅记录流程 / 结构信号（如「漏 Unintended 引导词」「FTTI 缺失高发」），**不**记录具体 hazard / ASIL / SG 数值
- [ ] **状态总结**：保守 document_status（仅 `ready_for_human_review` / `finalized_with_open_items` / `blocked_pending_confirmation`）

### Review 要点

| 失效 | 级别 |
|---|---|
| summary 写 `completed` / `approved` 作为专业批准 | **P0** |
| 未确认 critical claim 在 summary 中被标 confirmed | **P0** |
| HITL 决策伪造（无对应记录却声称已确认） | **P0** |
| Stage Gate 状态写「通过」但 P0 未关闭 | **P0** |
| 流程模式条目含具体 hazard / ASIL / SG 数值 | **P0**（事实泄露） |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 输入摘要 | 标 "no reference HARA" | 标 sample 文件数；列出 Δ-Analysis 节是否完成 |
| 状态总结 | 同 | 必须显示 Δ-Analysis 节是否已通过内审 |


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA Run Summary 应记录的核心内容

run_summary 是本次 HARA run 的可追溯记录，**只描述发生了什么，不重下任何 HARA 专业结论**。

#### 1. 输入材料摘要

```
## 输入材料摘要

| 材料类型 | 文件数 | tier | 覆盖情况 |
|---|---|---|---|
| Item Definition | 1 | T1 | 完整：含功能/边界/接口/约束 |
| Operational Situations | 1 | T1 | 覆盖 4 个工况（高速/城市/停车场/恶劣天气）|
| HARA Template | 1 | T2 | 提供 12 节结构和表格格式 |
| ISO 26262-3 参考 | 1 | T3 | 提供 S/E/C 定义与 ASIL 矩阵 |
| Sample HARA | 1 | T4 | 仅用于格式参考，未用作事实来源 |
```

#### 2. HITL 决策记录

```
## HITL 决策记录（本次 run）

| 决策点 | 相关 ID | 决策类型 | 状态 | 记录时间 |
|---|---|---|---|---|
| 功能 F-03 是否在 item 范围内 | F-03 | item_boundary | 待确认（knowledge_gap） | - |
| 危害 H-01 ~ H-05 识别结果 | H-01 ~ H-05 | hazard_identification | 待功能安全工程师确认 | - |
| HE-001 的 S3+E4+C3 → ASIL D | HE-001 | severity/exposure/controllability/asil | 待功能安全工程师确认 | - |
| SG-01 措辞与 ASIL D 适用性 | SG-01 | safety_goal | 待功能安全工程师确认 | - |
```

**规则**：非交互 run 中，上表所有状态均为"待确认"——禁止将任何项写成"已确认"或"工程师同意"。

#### 3. 知识缺口摘要

```
## 知识缺口摘要

| Gap ID | 受影响的分析 | 缺口描述 | 建议补充内容 |
|---|---|---|---|
| KG-001 | OS-02 工况 E 评级 | 城市工况无 T1 source 车速分布数据 | 项目组提供 operational situations 补充文件 |
| KG-002 | F-03 功能边界 | F-03 是否属于 item 范围无 T1 source 说明 | 项目组确认 item definition §2.3 |
```

#### 4. 可复用流程模式（仅结构信号，不含 HARA 事实）

```
## 可复用 HARA 流程模式

以下模式适用于同类汽车功能安全 HARA 场景，与具体危害/评级/结论无关：

1. **引导词分析覆盖**：对每个功能应用 6 种 GUIDEWORD（No/More/Less/Wrong Direction/Unintended/Timing），
   确保危害识别完整性
2. **工况 × 危害交叉矩阵**：不必列出所有 H×OS 组合，只列成立的危害事件，不成立的注明原因后省略
3. **NEEDS_USER_CONFIRMATION 传播规则**：从 hazard → HE → S/E/C → ASIL → SG 依次传播，无例外
4. **分段知识缺口记录**：在 source index 阶段即识别 gap，避免草稿阶段静默推断填充
```

#### 5. Run 状态总结

```
## Run 状态

- 草稿状态：finalized_with_open_items / ready_for_human_review / blocked_pending_confirmation（选填实际值）
- P0 验证失败：X 条（已修订完成）/ X 条（未完成，阻断）
- 未解决开放项：X 条（NEEDS_USER_CONFIRMATION）
- 知识缺口：X 条
- 本报告不等于 HARA 专业批准
```

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按 HARA artifact 逐项核对。
- 方案C 先扫高风险约束（是否重下 HARA 专业结论、是否伪造 HITL 确认、是否把 completed 当批准）再补其余。

### 典型审核子任务
1. 核对总结是否只描述发生了什么而未重下 HARA 专业结论（hazard/rating/ASIL/safety goal）。
2. 核对非交互 run 是否未伪造 HARA HITL 确认。
3. 核对 `completed` 是否未被当作 HARA 专业批准。
4. 核对 trace/summary/patterns 是否符合 artifact 契约。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 按 HARA run 各阶段顺序重建轨迹再汇总（ingest → outline → evidence → draft → review → revision → final）。
- 方案B 先抽 HARA HITL 决策与 open items 再生成总结。
- 方案C 按 artifact（session_trace / hitl_decisions / run_summary / reusable_patterns）分组生成。

### 典型修订子任务
1. 重建 HARA run `trace/session_trace.jsonl` 与 `trace/hitl_decisions.jsonl`（记录各阶段 HITL 决策点）。
2. 抽取 HARA HITL 决策（确认了什么/未确认什么）与 open items（哪些 HARA 条目仍 pending）。
3. 生成中性 `learning/run_summary.md`（描述流程，不重下 HARA professional 结论，不把 completed 当批准）。
4. 提炼 HARA 场景可复用模式 `learning/reusable_patterns.md`（流程结构、HITL 节点设计，不含事实结论）。

## state.json 示例（HARA）

```json
{
  "step": "run-summary",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对总结未重下 HARA 专业结论", "status": "done"},
      {"id": "rv-2", "desc": "核对非交互 run 未伪造 HARA HITL 确认", "status": "running"},
      {"id": "rv-3", "desc": "核对 completed 未被当作 HARA 专业批准", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "重建 HARA run session_trace 与 hitl_decisions", "status": "done"},
      {"id": "rt-2", "desc": "抽取 HARA HITL 决策与 open items（仍 pending 的 HARA 条目）", "status": "running"},
      {"id": "rt-3", "desc": "生成中性 run_summary（不重下 HARA 专业结论）", "status": "not_run"},
      {"id": "rt-4", "desc": "提炼 HARA 场景可复用模式（流程结构，不含事实结论）", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：总结是否只描述发生了什么而未重下 HARA 专业结论（hazard/rating/ASIL/safety goal 等）；非交互 run 是否未伪造 HARA HITL 确认；`completed` 是否未被当作 HARA 专业批准或合规认证；`trace/hitl_decisions.jsonl` 是否如实记录了 HARA HITL 决策点；reusable_patterns 是否仅记录流程/结构模式而不掺入 HARA 事实结论。
