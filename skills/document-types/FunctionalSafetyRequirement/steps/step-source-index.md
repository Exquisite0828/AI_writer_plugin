# FSR 子 skill · Step 3 · 文档目录索引

骨架：`skills/workflow-steps/step-source-index/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点

- 为每份输入建立 **L1→L2→L3** 语义目录树。
- `topic_index` 宜覆盖：**Safety Goal**、**HARA 追溯**、**Item 上下文**、**约束/假设**、**验证线索**。
- 样例 FSR 只索引章节结构，不将样例需求编入事实条目。

## FSR 方法论（本步定位）

本步对应 **阶段 1：材料消化与索引**——后续读原文的 **唯一导航入口**。

### 阶段 1 · 索引（本步执行）

建立可检索索引，主题覆盖：

| 主题 | 典型入口 | 用途 |
|---|---|---|
| Safety Goal | safety_goals_source | SEC-SG、FSR 链接 |
| HARA 追溯 | hara_summary_source | HE→SG（**仅显式内容**） |
| Item 上下文 | item_definition_source | SEC-ITEM |
| 约束/假设 | 约束 source | SEC-LIMIT |
| 验证线索 | SG/项目约束 | SEC-VERIF 计划 |

读材料顺序（贯穿全程）：`L1 → L2 → L3 → 原文摘录`

## 本步 Review / Checklist 要点

### 本步 Checklist

- [ ] 每份 **source** 有 L1→L2→L3 toc，L3 含 location
- [ ] `topic_index` 覆盖：SG、HARA 追溯、Item、约束、验证线索
- [ ] SG 主题可导航或 gap
- [ ] sample/参考 FSR **未编入** topic_index 事实条目

### 本步 Review 要点

| From-Scratch | With-Reference |
|---|---|
| SG 无索引且无 gap → **P0** | 参考 FSR **仅索引章节结构** |
| 为 VC-2 准备 provenance | HE→SG 仅来自本项目 hara_summary，非参考 FSR |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | SG 无索引无 gap | 参考 FSR 的 FSR-xx 进 topic_index |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 参考 FSR 的 FSR-xx 编入 topic_index 作事实 | 事实来源违规 |
| SG 主题无索引且无 gap | 追溯链断裂 |

## A1 / A2 / B

**A1**：SG/追溯/Item 主题可导航或 gap；L3 含 location。  
**A2**：补建目录、补 topic_index。  
**B**：SEC-SG/SEC-FSR 相关主题可导航。
