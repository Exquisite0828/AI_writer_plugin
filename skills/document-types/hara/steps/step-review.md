# HARA 子 skill · Step 10 · 审查 (Review)

通用骨架：`skills/workflow-steps/step-review/SKILL.md`。HARA 根规则：`skills/document-types/hara/SKILL.md`。

## Purpose

对 HARA 草稿做结构化审查并输出 issue，不直接改稿，不给专业批准。问题按 P0/P1/P2/info 分级并定位到章节、行、表格或 claim id；P0/P1 供 Step 12 修订。

## Required Review Dimensions

| Code | Focus | Blocking examples |
|---|---|---|
| RD-1 | 模板完整性 | mandatory sections 缺失、元数据/状态缺失 |
| RD-2 | Item 定义 | 功能、边界、接口、误用缺失；sample 作为 source |
| RD-3 | 危害识别 | 每功能 guide word 覆盖不足；H-xx 描述后果/工况/底层失效；pending 被移除 |
| RD-4 | S/E/C 证据 | HE 无 S/E/C；E 无 T1 工况 source；评级写成已确认 |
| RD-5 | ASIL/SG 一致性 | ASIL 与 S/E/C 不一致；ASIL>QM 无 SG；SG 非禁止性措辞或含批准语义 |
| RD-6 | 开放项 | SEC-OPEN 未覆盖 `NEEDS_USER_CONFIRMATION`、knowledge gap 被掩盖 |

Review findings 自身也要合规：每个维度有 pass/fail/N/A，issue 有 severity，不写 `approved` / `validated` / `compliant` / 审查通过 等批准语义，不建议移除 `NEEDS_USER_CONFIRMATION`。

## Scenario Focus

- From-Scratch：重点查 item 完整性、open/gap 是否诚实。
- With-Reference：重点查 hazard/rating/SG 独立性、sample 相似度、Δ-Analysis 是否具体。

## Severity

- **P0**：批准语义误用、sample 被用作事实 source、critical claim 无 pending/HITL、`NEEDS_USER_CONFIRMATION` 被移除。
- **P1**：mandatory section 缺失、覆盖不足、S/E/C 依据空白、trace 不完整。
- **P2**：编号/表格/措辞一致性问题。
- **info**：非阻断改进建议。

## A1 / A2 / B

**A1**：核对 RD-1~RD-6 覆盖、P0/P1 显式、issue 定位具体、无批准语义、HITL 未确认项可见。
**A2**：仅当 P0/P1 已明确时进入局部修订；不在 review step 直接重写草稿。
**B**：subagent 逐项核对 HARA template/checklist/evidence/final review 关注点：hazard、HE、S/E/C、ASIL、SG、sample/reference 边界。
