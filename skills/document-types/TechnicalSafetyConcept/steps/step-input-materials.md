# TSC 子 skill · Step 1 · 输入材料

骨架：`skills/workflow-steps/step-input-materials/SKILL.md`（`task_type: TechnicalSafetyConcept`）。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点

- 创建 `runs/<run_id>/`，写入 manifest、`task_brief`；确认 `task_type: TechnicalSafetyConcept`（或 `tsc`）。
- 登记 task.yaml 每份输入：`file_id`、path、title、format、`role`。
- **source**：Item 定义、Safety Goals、FSR 确认清单、HARA 摘要/FTTI、系统架构、项目约束 → `is_fact_source=true`。
- **template**：TSC 模板 → T2。
- **checklist / reference**：TSC 检查项、写法参考 → T2/T3，`is_fact_source=false`。
- **sample**：样例 TSC → T4，**仅形状**。
- 声明 TSC critical claims 须 `requires_human_confirmation`。
- **底线**：不得把 sample 中的 TSR/机制/ASIL/架构分配当作本项目事实；FSR/HARA 摘要不得标为批准记录。

## TSC 方法论（本步定位）

### 1.1 功能安全生命周期中的位置

```
Item 定义（Part 3, Clause 5）
    ↓
HARA（Part 3, Clause 6）→ Safety Goal（SG）
    ↓
功能安全概念 FSC（Part 3, Clause 7）→ 功能安全需求 FSR
    ↓
技术安全概念 TSC（Part 4, Clause 8）  ← 本类型
    ↓
系统设计 / HW-SW 接口 / 软硬件安全需求细化
    ↓
硬件安全概念、软件安全概念、生产与运行…  ← HSC/SSC deferred
```

**核心转变**：FSR =「功能层面要实现什么」；TSC =「技术上如何落实到架构、机制、故障处理与接口」。FSR 技能止于功能层，不写 TSC；TSC 是独立下游交付物。

**TSC 核心作用**：在已确认的 **FSR / SG** 与 **系统架构** 之上，把「技术层面如何实现安全目标」写成 **可追溯、可验证、可审查** 的 TSR、机制与故障处理概念。

### 1.2 本仓库定位

- document-type skill 层，走统一 **13 步** workflow。
- 产出 **review-ready** TSC 候选包，**不是** TSC 批准书或合规认证。
- **明确不做 HSC/SSC**：不生成硬件/软件安全概念终稿或详细实现。

### 1.3 TSC 目的与边界

**目的（读者应能理解）**：

1. 每条 TSR 如何从 FSR/SG 派生
2. 安全需求在架构元素上的分配
3. 实现安全目标所需的技术安全机制
4. 故障检测与处理、安全状态、降级/警告策略
5. 为系统设计、HW-SW 接口、软硬件安全需求提供可追溯输入

| TSC 应包含 | TSC 通常不包含（留给下游） |
|---|---|
| TSR 及追溯 | 详细电路/软件实现 |
| 架构级分配与机制概念 | HSC/SSC 终稿 |
| 故障处理与安全状态策略 | 生产/运行/服务详细规程 |
| HW-SW/SW-SW 接口安全约束（概要） | 功能安全认证 sign-off |
| ASIL 分解/继承技术侧理由 | |

### 1.4 重要边界（与相邻文档）

| 文档 | TSC 与之关系 |
|---|---|
| FSR | 上游；**不得改写** SG/FSR 事实，只能派生 TSR |
| 系统设计 | 下游；机制细化为设计决策 |
| HSC / SSC | 下游；**禁止**写终稿 |
| 安全验证报告 | 下游验证 TSR；TSC **不宣称**已验证 |
| IDD | 上游：Item 范围、接口（摘要引用） |
| HARA 摘要 | 上游：FTTI、安全状态；**不能当新 HARA** |
| 合规/批准 | 不能写「TSC 已批准」「可量产」 |

本步是流程入口，对应 **阶段 0：启动与范围对齐**。

### 阶段 0 · 启动与范围对齐（本步执行）

1. 确认 TSC 覆盖边界：**Item、变型、ECU 范围**。
2. 锁定已批准（或 review-ready）的 **FSR/SG 版本**。
3. 确认上游：**Item 定义**、**Safety Goals**、**FSR 确认清单**、HARA 摘要（FTTI/安全状态）、**系统架构**（若有）。
4. 明确 **不做** 的事：不写详细实现、不做 HSC/SSC、不做合规认证结论。
5. 收集输入，标注 role；列出缺失输入（无架构图、无 FTTI 来源等）为 **open item**。

### 启动时必须回答的问题（3.3）

| # | 问题 | 本步处理 |
|---|---|---|
| 1 | TSC 覆盖哪个 Item / 系统 / 变型？ | task_brief 声明 |
| 2 | 哪些 FSR 在本轮 TSC 范围内？有无 deferred 项？ | 登记 fsr_source 范围或 gap |
| 3 | 架构是全新设计还是基于平台扩展？ | architecture_source 或 gap + notes |
| 4 | 是否存在 ASIL 分解？分解方案是否已获认可？ | 登记分解依据 source 或 HITL gap |
| 5 | 哪些 FTTI/FHTI 约束来自 HARA，必须在机制设计中体现？ | hara_summary_source 或 gap |
| 6 | 哪些关键假设尚待 HITL？ | `knowledge_gaps` / `requires_human_confirmation` |

### 必需上游输入（3.1）

| 输入 | 作用 | 本步 role |
|---|---|---|
| 已确认的 Safety Goals | 追溯顶层锚点 | source |
| 功能安全概念（FSC）/ FSR 集 | TSC 直接派生源 | source（**P0**） |
| Item 定义 / 系统边界 | 明确适用对象与接口 | source |
| 初步系统架构 | 分配 TSR、定义机制落点 | source |
| HARA 摘要（含 FTTI、安全状态） | 约束故障处理时间、安全状态 | source |
| 相关标准/企业规范 | 写法、命名、表格、ASIL 策略 | reference / checklist |
| 已有设计约束（平台、复用件、通信拓扑等） | 避免 TSC 与可实现架构脱节 | source |

### 建议辅助材料（3.2，登记或 gap）

| 材料 | 用途 |
|---|---|
| 系统框图、信号流图、状态机草案 | SEC-ARCH、SEC-MECH |
| FMEA 早期结果（若有） | 机制/故障上下文线索（**非**新 HARA） |
| 同类项目 TSC 样例 | **仅**结构与写法，`role=sample` |
| 诊断概念、降级策略企业 checklist | T2 完备性检查 |

### 要回答的问题（本步须为后续奠基）

| 问题 | 对应内容 | 本步动作 |
|---|---|---|
| 本文档范围是什么？ | 适用 Item/系统、读者、不含 HSC/SSC/批准 | task_brief 声明 |
| 基于哪些输入？ | FSR、SG、架构、HARA 摘要、约束 | 登记 source |
| 每条 TSR 追溯哪个 FSR/SG？ | FSR/SG 链接 | 登记 fsr_source、safety_goals_source |
| 架构元素从哪来？ | 系统架构 source | 登记 architecture_source 或 gap |
| ASIL / FTTI 从哪来？ | SG/FSR/HARA 摘要 | 同上 |
| 还缺什么？ | 开放项 | `knowledge_gaps` |

### 输入材料（事实来源）

| 类别 | 典型文档 | role | 用途 |
|---|---|---|---|
| Item 定义 | item_definition_source.md | source | Item 范围、接口、工况摘要 |
| 安全目标 | safety_goals_source.md | source | SG ID、表述、ASIL、安全状态 |
| 功能安全需求 | fsr_source.md | source | FSR-xx、SG 链接、功能层需求 |
| HARA 追溯/FTTI | hara_summary_source.md | source | **仅**摘要中显式 FTTI、安全状态、HE→SG |
| 系统架构 | architecture_source.md | source | 架构元素、分配落点 |
| TSC 模板 | tsc_template.md | template | 章节与表列结构 |
| 审查清单 | tsc_checklist.md | checklist | 完备性检查 |
| 方法学 | tsc_reference.md | reference | 写法（**不证明项目事实**） |
| 样例 | tsc_sample.md | sample | **仅**章节/表格形状 |

**原则**：`fact source ≠ sample`；FSR source **不是** blanket 批准；HARA 摘要 **不是** HARA 批准记录；reference 不能证明本项目 TSR/机制。

## 本步 Review / Checklist 要点

### 全局原则（本步须落实登记）

| 原则 | 说明 |
|---|---|
| 追溯锚点 | 每条 TSR 须链到 **本项目 source** 中的 FSR 与 SG |
| 事实来源 | 仅 T0/T1；sample/reference **不能**支撑 TSR/机制/ASIL |
| FSR 边界 | 仅显式 FSR-xx，非 blanket 批准 |
| HARA 摘要 | 仅显式 FTTI/安全状态，非新 HARA |
| HSC/SSC | 禁止 HSC/SSC/详细实现终稿 |
| 措辞/交付 | 禁止批准/合规/量产；交付为 review-ready |

### 输入阶段 Checklist

- [ ] `task_type: TechnicalSafetyConcept`（或 `tsc`）已确认
- [ ] **fsr_source** 已登记或 gap（**P0**）
- [ ] **safety_goals_source** 已登记或 gap（**P0**）
- [ ] **architecture_source** 已登记或 gap
- [ ] **item_definition_source** 已登记或 gap
- [ ] **hara_summary_source**（若有）`role=source`，notes 标明非 HARA 批准
- [ ] tsc_template / checklist / reference → `is_fact_source=false`
- [ ] **参考 TSC**（若有）→ `role=sample`，`is_fact_source=false`
- [ ] 缺失项写入 `knowledge_gaps`，不静默跳过

### 本步 Review 要点

| 检查项 | From-Scratch | With-Reference |
|---|---|---|
| FSR source | 无则必须 gap，**不得开跑** | 参考 TSC **不能**替代 FSR source |
| SG source | 无则必须 gap | 参考 TSC **不能**替代 SG source |
| sample 边界 | 若有 sample，仅形状 | 参考 TSC **不得**标为 source |
| 架构 source | 无则 gap，不静默编造元素 | 参考 TSC 架构 **不得**当本项目事实 |
| manifest 完整性 | role/tier/file_id 齐全 | 参考与本项目 source **分 file_id 登记** |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主要风险 | 输入不全、静默推断 | 把参考 TSC 的 TSR/机制/ASIL 当本项目事实 |
| 本步动作 | 缺失标 `[PENDING]`、登记 gap | 参考 TSC 必须 `sample`；FSR/SG/架构独立 source |

### 常见 P0（本步重点防）

| 错误 | 后果 |
|---|---|
| 无 FSR 且无 gap 开跑 | TSR 无追溯锚点 |
| sample/参考 TSC 标为 source | 事实来源违规 |
| 把 HARA 摘要标为 HARA 批准 | 批准边界错误 |
| 把 FSR source 标为 FSR 已批准 | 上游边界错误 |

## A1 / A2 / B

**A1**：manifest 完整；sample/reference `is_fact_source=false`；FSR/SG source 或 gap 已处理。  
**A2**：补登材料、修正 role、登记 gap。  
**B**：核对 role/tier/gap；sample 未升格为 source。
