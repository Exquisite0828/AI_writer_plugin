# TSC 子 skill · Step 3 · 文档目录索引

骨架：`skills/workflow-steps/step-source-index/SKILL.md`。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点

- 为每份输入建立 **L1→L2→L3** 语义目录树。
- `topic_index` 宜覆盖：**Safety Goal**、**FSR**、**HARA/FTTI**、**架构元素**、**Item 上下文**、**约束/假设**、**验证线索**。
- 样例 TSC 只索引章节结构，不将样例 TSR/机制编入事实条目。

## TSC 方法论（本步定位）

本步对应 **阶段 2：架构与安全元素识别**（索引环）——后续读原文的 **唯一导航入口**。

### 阶段 2 · 架构与安全元素识别（本步执行）

1. 在系统框图/架构 source 上标注所有 **安全相关元素**（传感器、控制器、执行器、通信、电源、看门狗、关键 SW 组件等）。
2. 识别 **单点失效**、**共因失效**敏感区域（记入 topic_index 备注，非新 HARA 结论）。
3. 形成 **「架构元素清单」**，作为后续 TSR 分配表与机制落点的主键。
4. 建立可检索索引，主题覆盖下表。

### 阶段 1 延续 · 索引主题

| 主题 | 典型入口 | 用途 |
|---|---|---|
| Safety Goal | safety_goals_source | SEC-SG、TSR 顶层追溯 |
| FSR | fsr_source | SEC-FSR、TSR 派生 |
| HARA / FTTI | hara_summary_source | SEC-FAULT、安全状态（**仅显式内容**） |
| 架构元素 | architecture_source | SEC-ARCH、SEC-TSR 分配、SEC-MECH |
| Item 上下文 | item_definition_source | SEC-ARCH 摘要 |
| 约束/假设 | 约束 source | SEC-LIMIT |
| 验证线索 | FSR/项目约束 | SEC-VERIF 计划 |

读材料顺序（贯穿全程）：`L1 → L2 → L3 → 原文摘录`

## 本步 Review / Checklist 要点

### 本步 Checklist

- [ ] 每份 **source** 有 L1→L2→L3 toc，L3 含 location
- [ ] `topic_index` 覆盖：SG、FSR、HARA/FTTI、架构、Item、约束、验证线索
- [ ] FSR 主题可导航或 gap
- [ ] 架构元素清单可从 topic_index 导航（阶段 2 产出）
- [ ] 单点/共因敏感区已标注或 gap（非危害结论，仅架构线索）
- [ ] sample/参考 TSC **未编入** topic_index 事实条目

### 本步 Review 要点

| From-Scratch | With-Reference |
|---|---|
| FSR 无索引且无 gap → **P0** | 参考 TSC **仅索引章节结构** |
| 架构无索引且无 gap → **P1**（分配将缺落点） | FSR→TSR 仅来自本项目 fsr_source，非参考 TSC |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | FSR 无索引无 gap | 参考 TSC 的 TSR-xx 进 topic_index |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 参考 TSC 的 TSR-xx 编入 topic_index 作事实 | 事实来源违规 |
| FSR 主题无索引且无 gap | 追溯链断裂 |

## A1 / A2 / B

**A1**：FSR/SG/架构主题可导航或 gap；L3 含 location。  
**A2**：补建目录、补 topic_index。  
**B**：SEC-TSR/SEC-MECH 相关主题可导航。
