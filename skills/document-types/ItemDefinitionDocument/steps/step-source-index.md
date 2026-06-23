# IDD 子 skill · Step 3 · 文档目录索引

骨架：`skills/workflow-steps/step-source-index/SKILL.md`。领域规则：`skills/document-types/ItemDefinitionDocument/SKILL.md`。

## 本步目的要点

- 为每份输入建立 **L1→L2→L3** 语义目录树。
- 产出 `source_index.json`（`topic_index`）、`provenance_index.json`、`document_tocs/<file_id>.md`、`knowledge_gaps.md`。
- `topic_index` 宜覆盖 IDD 主题：**功能**、**边界**、**接口**、**环境**、**工况**、**假设**、**误用**。
- 无结构材料标 gap；禁止 chunk/SRC 旧式索引。

## IDD 方法论（本步定位）

本步对应 **阶段 1：材料消化与索引** 的核心环节——建立后续所有步骤读原文的 **唯一导航入口**。

### 阶段 1 · 材料消化与索引（本步执行）

1. 解析 SyRS、架构、接口规范等，建立 **可检索索引**（按主题：功能、边界、接口、环境、工况、误用）。
2. 从材料中定位 **候选 F-xx、IF-xx、边界条目** 的原文位置（L1→L2→L3），供 Step 5/6 精读。
3. 样例 IDD 只索引 **章节结构**，不将样例中的功能/边界内容编入 `topic_index` 事实条目。

### 读材料顺序（贯穿全程）

```
L1（文档章）→ L2（节）→ L3（段/表/图）→ 原文摘录
```

Step 4 及以后 **必须** 经本步索引导航，不得跳过直接全文搜索后编造位置。

## 本步定位

Step 4 及以后读原文的**唯一导航入口**（L1→L2→L3→原文）。

### IDD 导航主题与 Clause 5 映射

| 主题 | 典型 L1/L2 入口 | Clause 5 |
|---|---|---|
| 功能 F-xx | 需求规格 / 功能章节 | §5.4.2 |
| 系统边界 | 架构 / 范围说明 | §5.4.3 |
| 接口 IF-xx | 接口规范 / 信号矩阵 | §5.4.3 |
| 运行环境 | ODD / 环境章节 | §5.4.4 |
| 运行工况 | 场景 / 模式说明 | HARA 输入上下文 |
| 假设与依赖 | 假设清单 / 约束章 | §5.4.4 |
| 合理可预见误用 | 安全分析输入 / 用户场景 | §5.4.4 b |

### 成功标准（本步视角）

- 每份 **source** 有完整 toc（L1→L2→L3）。
- `topic_index` 七大主题均可导航到至少一个 L3 入口，或显式 gap。
- L3 条目含 **location**（页码/锚点/表号），可供 EVD 引用。

## 本步 Review / Checklist 要点

本步产出支撑 Step 11 **VC-2**（EVD 须含 L1/L2/L3 provenance）及 Step 10 证据匹配审查。

### 与本步相关的 Clause 5 索引检查

- [ ] `topic_index` 七大主题（功能/边界/接口/环境/工况/假设/误用）可导航或已标 gap
- [ ] 接口主题含方向相关 L3 入口，或 gap 已登记
- [ ] 误用主题（§5.4.4 b）有 L3 入口或 gap
- [ ] 每份 source 的 L3 条目含 location（页码/锚点/表号）
- [ ] sample 仅索引章节结构，功能/边界未编入 `topic_index` 事实条目

### 本步 Review 要点

| 维度 | 检查项 | 级别 |
|---|---|---|
| 可追溯性 | L1→L2→L3→location 完整 | P0 |
| 接口方向 | 接口主题可定位方向描述 | P0 |
| 误用可导航 | 误用主题有入口或 gap | P0 |
| 事实来源 | sample 未编入 topic_index 事实 | P0 |
| 语义索引 | 无 chunk/SRC 旧式编号 | P1 |

### 本步自检（交付前）

- [ ] `source_index.json` 与 `document_tocs/` 一致
- [ ] `knowledge_gaps.md` 覆盖无法索引的主题
- [ ] SEC-FUNC/BOUNDARY/IF/ENV/OPS/ASSUMP/MISUSE 均有导航或 gap

## 常见错误（本步重点防）

| 错误 | 后果 | 级别 |
|---|---|---|
| 误用索引将 sample 功能编入 topic_index | 事实来源违规 | P0 |
| 接口主题无方向相关 L3 入口 | 后续 IF-xx 缺方向 | P0 |
| 误用主题完全无索引且无 gap | §5.4.4 b 风险 | P0 |
| 使用 chunk 编号代替语义 L1/L2/L3 | 不可审查、不可追溯 | P1 |

## A1 / A2 / B

**A1**：每份 source 有 toc；L3 含 location；gap 已登记；七大主题可导航或已标 gap。  
**A2**：补建目录、补 topic_index 条目。  
**B**：核对 SEC-FUNC/BOUNDARY/IF/ENV/OPS/ASSUMP/MISUSE 相关主题可导航。
