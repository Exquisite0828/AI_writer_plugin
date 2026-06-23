# HARA 子 skill · Step 10 · 审查 (Review)

本文件是通用骨架 `skills/workflow-steps/step-review/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 自主重新驱动）

- 对 HARA 草稿做多维度结构化审查：模板符合性、HARA checklist 满足度、证据支撑情况。
- 审查维度覆盖：模板完整性、hazard/S-E-C/ASIL/safety goal 等 critical claim 的证据支撑、sample/reference 误用、HITL 未确认项可见性。
- 问题按 P0/P1/P2/info 分级，阻断类问题（P0/P1）显式标记。
- 审查是机器辅助检查，不等于合格人工审查或专业批准；未确认项保持可见。
- 发现的问题供 Step 12 修订使用，不在此步直接改稿。

## HARA 报告过程总览（本步定位）

HARA 草稿完成后须经多维结构化审查。本步以 6 大维度系统化检视草稿。

**HARA 审查 6 大维度**：

| 维度 | 重点检查 |
|---|---|
| RD-1 模板完整性 | 12 个章节齐全，元数据完整 |
| RD-2 Item 定义完整性 | 功能 ≥1 条，边界声明，接口表填写，无 sample 来源 |
| RD-3 危害识别合理性 | 每功能 ≥2 引导词，H-xx 描述**行为**而非后果，全部标 pending |
| RD-4 S/E/C 评级证据 | 每 HE 有 S/E/C 候选 + 文字依据，E 引用 T1 工况 source |
| RD-5 ASIL 与 SG 一致性 | ASIL 候选与 S×E×C 逻辑一致；ASIL>QM 均有 SG；SG 用禁止性措辞 |
| RD-6 开放项可见性 | SEC-OPEN 汇总全部 NEEDS_USER_CONFIRMATION |

**本步定位**：问题按 P0 / P1 / P2 / info 分级，作为 Step 12 修订输入；本步**不改稿**。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`review/review_findings.md`）本身将在 Step 11 验证中被元检查。subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-1-06 | review 记录存在 | `review/review_findings.md` 存在且非空 |
| 元审查 | 6 大维度（RD-1 ~ RD-6）全部覆盖 | review_findings 中各维度均有结论（pass / fail / N/A）|
| 元审查 | P0 / P1 / P2 / info 分级显式 | 每条 issue 含 severity 字段 |
| 元审查 | 不出现专业批准语义 | review_findings 摘要无「审查通过」「合规」「validated」 |
| 元审查 | HITL 未确认项可见 | review_findings 不建议移除任何 `NEEDS_USER_CONFIRMATION` |
| 元审查 | issue 定位具体 | 每条 issue 含章节 / 行号 / 表格位置 |

**自检底线**：本步只发现问题、不改稿；P0 阻断项必须显式标记，未确认项保持可见，由 Step 12 修订处理。



## ISO 26262-3 标准 Checklist 与 Review 要点（Clause 对照）

本步是 Phase G1（Verification，§6.4.5）+ Phase H1（Documentation Completeness）的内审落点，并为 Phase G2（Confirmation Review，§Part 2 §6.4.7）准备材料。

### G1 · 验证（§6.4.5）Checklist

- [ ] HARA 输出与 Item Definition（Clause 5）一致（无矛盾）
- [ ] HARA 输出与 Functional Safety Concept（Clause 7）接口一致
- [ ] hazard 识别方法的适用性已论证（≥ 2 种方法）
- [ ] S/E/C/ASIL 评级的合理性已论证（每条含文字依据）
- [ ] SG 完备性：每个 ASIL ≥ A 的 HE 有 SG 覆盖
- [ ] 验证方法（Walkthrough / Inspection / Analysis）已记录
- [ ] 验证发现的所有 issue 已闭环或登入开放清单
- [ ] 验证报告非由唯一作者执行（独立性占位）

### 6 维度内审 Checklist 与标准映射

| 维度 | 对应 Clause | 关键 P0 |
|---|---|---|
| RD-1 模板完整性 | §6.4.4 + Part 2 §5.4.2 | 强制章节缺失 |
| RD-2 Item 定义完整性 | §5 | 边界 / 接口 / 误用缺失 |
| RD-3 危害识别合理性 | §6.4.2 | 单一引导词、H-xx 抽象层次错误 |
| RD-4 S/E/C 评级证据 | §6.4.3 + Tables 1/2/3 | E 与 fault rate 混淆、C 用专家假设 |
| RD-5 ASIL 与 SG 一致性 | §6.4.3 Table 4 + §6.4.4 + §7.4 | ASIL ↔ S/E/C 不一致、FTTI 缺失 |
| RD-6 开放项可见性 | 全篇 | NEEDS_USER_CONFIRMATION 被移除 |

### 元审查（review_findings 自身合规）

| 失效 | 级别 |
|---|---|
| review_findings 摘要写「审查通过 / 合规 / validated / approved」 | **P0** |
| 建议移除 `NEEDS_USER_CONFIRMATION` | **P0** |
| 唯一审核员（无独立性占位） | **P0** |
| 任一维度结论缺失 | **P1** |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点 | RD-2（Item 完整性）/ RD-6（开放项） | RD-3 / RD-4 / RD-5（hazard / 评级 / SG 独立性） + Δ-Analysis 节内审 |
| 必加检查 | — | 草稿与 sample 文字相似度检查；Δ-Analysis 节具体差异条目 ≥ 1 |


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA 审查检查维度（review_dimensions）

审查须覆盖以下 6 大维度，每条问题注明维度代码：

#### RD-1 模板完整性
| 检查项 | 通过条件 | 典型 P0 失败示例 |
|---|---|---|
| 所有 mandatory sections 均存在 | SEC-SCOPE/ITEM/OPS/HAZ/HE/SEC/SG/OPEN/REVIEW 均出现 | 缺少 SEC-OPS 或 SEC-OPEN |
| 文档元数据完整 | 标题/版本/日期/作者/状态字段全部填写 | 状态字段为空 |
| 修订历史记录 | 至少1条修订记录 | 无任何修订记录 |

#### RD-2 Item 定义完整性
| 检查项 | 通过条件 | 典型 P1 失败示例 |
|---|---|---|
| 功能清单 ≥ 1 条 | F-xx 至少有1条含描述 | 仅列功能编号无描述 |
| 系统边界已声明 | In scope / Out of scope 均有内容 | 边界表为空 |
| 接口表已填写 | IF-xx 至少1条，含信号方向 | 接口表完全缺失 |
| 无功能描述来自 sample | 每条 F-xx 来源字段是 T1 source | F-xx 来源指向 sample_hara |

#### RD-3 危害识别合理性
| 检查项 | 通过条件 | 典型 P0 失败示例 |
|---|---|---|
| 每个功能至少覆盖 ≥ 2 种失效类型 | H-xx 中对每 F-xx 可见 ≥ 2 种引导词 | 某功能只有 No Function，未考虑 Unintended |
| 危害描述描述行为而非后果 | H-xx 描述失效行为（如"意外施加制动力"），不含工况 | H-xx 描述"在高速下撞车" |
| 每条危害有 NEEDS_USER_CONFIRMATION | 所有 H-xx 状态列含此标记 | 某危害状态为"已确认" |
| 无来自 sample 的危害 | H-xx 无 source=sample | source 指向 sample_hara.pdf |

#### RD-4 S/E/C 评级证据
| 检查项 | 通过条件 | 典型 P1 失败示例 |
|---|---|---|
| 每个 HE 均有 S/E/C 候选值 | SEC 表每行均填写 | 有 HE 行 S/E/C 列为空 |
| S 评级有文字依据（含伤害类型） | S 依据摘要不为空 | S=3 但依据列为"—" |
| E 评级有 T1 source 对应工况 | E 依据引用 OS-xx | E=4 但工况引用为 sample |
| 所有评级均标 NEEDS_USER_CONFIRMATION | 状态列无"已确认"/"final"措辞 | 出现"S3（已批准）" |

#### RD-5 ASIL 与安全目标一致性
| 检查项 | 通过条件 | 典型 P0 失败示例 |
|---|---|---|
| ASIL 候选值由 S/E/C 候选值经 Table 4 计算得出 | ASIL 列与 S/E/C 列逻辑一致 | S3+E4+C3=D，但写了 C |
| ASIL > QM 的 HE 均有对应 SG | SG 表行数 ≥ ASIL>QM 的 HE 数 | HE-003 ASIL=C 但无 SG |
| SG 措辞使用禁止性表述 | 不含"应保证"/"保证安全"/"确保" | SG 写"保证制动功能正常工作" |
| SG 无 "ASIL is D"/"approved" 措辞 | 状态列不含批准词 | 状态写"ASIL D（已批准）" |

#### RD-6 开放项与可见性
| 检查项 | 通过条件 | 典型 P1 失败示例 |
|---|---|---|
| SEC-OPEN 汇总了所有 NEEDS_USER_CONFIRMATION | OPEN 条目数 ≥ 草稿中 NEEDS_USER_CONFIRMATION 数 | OPEN 节为空但草稿有未确认项 |
| knowledge_gap 已记录 | 缺失 source 有对应 gap 条目 | 无 T1 工况 source 但未记录 gap |
| 审查结论不使用批准措辞 | 不出现"审查通过"/"合规"/"validated" | 审查摘要写"HARA审查通过" |

### 问题严重性分级

| 级别 | 适用情形 | 处理要求 |
|---|---|---|
| P0 | 批准语义误用、sample 被用作事实 source、critical claim 无标记、NEEDS_USER_CONFIRMATION 被移除 | 立即标记，必须由 Step 12 修订后才可继续 |
| P1 | mandatory section 缺失、功能/危害/工况覆盖不足、S/E/C 依据空白 | 须修订，不阻断后续但需在 OPEN 中记录 |
| P2 | 表格格式不一致、编号不连续、措辞不统一 | 建议修订，不强制 |
| info | 可能提升质量的建议（非问题） | 记录供参考 |

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按 HARA artifact/章节逐项核对。
- 方案C 先扫高风险约束（批准语义、sample 误用、HITL 未确认项可见）再补其余。

### 典型审核子任务
1. 核对是否覆盖 HARA template/checklist/evidence/final 关注点。
2. 核对问题是否具体且 P0/P1 显式（定位、严重度、是否阻断）。
3. 核对是否未出现批准语义（HARA professional approval 等）。
4. 核对 HARA HITL 未确认项（`NEEDS_USER_CONFIRMATION`）是否仍可见。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 按审查维度（溯源/一致性/越权结论）逐维扫描。
- 方案B 按 HARA 章节逐节多维审查（hazard identification → hazardous event → S/E/C → ASIL → safety goal）。
- 方案C 维度×章节矩阵抽查高风险项（critical claim 支撑与 sample 误用）。

### 典型修订子任务
1. 枚举 HARA 审查维度（template/checklist/evidence/final）与章节。
2. 逐项扫描并登记 issue（定位、severity/category，含 HARA 专属：hazard 溯源、S-E-C 支撑、ASIL 合理性）。
3. 标注 P0/P1 阻断项（如 ASIL 无 T0/T1 支撑、safety goal 缺失确认）。
4. 汇总 review_report 并校验无漏检、无专业批准语义。

## state.json 示例（HARA）

```json
{
  "step": "review",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对覆盖 HARA template/checklist/evidence/final", "status": "done"},
      {"id": "rv-2", "desc": "核对问题具体且 P0/P1 显式", "status": "running"},
      {"id": "rv-3", "desc": "核对未出现 HARA 批准语义、HITL 未确认项可见", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "枚举 HARA 审查维度与章节", "status": "done"},
      {"id": "rt-2", "desc": "逐项扫描并登记 issue（含 HARA 专属：hazard/S-E-C/ASIL 支撑）", "status": "running"},
      {"id": "rt-3", "desc": "标注 P0/P1 阻断项（ASIL 无 T0/T1 等）", "status": "not_run"},
      {"id": "rt-4", "desc": "汇总 review_report 并校验无漏检", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：是否覆盖 HARA template/checklist/evidence/final review 关注点（hazard identification、hazardous event、S/E/C、ASIL、safety goal）；问题是否具体且 P0/P1 显式；是否出现 HARA 专业批准语义；`NEEDS_USER_CONFIRMATION` 等未确认项是否仍可见；sample/reference 是否被误当作 HARA 事实证据。
