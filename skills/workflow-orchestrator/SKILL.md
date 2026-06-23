---
name: workflow-orchestrator
description: 中文优先总控 skill，按顺序编排 workflow 的 15 个 step skills。每个 step 执行完毕后，由 step skill 的 subagent 产出 stage-review 材料并弹出供用户确认的问题列表；必须用户审核通过（在 stage_reviews/<stage>/decision.json 落 accepted）才能进入下一步。不自动批准、不伪造 HITL。
---

# Workflow Orchestrator Skill

总控 skill：按固定顺序驱动 `skills/workflow-steps/` 下的 15 个 step skills，并在**每一步执行完毕后弹出供用户确认的问题列表**，由用户审核该步产出后才允许进入下一步。

本 skill 是编排指导层，不直接写最终文档。各 step 的 artifacts 由对应 step skill 的 subagent **提取该步目的、自主驱动**产出（须符合 artifact 契约）；stage-review 闸门通过 subagent 写入 `runs/<run_id>/stage_reviews/<stage>/decision.json` 记录，不自动批准、不伪造 HITL。

## 何时使用

- 用户希望「一步一步、每步人工确认」地走完整条专业文档写作流程。
- 需要在每个步骤产出后做人工审核，未通过不得继续。
- 作为 `/ai-writing-plugin:write` 命令「交互 workflow」的编排层：command 确认 task 后把控制权交给本 skill，由本 skill 逐 stage 驱动 `skills/workflow-steps/` 下的 15 个 step skill（每步先子代理审核、后用户确认闸门）。

## 核心原则

- **顺序、单向、artifact-first**：每步只消费上游 `runs/<run_id>/` 下的 artifacts。
- **输入文档仅经 L1→L2→L3 访问**：Step 4 及以后读原始输入须遵守 `writing-core` 输入文档访问协议；禁止 chunk/SRC/直接全文盲搜。
- **每步先子代理审核、再人工确认**：每个 step 执行后先由独立 subagent 自主审核并修订（见各 step skill 的「子代理审核」小节），通过后才向用户弹出确认问题列表。确认问题列表来自该 step 的 subagent 产出（`stage_reviews/<stage>/review_prompt.md` + `review_units.json` + `issues.json`），不是凭空生成。
- **子代理审核双轨 + 进度跟踪**：subagent 对「审核任务」与「修订任务」分别自主分解（各 ≥2 方案择优），在 `runs/<run_id>/subagent/<step>/state.json` 以 `review_state` / `revision_state` 两组任务、三态字段（`not_run` / `running` / `done`）各自跟踪进度；全部子任务 `done` 且无 P0/P1 才算本步审核结束。
- **修订靠提取目的、重新驱动**：发现问题时先提取该步脚本的执行目的，再由 subagent 围绕目的重新驱动完成任务，必要时为当前任务重新生成更适用的新脚本，产出仍须符合 artifact 契约与边界。
- **真实闸门**：用户「审核通过」必须落地为 `runs/<run_id>/stage_reviews/<stage>/decision.json`（`decision=accepted`，固定 `decision_scope=stage_review_gate_only`、`professional_approval=false`），否则不得进入下一步。
- **不自动批准**：禁止自动 `accepted`、禁止伪造 HITL、禁止把 sample/reference 当事实、禁止输出专业批准结论；subagent 不得移除 `NEEDS_USER_CONFIRMATION`、不得给出专业批准。
- **15 步 vs 8 个 stage 闸门**：8 个 deterministic stage 处提供真实可记录的闸门；多个 step 共用一个 stage 时，先逐个 step 向用户呈现确认问题，全部确认后再记录该 stage 的单一闸门决定，然后才跑下一 stage。

## Step → stage 映射

stage 是 stage-review 闸门记录的单元；多个 step 共用一个 stage 时共享该 stage 的单一闸门决定。各 step 的产出由对应 step skill 的 subagent **自主驱动**完成。

| Step | stage |
|---|---|
| 1 输入材料 / 2 材料清单 / 3 文档目录索引 | `ingest` |
| 4 模板大纲 | `outline` |
| 5 研究问题 / 6 证据映射 | `evidence` |
| 7 引用计划 / 8 章节任务 | `planning` |
| 9 保守草稿 | `draft` |
| 10 审查 / 11 验证 | `review` |
| 12 修订 / 13 最终报告 | `finalize` |
| 14 运行总结 / 15 候选 profile 更新 | `learning` |

8 个 stage 顺序固定：`ingest → outline → evidence → planning → draft → review → finalize → learning`。

## 编排主循环

对每个 stage（按上表顺序），执行以下闭环：

1. **驱动本 stage 产出（subagent 自主驱动）**：进入本 stage 前先确认上一 stage 的 `runs/<run_id>/stage_reviews/<prev_stage>/decision.json` 存在且 `decision ∈ {accepted, skipped}`（首个 stage `ingest` 无上游闸门）。随后对本 stage 覆盖的每个 step（见上表），由对应 step skill 的 subagent **提取该 step 目的、自主驱动**，在 `runs/<run_id>/` 产出符合 artifact 契约的 artifacts。

2. **逐个 step 的子代理审核与修订（state.json 三态推进）**：对本 stage 覆盖的每个 step，按该 step skill 的「子代理审核」小节新开独立 subagent，自主完成 A1 审核任务与 A2 修订任务的分解与执行，在 `runs/<run_id>/subagent/<step>/state.json` 以 `review_state` / `revision_state` 三态跟踪进度；修订采用「提取脚本目的、重新驱动」，循环直到无 P0/P1 且全部子任务 `done`。subagent 不得伪造 HITL、不得移除 `NEEDS_USER_CONFIRMATION`、不得输出专业批准结论。

3. **逐个 step 说明产出**：参照本 stage 覆盖的 step skill，用中文向用户说明每个 step 产出的 artifact 与边界。

4. **生成 stage-review 包**：由本 stage 末尾的 step skill subagent 写入：

   ```text
   runs/<run_id>/stage_reviews/<stage>/review_prompt.md
   runs/<run_id>/stage_reviews/<stage>/review_units.json
   ```

   `review_units.json` 必须穷举本 stage 内每个 step 的 required units；不允许漏单元。

5. **完成 unit 级审查**：subagent 读取 `review_prompt.md` 与 `review_units.json`，对每个 required unit 逐一审查，写出 `stage_reviews/<stage>/issues.json`，必须包含：

   ```text
   reviewed_unit_ids   # 覆盖全部 required units
   unchecked_unit_ids  # 必须为空
   issues[].unit_id    # 每条 issue 必须挂在已知 unit 上
   coverage_complete   # true 仅当 unchecked_unit_ids 为空且无 reviewed/unchecked overlap
   ```

6. **弹出确认问题列表**：把 `issues.json` 中的 issues（按 step / unit 归类）整理成中文「待用户确认问题列表」呈现给用户，明确标注 P0/P1、`requires_user_review`、`requires_hitl` 项。此列表即用户审核本 stage 产出的依据。

7. **等待用户审核**：用户逐项确认。未获明确「通过」前，**不得**进行第 8 步。

8. **记录闸门决定**：用户回复后，由总控 skill 在以下路径落盘 decision（`decided_by` 写用户标识或 `interactive_user`）：

   ```text
   runs/<run_id>/stage_reviews/<stage>/decision.json
   ```

   schema：

   ```yaml
   stage: <stage>
   decision: accepted | needs_revision | blocked | skipped
   decision_scope: stage_review_gate_only      # 固定值
   professional_approval: false                 # 固定值
   notes: "<用户审核结论原文>"
   decided_by: "<user>"
   decided_at: "<ISO 8601 时间戳>"
   issues_hash: "<issues.json 的 SHA-256，绑定本次决定>"
   ```

   `decision` 取值：`accepted` / `needs_revision` / `blocked` / `skipped`（`skipped` 必须填 `notes`）。只有 `accepted` 或 `skipped` 才允许进入下一 stage。`coverage_complete=false` 不得标 `accepted`。

9. **进入下一 stage**：`decision.json` 落盘且 `decision ∈ {accepted, skipped}` 后，回到第 1 步处理下一个 stage。

## 审核不通过的处理

- 用户发现问题 → 落 `decision=needs_revision`（或 `blocked`），**不要**进入下一 stage。
- 按 issues 修正：交由对应 step 的 subagent 走 A2 修订任务——**提取该步脚本的执行目的、重新驱动**完成修订（不机械重跑原命令；必要时依目的为当前任务重新生成更适用的新脚本），并在 `state.json` 的 `revision_state` 以三态跟踪修订子任务；修订产出仍须符合 artifact 契约与边界、保持可追溯。修订后重新走 `生成 stage-review 包 → 审查 → 用户确认 → 落 decision(accepted)` 闭环。
- 真实人工确认（如 critical claim 的 HITL）由总控 skill 追加写入 `runs/<run_id>/hitl_log.jsonl`；非交互运行不得伪造。

## 边界与约束

- 本 skill 不生成草稿、不做专业判断、不下最终结论；这些由各 step skill 的 subagent 完成。
- `final/final_report.md` 是 review-ready package，不等于专业批准。
- 候选物（`candidate_profile_update.yaml` / `candidate_skill_patch.md`）保持 proposed/inactive，不在编排中自动启用。
- 不引入 RAG / 向量库 / 复杂 agent 框架；不为单一文档类型新建并行 pipeline。
- `runs/<run_id>/` 是本地 runtime 输出，不提交 git。
