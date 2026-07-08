# IDD 子 skill · Step 1 · 输入材料

骨架：`skills/workflow-steps/step-input-materials/SKILL.md`（`task_type: ItemDefinitionDocument`）。领域规则：`skills/document-types/ItemDefinitionDocument/SKILL.md`。

## 本步目的要点

- 确认本步 run 元数据与 `task_type: ItemDefinitionDocument` 边界；共享 run 起点与 manifest / task_brief ownership 由通用 Step 1 / deterministic engine 负责。
- 登记 task.yaml 中每份输入：`file_id`、path、title、format、`role`。
- **source**：SyRS/SRS、架构、接口规范、ODD、假设清单等 → `is_fact_source=true`。
- **template**：IDD 模板 → T2。
- **checklist / reference**：检查项、ISO 26262-3 Clause 5 → T2/T3，`is_fact_source=false`。
- **sample**：既有 IDD 或 HARA 中 Item 章节样例 → T4，**仅形状**。
- 声明 IDD critical claims 须 `requires_human_confirmation`。
- **底线**：不得把 sample 中的 F-xx/边界/接口当作本项目事实。

## IDD 报告过程总览（本步定位）

Item Definition（Item 定义）属于 **ISO 26262-3:2018 第 5 章**，是 **概念阶段（Concept Phase）** 的起点之一，位于：

```
相关项定义（Item Definition）
    ↓
危害分析与风险评估（HARA，第 6 章）
    ↓
功能安全概念（FSC，第 7 章）…
```

**核心定位**：把待分析对象（Item）说清楚——是什么、做什么、边界在哪、与谁交互、在什么环境下运行——为 HARA 提供一致、可追溯的输入。

**重要边界**：

- Item Definition **不是** HARA，不写 hazard、S/E/C、ASIL、Safety Goal。
- Item Definition **不是** 合规批准书，不能写成「已满足 ISO 26262」「定义已最终批准」。

IDD 经 **13 个** workflow step skill 产出 Item 定义报告（逻辑 Step 1–6、9–15）。本步是流程入口，对应 **阶段 0：启动与范围对齐**。

### 阶段 0 · 启动与范围对齐（本步执行）

1. **明确 Item 范围**：例如「EPS 助力转向」「AEB 制动请求」等，避免与整车或其它 ECU 混淆。
2. **确定读者与下游**：HARA 负责人、系统工程师、安全经理。
3. **收集输入清单**，标注每份材料的 **角色**（事实源 / 模板 / 样例 / 方法学）。
4. **登记缺失材料**，不静默假设。

### 要回答的问题（本步须为后续步骤奠基）

| 问题 | 对应内容 | 本步动作 |
|---|---|---|
| 分析对象是谁？ | Item 名称、版本、变型、适用车型/平台 | 在 task_brief 中声明；登记 IDENT 来源 |
| Item 做什么？ | 功能清单 F-xx | 登记 SyRS/SRS 等 source |
| Item 管到哪里、不管什么？ | 系统边界 In / Out of scope | 登记架构/边界 source |
| 与外部如何连接？ | 外部接口 IF-xx（含方向） | 登记接口规范/信号矩阵 |
| 在什么条件下运行？ | 运行环境、物理/操作约束 | 登记 ODD/环境规范 |
| 典型使用场景？ | 运行工况 OS-xx、操作模式 | 登记场景/ODD source |
| 前提是什么？ | 假设、依赖 | 登记假设清单 source |
| 可能被怎样误用？ | 合理可预见误用 | 登记相关材料或 gap |
| 还缺什么？ | 开放项、待确认项 | 写入 `knowledge_gaps` |

## 输入材料（事实来源）

按汽车项目常见实践，输入通常包括：

| 类别 | 典型文档 | 用途 | role |
|---|---|---|---|
| 需求 | SyRS、SRS、功能需求 | F-xx、范围 | source |
| 架构 | 系统架构、子系统划分 | 边界 | source |
| 接口 | 接口规范、CAN/LIN 矩阵、信号列表 | IF-xx、方向 | source |
| 场景 | ODD、用例、场景说明 | 环境、工况 | source |
| 约束 | 环境规范、安装条件 | SEC-ENV | source |
| 假设 | 安全假设、依赖清单 | SEC-ASSUMP | source |
| 方法学 | ISO 26262-3 Clause 5、公司模板 | 结构与检查项 | reference / template |
| 样例 | 历史 IDD | **仅**章节/表格形状 | sample |

**原则**：样例文档、标准条文可以提供「怎么写」，不能替代本项目 SyRS/架构/接口中的「写什么」。

### 典型输入登记

| 材料 | role | is_fact_source |
|---|---|:---:|
| SyRS / SRS / 需求规格 | source | true |
| 系统架构 / 边界说明 | source | true |
| 接口规范 / 信号矩阵 | source | true |
| ODD / 场景说明 | source | true |
| 假设与约束 | source | true |
| IDD 模板 | template | false |
| Clause 5 检查清单 | checklist | false |
| ISO 26262-3 摘录 | reference | false |
| 样例 IDD | sample | false |

## 本步 Review / Checklist 要点

本步为审查奠基：Step 10/11 将回溯 manifest 的 role、tier、gap 登记是否完整。

### 输入阶段 Checklist（§5 材料登记）

- [ ] 功能描述来源已声明（§5.4.2）
- [ ] 边界与接口来源已声明（§5.4.3）
- [ ] 运行环境/约束来源已声明（§5.4.4）
- [ ] 误用（§5.4.4 b）相关材料已声明或 gap 登记
- [ ] 假设与依赖来源已声明
- [ ] 缺失项写入 `knowledge_gaps`，不静默跳过
- [ ] sample IDD 的 `role=sample`，`is_fact_source=false`
- [ ] 参考文档含版本号与日期

### 本步 Review 要点

| 维度 | 检查项 | 级别 |
|---|---|---|
| manifest 完整性 | role / tier / is_fact_source 非空 | P0 |
| provenance | 每条 source 含 path、format、file_id | P1 |
| 事实来源边界 | sample 未升格为 source | P0 |
| 缺口诚实性 | 缺失材料写入 `knowledge_gaps` | P0 |
| 边界材料 | Item 边界 source 已登记或 gap | P0 |
| 误用材料 | §5.4.4 b 相关材料已登记或 gap | P0 |
| 接口方向材料 | 信号矩阵/接口规范已登记或 gap | P1 |
| 参考可追溯 | 输入文档含版本号与日期 | P1 |

### 本步自检（交付前）

| 关联检查 | 自检方法 |
|---|---|
| VC-1-01 | 遍历 file_id，role/tier/is_fact_source 非空 |
| VC-2-04 | 每条 source 含 path、format、file_id |
| RD-2 | sample 必须 `is_fact_source=false` |
| RD-6 | 缺失材料已写入 `knowledge_gaps` |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主要风险 | 输入不全、推断填值 | 误用既有项目的边界/接口定义 |
| 本步动作 | 缺失项标 `[PENDING]`、登记 gap | 既有 IDD 样例 role 必须 `sample`；项目独立 source 单独登记 |

### 常见 P0（本步重点防）

| 错误 | 后果 |
|---|---|
| 把样例 IDD 标为 source | 事实错误，HARA 基线错误 |
| 缺材料时静默跳过 | 不可追溯，Confirmation Review 风险 |
| 未登记误用相关材料 | 不符合 §5.4.4 b，后续 HARA 漏场景 |

## A1 / A2 / B

**A1**：manifest 字段完整；sample/reference `is_fact_source=false`；无静默缺失；Item 范围已在 task_brief 声明。  
**A2**：补登材料、修正 role、登记 gap。  
**B**：核对 role/tier/gap；sample 未升格为 source。
