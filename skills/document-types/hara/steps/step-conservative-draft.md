# HARA 子 skill · Step 7 · 保守草稿 (Conservative Draft)

通用骨架：`skills/workflow-steps/step-conservative-draft/SKILL.md`。HARA 根规则：`skills/document-types/hara/SKILL.md`。

## Purpose

- 遍历 `section_tasks.json`，按 `outline_final.md` 的 L1/L2 渲染保守 HARA 草稿并汇编 `draft/full_draft.md` / HARA draft。
- 每个 TASK 只能使用其 `allowed_evidence`；证据须经 EVD 回溯 L1→L2→L3→原文。
- HARA critical claim（hazard、hazardous event、S/E/C、ASIL、safety goal、final acceptability）无 T0/T1 支撑时保持 `NEEDS_USER_CONFIRMATION` / pending。
- 保留 source tier、claim status、human confirmation status；sample/reference 不能当事实。
- 不写 `ASIL is approved`、`risk is acceptable`、`the rating is S1` 等 final claims。

## HARA Draft Structure

Draft should cover the HARA core chain:

1. **SEC-ITEM**：item 功能、边界、外部接口、假设与依赖；均来自 T1 source 或 open。
2. **SEC-OPS**：运行工况 OS-xx；速度/频率/环境来自 T1 source，缺失写 `[PENDING]`。
3. **SEC-HAZ**：对每个 F-xx 用 HAZOP guide words 识别 H-xx；H-xx 描述车辆层面危害行为，不写工况、底层失效或事故后果；全部 pending。
4. **SEC-HE**：HE = H-xx × OS-xx；描述「在工况下，危害行为可能导致的车辆/人员层面后果」；不成立组合需可见排除依据。
5. **SEC-SEC**：每个 HE 给出 S0–S3 / E0–E4 / C0–C3 候选和文字依据；ASIL candidate 由 ISO 26262-3 Table 4 查表得出；全部 `NEEDS_USER_CONFIRMATION`。
6. **SEC-SG**：仅 ASIL > QM 的 HE 生成 SG；SG 用禁止性表述「item 不应在…条件下…，以防止…」，不写保证/确保/ensure/guarantee；含 Safe State、FTTI，必要时含 Emergency Operation Interval。
7. **SEC-OPEN**：汇总全部 `NEEDS_USER_CONFIRMATION`、`[PENDING]`、knowledge gaps。

With-Reference 情景必须有 Differences from Reference HARA / Δ-Analysis：只比较结构和差异；sample 的 H-xx、HE、S/E/C、ASIL、SG 不能进入本项目事实。

## Self-Check / Review Focus

- 草稿非空，mandatory HARA sections 存在。
- F-xx、IF-xx、OS-xx、H-xx、HE-xxx、S/E/C、ASIL、SG 均可追溯或 open。
- 每个功能至少覆盖多个 guide words；H-xx 是行为，不是后果。
- E rating 引用 T1 工况 source；S 含伤害类型；C 有驾驶员响应依据。
- ASIL candidate 与 S/E/C 逻辑一致；ASIL>QM 有 SG；ASIL=QM 不生成 SG。
- SG 不越界到 FSC/TSC，不含具体技术方案。
- open 条目数覆盖全部 pending；不移除 `NEEDS_USER_CONFIRMATION`。
- 无专业批准措辞；无 sample 高度雷同或 sample fact transfer。

P0 examples: H-xx 抽象层次错误；HE 后果只考虑本车乘员；ASIL 与 S/E/C 不一致；ASIL>QM 无 SG；FTTI 缺失；sample 文字或数据污染 critical claim；With-Reference 缺 Δ-Analysis。

## A1 / A2 / B

**A1**：核对草稿未超证据范围、critical claims pending、forbidden final claims absent、tier/claim/HITL status preserved。
**A2**：按 section_tasks 和 allowed_evidence 局部修订；证据不足只写 pending/open，不补事实。
**B**：Step 8/9 应能重算 S/E/C→ASIL、追溯 EVD、确认 sample/reference 未作事实。
