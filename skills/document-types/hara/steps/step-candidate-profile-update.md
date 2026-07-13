# HARA 子 skill · Step 13 · 候选 Profile 更新 (Candidate Profile Update)

本文件是通用骨架 `skills/workflow-steps/step-candidate-profile-update/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 契约与角色边界以骨架为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 领域补充）

- 从本次 HARA run 提炼候选 profile 更新与 skill patch 提案，保持 proposed/inactive，不立即修改稳定 profile/skill。
- 候选物仅基于本次 run 的可复用流程/结构信号，不掺入 HARA 事实结论（hazard/rating/ASIL/safety goal）。
- `candidate_skill_patch.md` target 指向 `skills/document-types/hara/SKILL.md`，Status: proposed_only，标注未应用。
- `candidate_profile_update.yaml` 固定：status: proposed / active: false / auto_applied: false / requires_user_approval: true。
- 不实现自动 skill 替换、候选自动提升或 profile 自动学习。

## HARA 报告过程总览（本步定位）

HARA 流程结束后的候选 profile 更新**只基于流程 / 结构信号**，不掺入任何 hazard 或 ASIL 事实结论。

**HARA 候选提炼的允许 / 禁止信号**：

| 类型 | 允许提炼 | 禁止提炼 |
|---|---|---|
| 流程类 | 触发条件、章节顺序、知识缺口模式 | — |
| 结构类 | 模板章节是否需调整、checklist 漏项 | — |
| 事实类 | — | 具体 hazard / HE / S/E/C / ASIL / SG |

**候选物状态固定**：`status: proposed` / `active: false` / `auto_applied: false` / `requires_user_approval: true`

**本步定位**：保持稳定 HARA skill 不被自动覆盖；候选物 inactive 待人工评审。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`candidate_profile_update.yaml`、`candidate_skill_patch.md`）应沿用 Step 9 验证的检查边界。Stage review worker 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-5-03 | candidate 处于 proposed / inactive | yaml 字段：`status: proposed` / `active: false` / `auto_applied: false` / `requires_user_approval: true` |
| 元候选 | 不掺入 HARA 事实结论 | patch / yaml 内容不含具体 hazard / HE / S/E/C / ASIL / SG 值 |
| 元候选 | 仅基于流程 / 结构信号 | 提炼内容限于触发条件、章节顺序、checklist 漏项、知识缺口模式 |
| 元候选 | 不覆盖稳定 skill | patch target 文件存在但 status: proposed_only，未应用 |
| 元候选 | 不实现自动学习 / 提升 | 文件不包含 `auto_promote: true` / `auto_apply: true` 字段 |

**自检底线**：候选物默认 inactive，待人工评审；HARA 稳定 skill 不被自动覆盖。



## ISO 26262-3 标准 Checklist 与 Review 要点（Clause 对照）

本步提炼仅限**流程 / 结构 / 检查清单**信号，**任何**情况下不得把本项目或 sample 的 hazard / 评级 / ASIL / SG 数值写入候选更新——这等同于把事实跨项目泄漏，违反 ISO 26262 项目独立性原则。

### Checklist（候选更新）

- [ ] `candidate_profile_update.yaml` 固定字段：`status: proposed` / `active: false` / `auto_applied: false` / `requires_user_approval: true`
- [ ] `candidate_skill_patch.md` target 指向 HARA skill / 子 skill，含 `Status: proposed_only`
- [ ] 提炼内容**仅**含流程 / 结构信号（触发条件、章节顺序、checklist 漏项、知识缺口模式、引导词覆盖盲区）
- [ ] **不**含具体 hazard / HE / S/E/C / ASIL / SG 数值
- [ ] 无 `auto_promote: true` / `auto_apply: true` 字段
- [ ] With-Reference 情景：Δ-Analysis 的方法学改进可写入；Δ 的具体内容不可写入

### 可 / 不可提炼信号对照

| ✅ 可提炼（流程 / 结构 / 检查清单） | ❌ 不可提炼（事实数据） |
|---|---|
| "HARA 草稿常漏 Unintended 引导词" | "本项目 H-03 是 Unintended Acceleration" |
| "FTTI 字段在 sample 中常缺失，需加 checklist" | "FTTI = 100 ms" |
| "Δ-Analysis 节常见漏项：用户群体差异" | "本项目用户群体年龄 18-35" |
| "TASK-SG 任务模板需含 Safe State 字段" | "SG-02 的 Safe State = degraded mode" |

### Review 要点

| 失效 | 级别 |
|---|---|
| candidate `active: true` 或 `auto_applied: true` | **P0** |
| patch 内含具体 hazard / HE / S/E/C / ASIL / SG 数值 | **P0**（事实跨项目泄漏） |
| 提炼内容把 sample 报告的具体内容当通用规则 | **P0** |
| status 字段为 `accepted` / `merged` 等终态 | **P0** |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 信号类型 | 漏项 / 覆盖盲区 / gap 模式 | 同 + Δ-Analysis 方法学改进（不含 Δ 内容） |


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA 候选提炼规则

候选物只能基于**流程/结构信号**，不能包含任何 HARA 事实结论（危害/评级/ASIL/安全目标）。

#### 可提炼的信号类型

| 信号类型 | 示例 | 是否允许进入候选 |
|---|---|---|
| 流程改进（步骤顺序/覆盖完整性） | "引导词分析应在功能清单完成后启动" | ✅ 允许 |
| 结构改进（表格格式/节标题） | "SEC-OPEN 应在草稿完成时自动汇总 NEEDS_USER_CONFIRMATION 计数" | ✅ 允许 |
| 检查项扩充（验证规则） | "应增加 VC-4-03 检查 QM 事件被误生成 SG" | ✅ 允许 |
| 知识缺口模式（常见缺失） | "汽车电控 HARA 常见缺口：工况频率 T1 数据" | ✅ 允许（记录模式，不含具体值）|
| 具体危害内容 | "H-01 意外施加驱动力" | ❌ 禁止（HARA 事实结论）|
| 具体评级值 | "EPS HARA S=3 for 高速失控" | ❌ 禁止（HARA 事实结论）|
| 具体 ASIL 值 | "转向功能通常为 ASIL D" | ❌ 禁止（HARA 事实结论）|
| 具体安全目标 | "SG-01：不应意外施加驱动力" | ❌ 禁止（HARA 事实结论）|

### candidate_skill_patch.md 格式（HARA 场景）

```
# Candidate Skill Patch（HARA）

Status: proposed_only
Target: skills/document-types/hara/SKILL.md
Applied: false
Source Run: runs/<run_id>/
Auto-applied: false
Requires User Approval: true

## 建议更新项

### PATCH-01: 补充引导词覆盖检查提示
**信号来源**: 本次 run 中发现 F-02 仅分析了 No Function 和 More Function，遗漏 Unintended Function
**建议内容**: 在 step-research-questions.md 中明确注记：每个功能的 Q-HAZ 问题必须覆盖全部 6 种引导词
**风险**: 低（不改动任何评级方法，仅完整性提示）
**状态**: proposed，待用户确认

### PATCH-02: 补充 VC-4-03 到 REQUIRED_CHECKS
**信号来源**: 本次 run 发现 HE-007（ASIL=QM）被错误生成 SG-06
**建议内容**: 在 step-verification.md 的 VC-4 节中新增 VC-4-03 检查项
**风险**: 低（增加确定性检查，不影响已通过的 claims）
**状态**: proposed，待用户确认
```

### candidate_profile_update.yaml 固定格式（不得改动）

```yaml
status: proposed
active: false
auto_applied: false
requires_user_approval: true
source_run: runs/<run_id>/
target_profile: skills/document-types/hara/SKILL.md
notes: |
  候选更新提炼自本次 HARA run 的流程信号，不含任何 HARA 事实结论。
  所有内容须经用户审查后方可应用。
```

### 强制约束

- **status 必须为 `proposed`**，不得写成 `active` / `applied` / `promoted`
- **候选物内容无 HARA 事实**：验证方式——扫描候选物文本，无 H-xx 编号/S3/E4/C3/ASIL D/SG 具体措辞出现
- **不实现**：自动 skill 替换、候选自动提升、profile 自动学习

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对。
- 方案B 按 HARA 候选 artifact 逐项核对。
- 方案C 先扫高风险约束（候选物是否保持 proposed/inactive、是否未自动覆盖稳定 HARA Skill）再补其余。

### 典型审核子任务
1. 核对候选物是否保持 proposed/inactive（status: proposed / active: false / auto_applied: false）。
2. 核对是否未自动覆盖稳定 HARA Skill 文件或自动启用 profile。
3. 核对 `promotion_report.md` 是否未被写成 HARA 批准或合规认证。
4. 核对候选 artifact 是否符合契约、candidate_skill_patch target 是否正确。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 从 run_summary/patterns 逐条提 HARA 候选（仅流程/结构模式）。
- 方案B 按候选类型（HARA 模板改进/规则更新/profile 字段）分组提取。
- 方案C 先比对现有 HARA profile 差异再提增量候选。

### 典型修订子任务
1. 收集本次 HARA run 可复用信号（来自 run_summary/reusable_patterns，排除事实结论）。
2. 逐条生成候选物，固定 proposed/inactive；candidate_skill_patch target 指向 `skills/document-types/hara/SKILL.md`。
3. 标注候选物证据（来自哪次 run、哪个 pattern）与适用范围（仅 HARA task_type）。
4. 校验未自动启用、未覆盖稳定 HARA profile/skill，promotion_report 未被写成批准。

## B 审核检查项（HARA）

Stage review worker 逐项核对：候选物是否保持 proposed/inactive（status: proposed / active: false / auto_applied: false / requires_user_approval: true）；是否未自动覆盖稳定 HARA Skill 文件（`skills/document-types/hara/SKILL.md`）或自动启用 profile；`promotion_report.md` 是否未被写成 HARA 批准或合规认证；candidate_skill_patch target 是否正确指向 HARA；候选内容是否仅来自流程/结构模式而不掺入 HARA 事实结论。
