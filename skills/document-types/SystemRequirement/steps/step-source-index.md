# SyRS 子 skill · Step 3 · 文档目录索引

骨架：`skills/workflow-steps/step-source-index/SKILL.md`。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点

- 为每份输入建立 **L1→L2→L3** 语义目录树。
- `topic_index` 宜覆盖：**干系人需求**、**功能**、**接口**、**性能**、**环境**、**诊断**、**追溯**、**安全引用**。
- 样例 SyRS 只索引章节结构，不将样例需求编入事实条目。

## SyRS 方法论（本步定位）

本步对应 **阶段 1：材料消化与索引**——后续读原文的 **唯一导航入口**。

### 阶段 1 · 索引（本步执行）

建立可检索索引，主题覆盖：

| 主题 | 典型入口 | 用途 |
|---|---|---|
| 干系人需求 | swrs_source、rfq | SEC-STAKE、SEC-TRACE |
| 功能 | SWRS 功能章节 | SEC-FUNC |
| 接口 | interface_spec | SEC-IF |
| 性能 | SWRS、技术规范 | SEC-PERF |
| 环境/工况 | odd、电气规范 | SEC-ENV |
| 诊断 | diagnostic_spec | SEC-DIAG |
| 安全引用 | fsr_source（若有） | SEC-SAFE（仅引用） |
| 法规 | regulatory_list | SEC-LEGAL |

读材料顺序（贯穿全程）：`L1 → L2 → L3 → 原文摘录`

## 本步 Review / Checklist 要点

### 通用 Checklist（每次 run 必查）

- [ ] 每份 **source** 有 L1→L2→L3 toc，**L3 必须含 `location`**（页/段/行锚点）
- [ ] 每份 **template / checklist / reference / sample** 仅作章节结构索引，不进 `topic_index` 事实条目
- [ ] `topic_index` 覆盖 **8 主题**：干系人需求 / 功能 / 接口 / 性能 / 环境 / 诊断 / 法规 / 安全引用
- [ ] 每个 topic 至少 1 个 file_id + L1/L2/L3 命中，或显式登记 gap
- [ ] `document_tocs/<file_id>.md` 可读、章节顺序与原文一致
- [ ] 跨文档导航：同主题（如接口）至少能从 `source_index.topic_index` 跳到所有相关 file_id

### 索引覆盖度 Checklist（按章节）

| 章节 | 主题入口 | 通过条件 |
|---|---|---|
| SEC-STAKE | 干系人需求 | swrs/rfq 至少 1 个 L3 命中 |
| SEC-FUNC | 功能 | 功能描述章节可导航 |
| SEC-IF | 接口 | 接口规范 + CAN 矩阵可导航 |
| SEC-PERF | 性能 | 性能/时序章节可导航或 gap |
| SEC-ENV | 环境 | ODD/电气规范可导航或 gap |
| SEC-DIAG | 诊断 | 诊断规范可导航或 gap |
| SEC-LEGAL | 法规 | 法规清单可导航或显式不适用 |
| SEC-SAFE | 安全引用 | FSR/SG 文档可导航或 gap |
| SEC-TRACE | 上游 ID | swrs/rfq 中的 ID 列表可导航 |

### ASPICE / ISO 维度 Checklist

- [ ] **ASPICE SYS.2 BP5**：上游 SWRS 文档的需求 ID 章节可被 L3 精确定位（追溯前置条件）
- [ ] **ISO 26262-3 §5**：Item 功能/边界/接口主题在 source 中可导航（为下游 IDD 提供 provenance）
- [ ] **ISO 26262-3 §7**：若有 FSR/SG 文档，SG ID 与 FSR ID 章节可导航
- [ ] 接口主题须细分为：信号清单 / 物理接口 / 诊断接口 / HMI（按 source 实际结构）

### From-Scratch 专属 Checklist

- [ ] SWRS 主题无索引且无 gap → **P0**
- [ ] 接口主题无索引 → 影响 SEC-IF 全章可写性，须 gap 登记
- [ ] FSR/SG 通常无 → SEC-SAFE 主题登记 gap，不视为错误

### With-Reference 专属 Checklist

- [ ] 参考 SyRS 仅建 `document_tocs/<ref_file_id>.md`，**禁止**编入 `topic_index` 作事实条目（**P0**）
- [ ] 参考 SyRS 章节结构可作为大纲对照；但其需求/接口/限值 **不得**与本项目 source 同主题混杂
- [ ] 平台/变型差异主题（如「新增网络安全要求」）显式作为 topic 登记，供 SEC-DIFF 使用
- [ ] 参考 SyRS 与本项目 source 在 `topic_index` 中**分开存储**（不同 `provenance.file_id`）

### 本步 Review 要点（双情景对比）

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主题覆盖 | 缺即 gap，不可静默跳过 | 参考 SyRS 仅章节索引，不进事实条目 |
| L3 锚点 | 每条 critical claim 须有 L3 定位 | 不得用参考 SyRS L3 充当本项目 provenance |
| Δ 主题 | — | 新增/删除/修改类主题显式登记 |
| 跨文档导航 | 接口主题跨 file_id 可跳转 | 本项目 source 与参考 SyRS 主题不混 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 参考 SyRS 的 SYS-xx 编入 `topic_index` 作事实 | 事实来源违规（**P0**） |
| SWRS 主题无索引且无 gap | 追溯链断裂 |
| L3 无 `location` 字段 | VC-2 失败 |
| 接口主题无索引但仍标 ready | SEC-IF 写作时编造 provenance |

### 常见 P1

- topic 粒度过粗（如「需求」一个主题打包所有功能/接口）
- 模板/checklist 误进 `topic_index`
- `document_tocs/<file_id>.md` 与 `provenance_index.json` 不同步

## A1 / A2 / B

**A1**：SWRS/功能/接口主题可导航或 gap；L3 含 location；sample 仅章节索引。  
**A2**：补建目录、补 topic_index、修正 L3 锚点。  
**B**：SEC-STAKE/SEC-FUNC/SEC-IF/SEC-TRACE 相关主题可跨文档导航。
