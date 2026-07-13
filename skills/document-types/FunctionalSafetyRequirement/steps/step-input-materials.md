# FSR 子 skill · Step 1 · 输入材料

骨架：`skills/workflow-steps/step-input-materials/SKILL.md`（`task_type: FunctionalSafetyRequirement`）。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`（与 `task_type: fsr` 语义相同）。

## 本步目的要点

- 确认本步 run 元数据与 `task_type: FunctionalSafetyRequirement`（或 `fsr`）边界；`init-run` 只负责 Phase 0 scaffold，本 overlay 的专业内容由明确选中它的 agent worker 负责。
- 登记 task.yaml 每份输入：`file_id`、path、title、format、`role`。
- **source**：Item 定义、Safety Goals、HARA 摘要/追溯、项目约束 → `is_fact_source=true`。
- **template**：FSR 模板 → T2。
- **checklist / reference**：FSR 检查项、需求写法参考 → T2/T3，`is_fact_source=false`。
- **sample**：样例 FSR → T4，**仅形状**。
- 声明 FSR critical claims 须 `requires_human_confirmation`。
- **底线**：不得把 sample 中的 FSR/SG/ASIL 当作本项目事实；HARA 摘要不得标为 HARA 批准记录。

## FSR 方法论（本步定位）

### 1.1 功能安全生命周期中的位置

```
Item 定义（Clause 5）
    ↓
HARA（Clause 6）→ Safety Goal（SG）
    ↓
功能安全概念 FSC（Clause 7）→ 功能安全需求 FSR  ← 本类型
    ↓
技术安全概念 TSC（Clause 8）…  ← 独立下游文档类型，FSR 不写
```

**FSR 核心作用**：在已确认的 **Safety Goal** 之下，把「系统/Item 为实现安全目标必须满足的功能层面需求」写成 **可追溯、可验证、可审查** 的需求条目。

### 1.2 本仓库定位

- 官方 L3 标签是 `fsr`；本 PascalCase 目录是可选 overlay guidance，不构成另一个 built-in，也没有独立 `fsr_pipeline`。
- 产出 **review-ready** FSR 候选包，**不是**需求批准书或合规认证。
- **明确不做 TSC**：不生成技术安全概念、技术安全需求、技术安全机制终稿。

### 1.3 重要边界

| 文档 | FSR 与之关系 |
|---|---|
| IDD | 上游：Item 范围、接口、工况（摘要引用） |
| HARA 报告 | 上游：SG 追溯；**不能把 HARA 摘要当新 HARA 或 blanket 批准** |
| Safety Goals | **核心追溯锚点**：每条 FSR 须链到 SG |
| TSC | **禁止**写技术安全机制/技术安全需求终稿 |
| 合规/批准 | 不能写「FSR 已批准」「需求集完整合规」「可量产」 |

本步是流程入口，对应 **阶段 0：启动与范围对齐**。

### 阶段 0 · 启动与范围对齐（本步执行）

1. 确认上游：**Item 定义上下文**、**已确认的 Safety Goals**、HARA 追溯摘要（若有）。
2. 明确 **不做 TSC**；FSR 止于功能层需求候选。
3. 收集输入，标注 role；登记缺失材料（如无 SG source → gap）。

### 要回答的问题（本步须为后续奠基）

| 问题 | 对应内容 | 本步动作 |
|---|---|---|
| 本文档范围是什么？ | 适用 Item、读者、不含 TSC/批准 | task_brief 声明 |
| 基于哪些输入？ | Item 定义、SG、HARA 摘要、约束 | 登记 source |
| 每条 FSR 追溯哪个 SG？ | Safety Goal 链接 | 登记 safety_goals_source |
| ASIL 从哪来？ | SG source | 同上 |
| 还缺什么？ | 开放项 | `knowledge_gaps` |

### 输入材料（事实来源）

| 类别 | 典型文档 | role | 用途 |
|---|---|---|---|
| Item 定义 | item_definition_source.md | source | Item 范围、接口、工况摘要 |
| 安全目标 | safety_goals_source.md | source | SG ID、表述、ASIL、安全状态 |
| HARA 追溯 | hara_summary_source.md | source | **仅**摘要中显式 HE→SG 追溯 |
| FSR 模板 | fsr_template.md | template | 章节与表列结构 |
| 审查清单 | fsr_checklist.md | checklist | 完备性检查 |
| 方法学 | fsr_reference.md | reference | 需求写法（**不证明项目事实**） |
| 样例 | fsr_sample.md | sample | **仅**章节/表格形状 |

**原则**：`fact source ≠ sample`；HARA 摘要 **不是** HARA 批准记录；reference 不能证明本项目 SG/ASIL。

## 本步 Review / Checklist 要点

### 全局原则（本步须落实登记）

| 原则 | 说明 |
|---|---|
| 追溯锚点 | 每条 FSR 须链到 **本项目 source** 中的 SG |
| 事实来源 | 仅 T0/T1；sample/reference **不能**支撑 FSR/SG/ASIL |
| HARA 摘要 | 仅显式 HE→SG，非 blanket 批准 |
| TSC | 禁止 TSC/技术机制终稿 |
| 措辞/交付 | 禁止批准/合规/量产；交付为 review-ready |

### 输入阶段 Checklist

- [ ] `task_type: FunctionalSafetyRequirement`（或 `fsr`）已确认
- [ ] **safety_goals_source** 已登记或 gap（**P0**）
- [ ] **item_definition_source** 已登记或 gap
- [ ] **hara_summary_source**（若有）`role=source`，notes 标明非 HARA 批准
- [ ] fsr_template / checklist / reference → `is_fact_source=false`
- [ ] **参考 FSR**（若有）→ `role=sample`，`is_fact_source=false`
- [ ] 缺失项写入 `knowledge_gaps`，不静默跳过

### 本步 Review 要点

| 检查项 | From-Scratch | With-Reference |
|---|---|---|
| SG source | 无则必须 gap，**不得开跑** | 参考 FSR **不能**替代 SG source |
| sample 边界 | 若有 sample，仅形状 | 参考 FSR **不得**标为 source |
| HARA 摘要 | 可选；无则 gap | 不得把参考 FSR 里的追溯当本项目事实 |
| manifest 完整性 | role/tier/file_id 齐全 | 参考与本项目 source **分 file_id 登记** |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主要风险 | 输入不全、静默推断 | 把参考 FSR 的 FSR/SG/ASIL 当本项目事实 |
| 本步动作 | 缺失标 `[PENDING]`、登记 gap | 参考 FSR 必须 `sample`；SG/Item 独立 source |

### 常见 P0（本步重点防）

| 错误 | 后果 |
|---|---|
| 无 SG 且无 gap 开跑 | FSR 无追溯锚点 |
| sample/参考 FSR 标为 source | 事实来源违规 |
| 把 HARA 摘要标为 HARA 批准 | 批准边界错误 |

## A1 / A2 / B

**A1**：manifest 完整；sample/reference `is_fact_source=false`；SG source 或 gap 已处理。  
**A2**：补登材料、修正 role、登记 gap。  
**B**：核对 role/tier/gap；sample 未升格为 source。
