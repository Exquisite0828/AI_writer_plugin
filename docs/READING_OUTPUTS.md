# Reading Outputs

这份指南说明运行完成后先读哪些文件、每类 artifact 的用途，以及如何理解 pending 状态。

所有路径都位于当前 run directory 下：

```text
runs/<run_id>/
```

## 推荐阅读顺序

1. `runs/<run_id>/final/final_report.md`
2. `runs/<run_id>/final/delivery_summary.md`
3. `runs/<run_id>/review/final_review.md`
4. `runs/<run_id>/verify/verify_report.json`
5. `runs/<run_id>/plans/claim_support_matrix.json`
6. `runs/<run_id>/learning/candidate_profile_update.yaml`

先读 final package，再读 review and verification，再按需查 claim support 和 learning proposal。

## User-Facing 输出

优先给普通使用者阅读：

```text
runs/<run_id>/final/final_report.md
runs/<run_id>/final/delivery_summary.md
runs/<run_id>/review/final_review.md
```

`final_report.md` 是 review-ready package。它用于集中查看 source facts、open confirmations、limitations、review findings 和 verification findings。

`delivery_summary.md` 用于快速了解 run status、主要输出、open items 和 candidate updates 状态。

`final_review.md` 是可读 review 摘要，适合在继续补材料或记录 HITL 前先看。

## Review and Verification

用于判断哪些 claim 被支持、哪些 claim 仍需要确认：

```text
runs/<run_id>/verify/verify_report.json
runs/<run_id>/plans/claim_support_matrix.json
runs/<run_id>/review/review_report.json
```

`verify_report.json` 可能包含 blocked verification、warnings 或 required action。`blocked` 不一定表示 run 失败；它可能表示仍缺少真实项目 `source` 或 HITL。

`claim_support_matrix.json` 用于检查 critical claims 的 evidence status、source support 和 confirmation status。

`review_report.json` 是结构化 review artifact，通常比 `final_review.md` 更适合排查细节。

## Audit/Debug Artifacts

这些文件主要用于审计、排查和维护者检查：

```text
runs/<run_id>/inputs/input_inventory.json
runs/<run_id>/knowledge/source_index.json
runs/<run_id>/knowledge/provenance_index.json
runs/<run_id>/plans/evidence_map.json
runs/<run_id>/plans/citation_plan.json
runs/<run_id>/trace/session_trace.jsonl
runs/<run_id>/trace/hitl_decisions.jsonl
```

如果需要确认某条内容来自哪里，按这个顺序查：

```text
source_index -> provenance_index -> claim_support_matrix -> verify_report -> final_report
```

## Pending 状态不是失败

以下状态可以是正确输出：

- `NEEDS_USER_CONFIRMATION`
- pending claims
- open confirmations
- blocked verification

它们表示系统没有找到足够的项目 `source` 或已记录 HITL 来支持某个 critical claim。不要手工删除这些标记；应补充真实项目材料，或在 workflow 中记录真实人工决定。

## Learning Proposal

Learning artifacts 是 proposal，不会自动覆盖稳定配置：

```text
runs/<run_id>/learning/candidate_profile_update.yaml
runs/<run_id>/learning/candidate_skill_patch.md
runs/<run_id>/learning/promotion_report.md
```

`candidate_profile_update.yaml` 和 candidate skill patch 默认 proposed/inactive。它们不能自动覆盖 stable profile、stable Skill 或 built-in document type rules。

`promotion_report.md` 是工程 gate 信息，不改变专业结论。

## 证据边界

- `source` 可以作为项目事实来源。
- `sample` is not fact source。
- `reference` is not project-specific fact support。
- critical claim 必须有项目 `source` 或 HITL，否则保持 pending / `NEEDS_USER_CONFIRMATION`。
- final report、eval passed、promotion report、candidate update 都不能替代真实人工审查和项目确认。
