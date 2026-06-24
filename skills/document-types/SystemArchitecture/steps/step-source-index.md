# System Architecture 子 skill · Step 3 · 文档目录索引

骨架：`skills/workflow-steps/step-source-index/SKILL.md`。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点

- 为每份输入建立 **L1→L2→L3** 语义目录树。
- `topic_index` 宜覆盖：**上游需求**、**逻辑架构**、**物理架构**、**接口**、**分配**、**诊断/降级**、**资源约束**、**安全引用**。
- 样例架构文档只索引章节结构，不将样例元素/接口编入事实条目。

## System Architecture 方法论（本步定位）

本步对应 **阶段 1：材料消化与索引**——后续读原文的 **唯一导航入口**。

### 阶段 1 · 索引（本步执行）

建立可检索索引，主题覆盖：

| 主题 | 典型入口 | 用途 |
|---|---|---|
| 上游需求 | syrs_source | SEC-REQTRACE、SEC-ALLOC |
| 逻辑架构 | system_context / architecture_source | SEC-LARCH |
| 物理架构 | architecture_source / platform_constraints | SEC-PARCH |
| 接口 | interface_spec / network_topology | SEC-IF |
| 分配 | syrs_source / architecture_source | SEC-ALLOC |
| 诊断/降级 | diagnostic_constraints | SEC-DIAG |
| 资源约束 | platform_constraints | SEC-RES |
| 安全引用 | fsr_or_tsc_excerpt | SEC-SAFE-ARCH |

读材料顺序（贯穿全程）：`L1 → L2 → L3 → 原文摘录`

## 本步 Review / Checklist 要点

### 通用 Checklist

- [ ] 每份 **source** 有 L1→L2→L3 toc，**L3 必须含 `location`**
- [ ] template / checklist / reference / sample 仅作章节结构索引，不进 `topic_index` 事实条目
- [ ] `topic_index` 覆盖 8 主题：上游需求 / 逻辑架构 / 物理架构 / 接口 / 分配 / 诊断 / 资源 / 安全引用
- [ ] 每个 topic 至少 1 个 file_id + L1/L2/L3 命中，或显式登记 gap

### 按章节索引覆盖 Checklist

| 章节 | 主题入口 | 通过条件 |
|---|---|---|
| SEC-REQTRACE | 上游需求 | SyRS requirement 章节可导航 |
| SEC-LARCH | 逻辑架构 | 架构分解章节可导航 |
| SEC-PARCH | 物理架构 | 模块/平台章节可导航 |
| SEC-IF | 接口 | 接口规范与网络拓扑可导航 |
| SEC-ALLOC | 分配 | requirement-allocation 章节可导航 |
| SEC-DIAG | 诊断/降级 | 诊断约束章节可导航 |
| SEC-RES | 资源约束 | 平台/资源章节可导航 |
| SEC-SAFE-ARCH | 安全引用 | FSR/TSC 摘要章节可导航或 gap |

### From-Scratch 专属 Checklist

- [ ] SyRS 主题无索引且无 gap → **P0**
- [ ] 接口 / 分配 / 资源主题缺索引则必须 gap

### With-Reference 专属 Checklist

- [ ] 参考架构文档仅建 `document_tocs/<ref_file_id>.md`，**禁止**编入 `topic_index` 作事实条目（**P0**）
- [ ] 参考架构章节结构可作大纲对照，但元素/接口/分配不得与本项目 source 混杂
- [ ] 平台/变型差异主题显式登记，供 SEC-DIFF 使用

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主题覆盖 | 缺即 gap，不可静默跳过 | 参考架构仅章节索引，不进事实条目 |
| L3 锚点 | 每条 critical claim 须有 L3 定位 | 不得用参考架构 L3 充当本项目 provenance |
| Δ 主题 | — | 新增/删除/修改类主题显式登记 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 参考架构元素/接口编入 `topic_index` 作事实 | 事实来源违规 |
| SyRS 主题无索引且无 gap | 分配与追溯链断裂 |
| L3 无 `location` 字段 | VC-2 失败 |

## A1 / A2 / B

**A1**：上游需求/架构/接口/分配主题可导航或 gap；L3 含 location；sample 仅章节索引。  
**A2**：补建目录、补 topic_index、修正 L3 锚点。  
**B**：SEC-REQTRACE / SEC-LARCH / SEC-IF / SEC-ALLOC 相关主题可跨文档导航。
