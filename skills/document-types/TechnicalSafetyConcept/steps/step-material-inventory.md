# TSC 子 skill · Step 2 · 材料清单

骨架：`skills/workflow-steps/step-material-inventory/SKILL.md`。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点

- 解析每份材料，产出 `inputs/input_inventory.json`。
- **source** 摘要须覆盖：SG 列表、FSR-xx 列表、HARA 追溯/FTTI 片段、架构元素、Item 上下文、约束/假设、候选 TSR 线索。
- **sample** 仅入 `style_hint`，**禁止**写入 TSR/机制/ASIL/架构分配事实字段。
- 失败/缺失如实标记。

## TSC 方法论（本步定位）

本步对应 **阶段 1：输入材料清点与来源分级** 第一环——在索引（Step 3）前结构化解析。

### 阶段 1 · 材料消化与来源分级（本步执行）

1. 解析 fsr_source、safety_goals_source、hara_summary、architecture_source、item_definition 等。
2. 从 **source** 提取 **候选 TSR-xx**（未定稿）及机制线索。
3. **样例 TSC** 只提取表头、章节粒度，不复制 TSR/机制/ASIL/架构内容。

### 来源分级（T0–T5，硬规则）

| 层级 | 含义 | TSC 中的用法 | critical claim |
|---|---|---|---|
| T0 | 人工确认/HITL | 架构裁断、ASIL 分解批准 | 允许 |
| T1 | 项目事实来源 | SG、FSR、HARA、Item 定义、架构 | 允许 |
| T2 | 模板/checklist | 章节结构、检查项 | 仅结构 |
| T3 | 参考方法 | 写法指南 | 不单独证明项目事实 |
| T4 | 样例 | 仅借表格形状与风格 | **禁止** |
| T5 | 推断 | — | **禁止** |

**硬规则**：样例 TSC 中的 TSR、机制、ASIL **不能**当成本项目事实。

### 各 role 提取重点

| role | 须提取 | 禁止 |
|---|---|---|
| fsr_source | FSR ID、表述、Linked SG、ASIL | 标为 TSR 已确认或 FSR 已批准 |
| safety_goals_source | SG ID、表述、ASIL、safe state | 标为 TSR 已确认 |
| hara_summary_source | 显式 FTTI、安全状态、HE→SG | 扩展为新危害判断 |
| architecture_source | 架构元素、模块/ECU/通道清单 | 当作详细系统设计定稿 |
| item_definition_source | Item 范围、模式/接口摘要 | 当作完整 IDD 定稿 |
| tsc_reference | 写法要点标题 | 当作项目 TSR/机制事实 |
| fmea_early（若有） | 故障模式线索标题 | 扩展为新危害判断或标为机制事实 |
| sample | 表头、TSR/机制列定义 | 提取具体 TSR/机制/ASIL/分配 |

## 本步 Review / Checklist 要点

### 本步 Checklist

- [ ] 每份材料有 `parse_status`
- [ ] source 摘要覆盖：SG、FSR、HARA/FTTI、架构元素、Item 上下文、候选 TSR 线索
- [ ] sample/参考 TSC **未流入** TSR/机制/ASIL/架构事实字段
- [ ] 候选 TSR **未标** confirmed

### 本步 Review 要点

| From-Scratch | With-Reference |
|---|---|
| 缺 FSR 须在 inventory 标 gap | 解析参考 TSC 时 **只提取 style_hint**，不提取 TSR/机制正文 |
| 缺架构须在 inventory 标 gap | 参考 TSC 中的 TSR-ID **不得**写入本项目事实字段 |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 静默跳过 parse 失败 | 参考 TSR 进 inventory 事实字段 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 参考 TSC 需求照抄进 inventory | 事实来源违规 |
| 从 HARA 摘要推断未列出的 FTTI | 越权时间约束 |
| 从 FSR 推断未列出的技术机制 | 越权技术结论 |
| 解析失败静默跳过 | 不可追溯 |

## A1 / A2 / B

**A1**：parse_status 齐全；sample 未流入事实字段。  
**A2**：重解析失败项、补摘要。  
**B**：摘要支撑 SEC-SG/SEC-FSR/SEC-TSR/SEC-ARCH。
