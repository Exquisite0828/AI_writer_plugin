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

## 当前 worker 与 document-type guidance

当前 step worker 只能通过 StepContextPackage.instruction_refs[] 中的 path/hash 读取已纳入 package 的 instructions。wrapper 与本 canonical workflow Skill 是必需引用；document-type root Skill 与 per-step overlay 都按文件存在性懒加载，未出现时不加入 package。root Skill 存在但 per-step overlay 缺失是合法的 root-only 模式；可选 document-type root Skill 或 overlay 未出现不得判为 `metadata_invalid`。所有实际出现在 `instruction_refs[]` 中的引用都必须通过 path/hash 校验；已包含的引用缺失或 hash 无效时返回 `metadata_invalid` 并停止。不得由 controller 直接加载这些正文，不得读取 sibling document types。

## StepResult 与 stage review交接

当前 step worker 读取允许的refs，生成本步声明的专业artifacts，写入并自行校验StepResult，然后返回并结束。它不得继续派发其他worker，也不得创建独立审核状态或stage gate。

Stage review worker 在本stage所有StepResult完成后由controller统一调度，只接收ReviewContextPackage路径。它按 `steps[]` 顺序沿 `context_package_refs[]` 读取本canonical与当前document-type guidance；overlay存在时叠加其领域检查。

### A1/B 通用审核检查

- 本步声明的必需artifact均存在，StepResult path/hash与最终文件一致。
- 产出满足本canonical的输入、输出、顺序和边界约束。
- sample/reference未被当作项目事实，critical claim缺T0/T1时仍为pending或 `NEEDS_USER_CONFIRMATION`。
- 未生成批准、合规、风险接受或生产就绪结论。
- 当前document-type guidance存在时，其A1/B领域检查全部执行。

### A2 局部修订

Stage review worker只记录问题，不修改专业artifact或StepResult。它必须先汇总写入 `stage_reviews/<stage>/issues.json`，再对该stage一次性调用 `build-stage-review-issues` 与 `validate-stage-review-issues`，由builder原子生成并校验固定路径的index/details。本step存在P0/P1或明确返工项时，其ReviewResult返回 `needs_revision`；P2/P3只进入review/open items。A2由重新派发的原step worker执行，并绑定 `issue_id`、`target_artifact`、`changed_paths`；A2 worker不得自行派发其他step。若目标不是最后一步，controller按自动依赖协议重跑被失效的后续step。

Stage review worker为本step写入并校验一个ReviewResult，不创建第二套持久化编排状态。

## 交接到下一步

进入 **Step 4 · 模板大纲**。Step 4及后续步骤必须通过本步索引定位原始输入。
