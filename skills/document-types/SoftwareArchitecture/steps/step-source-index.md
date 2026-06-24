# Software Architecture 子 skill · Step 3 · 文档目录索引

骨架：`skills/workflow-steps/step-source-index/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点

- 为每份输入建立 **L1→L2→L3** 语义目录树。
- `topic_index` 覆盖 9 大主题，作为后续 EVD provenance 的 **唯一导航入口**。
- 历史 SwAD 只索引章节结构，不将样例组件/接口编入事实条目。

## Software Architecture 方法论（本步定位）

### 3.1 本步在八阶段方法链中的位置

本步对应 **阶段 1：材料消化与索引** 的第二环。Step 2 提取了候选摘要；本步建立 **可检索的 L3 锚点**，使 Step 6 的每条 EVD 都能追溯到「哪份文档、哪一章、哪一段」。

**方法原则**：读材料顺序固定为 `L1 → L2 → L3 → 原文摘录`。禁止跳读后直接写架构结论。

### 3.2 阶段 1 · 索引（本步执行）

#### 通用索引方法

1. 为每份 **source** 建 `document_tocs/<file_id>.md`，L3 必须含 `location`（页码/章节号/段落）。
2. 建 `topic_index.json`，把跨文档主题归并到统一入口。
3. 每个 topic 至少 1 个命中，或显式 `gap` 登记到 `knowledge_gaps.md`。

#### topic_index 九主题与章节映射

| topic_key | 典型 source 入口 | 支撑章节 |
|---|---|---|
| upstream_swrs | swrs_source | SEC-UPTRACE、SEC-ALLOC |
| system_arch_context | current_system_architecture | SEC-SWCTX、SEC-UPTRACE |
| logical_sw_arch | software_context | SEC-LOGARCH |
| physical_sw_arch | rte_bsw_constraints | SEC-PHYSARCH |
| sw_interface | interface_spec | SEC-IF |
| swrs_allocation | swrs_source + swad hints | SEC-ALLOC |
| task_scheduling | os_cfg / rte_bsw | SEC-PHYSARCH、SEC-RES |
| diagnostic_degradation | diagnostic_constraints | SEC-DIAG |
| resource_timing | platform_constraints | SEC-RES |
| safety_sw_ref | tsr_or_safety_sw | SEC-SAFE-ARCH |

#### From-Scratch 方法要点

| 动作 | 方法说明 |
|---|---|
| SwRS 主题 | **P0**：无索引且无 gap 则阻断 |
| 接口主题 | SWR-IF 与 RTE 规范须能交叉导航；缺则 gap |
| 分配主题 | 即使只有候选映射，也须在 SwRS 章节有 L3 锚点 |
| BSW/任务 | 无 OS 配置时，task_scheduling 主题 gap，不借模板填 |

#### With-Reference 方法要点

| 动作 | 方法说明 |
|---|---|
| 历史 SwAD toc | 仅 `document_tocs/<ref>.md`，**禁止**编入 `topic_index` 事实条目 |
| Δ 主题预建 | 增 `topic_key=variant_delta`，登记结构差异线索（非事实） |
| 交叉验证 | 参考 SwAD 某章有而本项目 SwRS 无 → 记 gap 或 Δ 线索，不补内容 |

### 3.3 索引质量判据（ASPICE 追溯准备）

- 每条未来 `SWA-COMP` / `SWA-IF` / 分配行，应能指向至少 1 个 L3 锚点或 open。
- 接口 topic 的 L3 摘录应能显示 **方向** 或 **对端** 信息（或明确 gap）。

## 本步 Review / Checklist 要点

### ASPICE SWE.2 追溯索引 Checklist（BP5/BP6 前置）

| 检查项 | 通过条件 |
|---|---|
| SwRS 主题可导航 | `upstream_swrs` 有 L3 命中或 gap |
| 分配主题可导航 | `swrs_allocation` 有 L3 或 gap |
| 接口主题可导航 | `sw_interface` 有 L3 或 gap |
| 架构上下文可导航 | `system_arch_context` 有 L3 或 gap |
| L3 含 location | 每条 L3 有页码/章节/段落定位 |

### ISO 26262-6 索引 Checklist

- [ ] `safety_sw_ref` 主题：有 TSR/软件安全 source 的 L3 或 gap
- [ ] 安全主题索引 **不**包含 HARA/ASIL 新分析条目
- [ ] 安全 L3 摘录仅为可引用约束，未扩展为机制设计

### 按章节索引覆盖 Checklist

| 章节 | topic_key | 通过条件 |
|---|---|---|
| SEC-UPTRACE | upstream_swrs | SWR-F/IF 章节可导航 |
| SEC-SWCTX | system_arch_context | 分层/运行模式可导航 |
| SEC-LOGARCH | logical_sw_arch | 功能分解可导航 |
| SEC-PHYSARCH | physical_sw_arch, task_scheduling | 组件/任务/BSW 可导航 |
| SEC-IF | sw_interface | RTE/服务/API 规范可导航 |
| SEC-ALLOC | swrs_allocation | 分配相关章节可导航 |
| SEC-DIAG | diagnostic_degradation | 诊断约束可导航 |
| SEC-RES | resource_timing | 平台/内存/时序可导航 |
| SEC-SAFE-ARCH | safety_sw_ref | TSR 摘要可导航或 gap |

### 通用 Checklist（8 项）

- [ ] 每份 **source** 有 L1→L2→L3 toc，L3 **必须含 `location`**
- [ ] `topic_index` 九主题覆盖或每主题显式 gap
- [ ] template / checklist / reference / sample **不进** `topic_index` 事实条目
- [ ] `provenance_index.json` 与 document_tocs 一致
- [ ] 接口 topic 的 L3 能显示方向或对端，或该字段 gap
- [ ] 跨文档 topic 可串联（如 SwRS SWR-IF ↔ interface_spec）
- [ ] gap 写入 `knowledge_gaps.md` 并链到 SEC-*
- [ ] 读序 `L1→L2→L3→原文` 在 toc 中可执行

### From-Scratch 专属 Checklist

- [ ] SwRS 主题无索引且无 gap → **P0**
- [ ] 接口 / 分配 / 资源主题缺索引则 **必须** gap
- [ ] 无 BSW/OS 材料时 task_scheduling 主题 gap，不借模板填

### With-Reference 专属 Checklist

- [ ] 历史 SwAD 仅 `document_tocs/<ref>.md`，**禁止**编入 `topic_index` 事实（**P0**）
- [ ] `variant_delta` 主题已建或注明「无结构差异线索」
- [ ] 参考 SwAD 的 L3 **不得**充当本项目 EVD provenance
- [ ] 参考有而本项目无的主题记为 gap 或 delta 线索，不补事实条目

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主题覆盖 | 缺即 gap，不可静默跳过 | 历史 SwAD 仅章节 toc |
| L3 锚点质量 | location 完整，摘录可定位 | 不得用参考 L3 当本项目 provenance |
| 追溯链 | SwRS↔接口↔分配可交叉导航 | 同上；Δ 主题仅线索非事实 |
| 安全索引 | 仅 TSR 引用条目 | 无参考安全条目进 topic_index |

### P0 失效项

| 失效 | 后果 |
|---|---|
| 历史 SwAD 组件/接口编入 `topic_index` 作事实 | 事实来源违规 |
| SwRS 主题无索引且无 gap | 追溯链断裂 |
| L3 无 `location` | Step 11 VC-2 失败 |
| sample 进 topic_index 事实条目 | tier 违规 |

### P1 失效项

- topic_index 缺 file_id 或 L1/L2 路径
- 同一主题多 source 未合并导航
- 接口 topic 无方向信息也未标 gap

### 一句话归纳

**Checklist 核心**：九主题可导航或 gap；L3 含 location；sample 不进事实索引。  
**Review 核心**：From-Scratch 查 SwRS/接口/分配锚点；With-Reference 查历史 SwAD 是否污染 topic_index。

## A1 / A2 / B

**A1**：九主题可导航或 gap；L3 含 location；sample 隔离。  
**A2**：补 toc、topic_index、L3 锚点。  
**B**：SEC-UPTRACE / SEC-IF / SEC-ALLOC 可跨文档导航。
