---
name: step-source-index
description: 中文优先指导 workflow 第 3 步「文档目录索引」：为已解析输入文档建立 L1/L2/L3 导航索引，供后续 Agent 经目录定位后访问原文。
---

# Step 3 · 文档目录索引 (Document Navigation Index)

本步基于 Step 2 的材料清单，为每份 `parse_status=parsed` 的输入文档建立可浏览的 L1→L2→L3 目录与跨文档 topic index。它不写草稿、不做专业判断、不把 sample/reference 升格为项目事实。

## Inputs

- `inputs/input_inventory.json` 是本步读取输入材料的唯一来源。
- 只处理 inventory 中已解析的记录；读取原文必须使用 `files[].path` 中已经解析好的路径。
- 禁止从 cwd、run_dir、manifest、文件名模式或常见目录名反推输入根。路径不可读时写 `knowledge_gaps.md` 并报告路径锚定缺陷，不搜索猜测。

## Method

1. 逐份阅读已解析材料。
2. 按实际标题、编号、表格/附录边界和语义主题划分 L1、L2、L3；不得硬套固定模板。
3. `location` 挂在 L3 叶子节点；若结构不足三级，L2 可作叶子但必须在 gaps 中说明。
4. 为 L3 写 1-2 句 `brief`；brief 只用于筛选，不是 evidence snippet。
5. 建立 `source_index.json.topic_index`：topic/keywords → `file_id + L1/L2/L3 + location`。
6. 为每份文档生成 `knowledge/document_tocs/<file_id>.md`，供后续步骤先读目录再开原文。

## Outputs

- `knowledge/source_index.json`：文档清单与跨文档 topic index。
- `knowledge/provenance_index.json`：每份文档的 L1/L2/L3 树、location、role/tier/is_fact_source 元数据。
- `knowledge/document_tocs/<file_id>.md`：单文档可读目录。
- `knowledge/knowledge_gaps.md`：解析、结构、定位失败或 unsupported/missing 材料。

## Required Fields

`source_index.json.documents[]`: `file_id`, `path`, `role`, `title`, `parse_status`, `toc_ref`, counts, `document_brief`.

`topic_index[]`: `topic_id`, `topic`, `keywords`, `locations[]` with file_id, l1/l2/l3 titles, anchor/line info when available.

`provenance_index.json`: `schema_version`, `run_id`, `task_type`, `documents[]`; each document records `file_id`, `path`, `title`, `role`, `source_tier`, `is_fact_source`, `parse_status`, and `toc`.

L3 leaf fields: `l3_id`, `l3_title`, `brief`, `location` (`section`, `anchor`, page/line/char positions when available; do not invent).

## Boundaries

- Agent access to original input after this step must follow L1→L2→L3→location; no direct full-text blind search.
- Preserve N4 tier metadata: T0 HITL, T1 project source, T2 template/checklist, T3 reference, T4 sample, T5 generated/unknown.
- sample / expected output can be indexed for structure/style only with `is_fact_source=false`.
- missing/unsupported/failed materials cannot be silently treated as indexed.
- Every L3 or L2 leaf must trace to file_id and location; empty provenance is a P1 defect.

## Load Document-Type Overlay

Before execution, load only the current task type overlay:

```text
skills/document-types/<task_type>/steps/step-source-index.md
skills/document-types/<task_type>/SKILL.md
```

If missing, report and stop for confirmation. Do not load sibling document types.

## Subagent Review

Open a fresh review worker after this step. Pass explicit paths: `project_root`, `run_dir`, `input_inventory_path`, `step_output_dir`. Review worker may inspect only the inventory, `source_index.json`, `provenance_index.json`, `document_tocs/`, and `knowledge_gaps.md`; original text may be sampled only through inventory paths.

No P0/P1: write `runs/<run_id>/subagent/step-source-index/state.json` and do not rewrite artifacts. P0/P1: perform local repair tied to issue/artifact; do not regenerate all directories or guess input roots. P2/P3 become user-visible issues, not automatic rewrites.

Review checks: path anchoring, parsed files covered, L1/L2/L3 usefulness, location completeness, topic index consistency, source tier preservation, sample not fact source, no professional judgments.

Next: Step 4 template outline. Step 4 and later must use this index for original input access.
