# FSR 子 skill · Step 2 · 材料清单

骨架：`skills/workflow-steps/step-material-inventory/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点

- 解析每份材料，产出 `inputs/input_inventory.json`。
- **source** 摘要须覆盖：SG 列表、HARA 追溯片段、Item 上下文、约束/假设、候选 FSR 线索。
- **sample** 仅入 `style_hint`，**禁止**写入 FSR/SG/ASIL 事实字段。
- 失败/缺失如实标记。

## FSR 方法论（本步定位）

本步对应 **阶段 1：材料消化** 第一环——在索引（Step 3）前结构化解析。

### 阶段 1 · 材料消化（本步执行）

1. 解析 safety_goals_source、hara_summary、item_definition 等。
2. 从 **source** 提取 **候选 FSR-xx**（未定稿）。
3. **样例 FSR** 只提取表头、章节粒度，不复制需求/SG/ASIL 内容。

### 各 role 提取重点

| role | 须提取 | 禁止 |
|---|---|---|
| safety_goals_source | SG ID、表述、ASIL、safe state | 标为 FSR 已确认 |
| hara_summary_source | 显式 HE→SG 追溯 | 扩展为新危害判断 |
| item_definition_source | Item 范围、模式/接口摘要 | 当作完整 IDD 定稿 |
| fsr_reference | 写法要点标题 | 当作项目 SG/ASIL 事实 |
| sample | 表头、FSR 列定义 | 提取具体需求/SG/ASIL |

## 本步 Review / Checklist 要点

### 本步 Checklist

- [ ] 每份材料有 `parse_status`
- [ ] source 摘要覆盖：SG、HARA 追溯、Item 上下文、候选 FSR 线索
- [ ] sample/参考 FSR **未流入** FSR/SG/ASIL 事实字段
- [ ] 候选 FSR **未标** confirmed

### 本步 Review 要点

| From-Scratch | With-Reference |
|---|---|
| 缺 SG 须在 inventory 标 gap | 解析参考 FSR 时 **只提取 style_hint**，不提取需求正文 |
| 七大主题线索可部分为空但须显式 | 参考 FSR 中的 FSR-ID **不得**写入本项目事实字段 |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 静默跳过 parse 失败 | 参考需求进 inventory 事实字段 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 参考 FSR 需求照抄进 inventory | 事实来源违规 |
| 从 HARA 摘要推断未列出的 SG | 越权追溯 |
| 解析失败静默跳过 | 不可追溯 |
| 解析失败静默跳过 | 不可追溯 |

## A1 / A2 / B

**A1**：parse_status 齐全；sample 未流入事实字段。  
**A2**：重解析失败项、补摘要。  
**B**：摘要支撑 SEC-SG/SEC-FSR/SEC-ASIL。
