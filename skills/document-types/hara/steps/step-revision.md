# HARA 子 skill · Step 10 · 修订 (Revision)

通用骨架：`skills/workflow-steps/step-revision/SKILL.md`。HARA 根规则：`skills/document-types/hara/SKILL.md`。

## Purpose

依据 Step 8/9 的明确 issue 生成定向修订计划并局部修订草稿。修订不得引入未支撑 HARA 新结论，不得把 HITL pending 改为 confirmed，不得输出批准类措辞。变更记录写入 `revised/change_log.md`，并在修订后回到 Step 8/9 重审验证。

## Revision Rules

- 每条修订绑定 review_findings 或 failures.md 的 issue ID。
- `NEEDS_USER_CONFIRMATION` 数量不得减少，除非已有真实 HITL 记录。
- 新证据 tier 不能是 T4/T5；sample/reference 不能补 hazard、rating、ASIL、SG 空白。
- 知识缺口型问题只登记 gap/open，不凭空填值。
- 修订后无新增 `approved` / `validated` / `compliant` / risk accepted 等措辞。
- 若修订影响 Item/Hazard/ASIL/SG，对应 gate 视为重新打开。

## Allowed / Forbidden Examples

| Trigger | Allowed | Forbidden |
|---|---|---|
| 批准语义 | 改为 candidate + `NEEDS_USER_CONFIRMATION` | 顺带改变 S/E/C 或 ASIL 内容 |
| sample evidence | 移除 sample 支撑，改 unsupported/open | 用 sample 值替补 |
| missing section | 新增节，填 T1 支撑内容或 `[PENDING]` | 用推断或 sample 填满 |
| ASIL mismatch | 按 Table 4 重算 ASIL candidate，pending | 改 S/E/C 来凑目标 |
| SG missing | 为 ASIL>QM HE 新增禁止性 SG，pending | 借用 sample SG 文案 |

## Outputs

- `revised/revision_plan.md`：P0/P1/P2 修订项、目标位置、完成状态。
- revised draft artifacts：只改受影响内容。
- `revised/change_log.md`：每个 REV-xxx 的变更前后、依据、affected paths。
- `revised/reverify_summary.md`：重跑 review/verification 的结果摘要。

## A1 / A2 / B

**A1**：核对修订严格依据 issue，未引入无支撑 hazard/S-E-C/ASIL/SG，open items 保持 pending，change_log 完整。
**A2**：先处理 P0，再 P1；每个修订只读取最小必要 artifact/source 片段。
**B**：Stage review worker 核对修订后 pending/HITL、source tier、sample/reference 边界和重审要求未被破坏。
