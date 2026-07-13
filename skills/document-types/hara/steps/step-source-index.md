# HARA 子 skill · Step 3 · 文档目录索引 (Document Navigation Index)

本文件是通用骨架 `skills/workflow-steps/step-source-index/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用流程、artifact 路径与 **L1→L2→L3→原文** 访问协议以骨架与 `writing-core` 为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 领域补充）

- **逐份阅读**已解析的 HARA 相关输入材料，为每份文档建立 **一级 / 二级 / 三级目录**，像书籍目录一样反映实际结构与语义。
- 为每份文档生成 `knowledge/document_tocs/<file_id>.md`，供 Agent **必须按 L1→L2→L3 顺序**浏览后再打开原文。
- 在 `knowledge/source_index.json` 建立 HARA 主题 `topic_index`，每条指向 `file_id` + L1/L2/L3 + 位置锚点。
- 在 `knowledge/provenance_index.json` 保存 L1→L2→L3 完整树；**`location` 挂在 L3 叶子**（无法分 L3 时在 `knowledge_gaps.md` 说明，L2 作叶子）。
- **底线**：sample=T4 / reference=T3 可建导航目录，但绝不在此步升格为 hazard/S-E-C/ASIL/SG 事实证据。

## HARA 报告过程总览（本步定位）

本步回答「相关内容在哪几份文档、经哪三级目录、在原文哪一段」，为后续步骤提供**唯一合法的原文入口**。

**HARA 本步产出用途**：

- Agent 读材料：**L1 → L2 → L3 → 原文**（可先经 `topic_index` 命中文档与三级路径）
- Item 功能 / 工况 / 接口：从 `topic_index` 命中主题 → 进入对应 `document_tocs` 逐级展开 → 读 L3 原文
- sample HARA：仅结构导航，`source_tier=T4`

**本步定位**：建立可跳转的三级文档地图；**不**生成 SRC chunk 或 hazard 结论。

## 本步将被审查的关键点（Review / Verification 自检清单）

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-1-02 | 导航索引存在 | `source_index.json` 含 `documents` 与 `topic_index` |
| VC-2-04 | 每条 L3 含 location | `provenance_index` 每个 L3（或 gap 下 L2 叶子）有可回溯 `location` |
| 可读目录 | 三级目录 md 一致 | `document_tocs/<file_id>.md` 与 JSON 的 L1/L2/L3 一致 |
| RD-6 | gap 已登记 | 缺功能/边界/工况等在 `knowledge_gaps.md` |
| 根 skill | source ≠ sample | sample 目录 T4，brief 无 hazard/评级事实 |

**自检底线**：后续步骤不得绕过 L1/L2/L3 读原文；任何 L3 不得缺 `location`。

## ISO 26262-3 标准 Checklist 与 Review 要点（Clause 对照）

### Checklist（目录完备性）

- [ ] 每份 parsed 项目 source 均有 L1/L2/L3 树（JSON + `document_tocs`）
- [ ] L3 沿语义边界（功能条目 F-xx、工况 OS-xx、接口 IF-xx、Table 行等）
- [ ] `topic_index` 覆盖 Item 功能、系统边界、工况、接口、安全假设、S/E/C/ASIL 方法学等
- [ ] sample 与项目 source **分文档**索引；sample 强制 T4
- [ ] 无法建立 L3 的分支在 `knowledge_gaps.md` 说明

### Review 要点

| 失效 | 级别 |
|---|---|
| L3 `location` 为空 | **P1** |
| 缺 `document_tocs/<file_id>.md` 或三级结构不一致 | **P1** |
| `topic_index` 缺 HARA 核心主题 | **P1** |
| sample 目录未标 T4 或 brief 含项目事实 | **P0** |

## HARA 文档目录划分指引（L1/L2/L3 语义边界）

| 常见 L1 | 常见 L2 | 常见 L3（叶子示例） | role | tier |
|---|---|---|---|---|
| Item / 系统概述 | 系统边界 / 功能列表 | 每条 F-xx、边界段落 | source | T1 |
| 运行工况 | 工况分类 / OS 表 | 每条 OS-xx | source | T1 |
| 接口与交互 | 接口清单 | 每条 IF-xx | source | T1 |
| 假设与约束 | 安全假设 | 每条假设条目 | source | T1 |
| 标准与方法学 | Table 1/2/3/4 | 每个等级定义行 | reference | T3 |
| HARA 样例 | 章节结构 | 各节表格形状 | sample | T4 |

### topic_index 建议主题（HARA）

系统边界、Item 功能、运行工况、外部接口、安全假设、S/E/C 等级定义、ASIL 方法、HARA 模板章节、检查单要求。

## A1 审核任务（HARA）

### 典型审核子任务

1. 核对 `document_tocs` 与 JSON 的 L1/L2/L3 一致。
2. 核对每个 L3（或 gap 下 L2 叶子）的 `location` 可回溯。
3. 核对 `topic_index` 覆盖 HARA 核心主题。
4. 核对 sample/reference tier 与 `knowledge_gaps.md`。

## A2 修订任务（HARA）

### 典型修订子任务

1. 逐份阅读材料，提取 L1/L2/L3。
2. 为 L3 填写 `brief` 与 `location`。
3. 生成 `document_tocs/<file_id>.md`（三级目录格式）。
4. 写入 `topic_index` 与 `provenance_index`。
5. 登记 `knowledge_gaps.md`。

## B 审核检查项（HARA）

Stage review worker 逐项核对：三级目录完整且 `document_tocs` 与 JSON 一致；L3（或 gap 下 L2 叶子）均有 `location`；`topic_index` 覆盖 HARA 检索主题；sample/reference 仅导航不作事实；缺口已写入 `knowledge_gaps.md`；**未**遗留「可直接全文读输入文件」的旧访问指引。
