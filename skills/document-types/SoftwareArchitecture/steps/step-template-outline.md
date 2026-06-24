# Software Architecture 子 skill · Step 4 · 模板大纲

骨架：`skills/workflow-steps/step-template-outline/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点

### 阶段 A · L1

- 读 task_brief、SwAD template（T2）、sample SwAD（T4，仅形状）。
- 产出 `outline_l1.md` + `template_structure.json`。
- **不写** 正文；**不含** HARA/FSR/TSC/详细设计章。

### 阶段 B · L2

- 为每个强制 L1 定义 L2 小节与 **表列结构**（组件表、接口表、分配矩阵）。
- 缺口 L2 标 `evidence: pending`。
- **With-Reference**：L1 含 **SEC-DIFF**。

## Software Architecture 方法论（本步定位）

### 4.1 本步在八阶段方法链中的位置

本步对应 **阶段 2：定大纲（先 L1，后 L2）**。把 ASPICE SWE.2 与汽车控制器 SwAD 的 **文档形状** 固定下来，为后续证据映射与成稿提供 **空槽位**。

**方法原则**：大纲只定义「写什么、表有哪些列」，不在本步填架构事实。无材料的 L2 标 `pending`，不得标 `complete`。

### 4.2 阶段 2 · 定大纲（本步执行）

#### 通用 L1 结构方法（ASPICE SWE.2 映射）

按以下逻辑顺序组织 L1（可与模板微调，但强制章不可删）：

```text
范围与输入 → 软件上下文 → 上游追溯 → 逻辑架构 → 物理/战术架构
→ 组件清单 → 接口架构 → SwRS 分配 → 诊断架构 → 资源/实时
→ 安全引用（若有）→ 验证候选 → 假设与开放项 → 审查声明
[→ SEC-DIFF 仅 With-Reference]
```

| SWE.2 产出 | L1 章节 | L2 核心表/图 |
|---|---|---|
| 静态架构 | SEC-LOGARCH、SEC-COMP | 功能分解图、组件表 |
| 动态架构 | SEC-PHYSARCH、SEC-RES | 任务/调度表、模式转换 |
| 接口规格 | SEC-IF | SWA-IF 表（含 Direction） |
| 追溯 | SEC-UPTRACE、SEC-ALLOC | SwRS 摘要表、分配矩阵 |
| 约束 | SEC-DIAG、SEC-RES | 诊断链路、资源预算表 |

#### 汽车控制器 L2 表列标准（须在 outline 中定义）

**软件组件表（SEC-COMP）**

| 列 | 说明 |
|---|---|
| SWA-COMP ID | 唯一标识 |
| Component name | 组件名称 |
| Layer | App / RTE / BSW / OS / CDD |
| Responsibility | 职责摘要 |
| Boundary | In scope / External / Shared |
| Linked SwRS | SWR-F / SWR-IF |
| Task / scheduling hint | 关联任务（可 pending） |
| Evidence source | T0/T1 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

**软件接口表（SEC-IF）**

| 列 | 说明 |
|---|---|
| SWA-IF ID | 唯一标识 |
| Interface name | 接口名称 |
| Type | RTE Port / Service / Internal API / Callback |
| **Direction** | Provider / Consumer / Bidirectional（**强制**） |
| Counterpart | 对端组件/BSW 模块 |
| Protocol / medium | 信号映射 / SOME/IP / shared memory |
| Linked components | 关联 SWA-COMP |
| Linked SwRS | 关联 SWR-IF |
| Evidence source | T0/T1 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

**分配矩阵（SEC-ALLOC）**

| 列 | 说明 |
|---|---|
| Upstream SwRS ID | SWR-F / SWR-IF |
| SWA-COMP ID | 分配到的组件 |
| Allocation type | Primary / Supporting / Shared |
| Rationale | 分配理由 |
| Interface impact | 相关 SWA-IF |
| Status | confirmed / NEEDS_USER_CONFIRMATION |

#### From-Scratch 方法要点

| 动作 | 方法说明 |
|---|---|
| 空槽优先 | 无 source 的 L2 全部 `evidence: pending` |
| 表列完整 | 即使零行数据，组件/接口/分配表列定义必须齐全 |
| 不预填 ID | 不在大纲阶段生成 SWA-COMP-001 等虚构 ID |
| SEC-SAFE-ARCH | 通常设 L2 占位 + pending |

#### With-Reference 方法要点

| 动作 | 方法说明 |
|---|---|
| 形状借鉴 | 可参考历史 SwAD 的章节顺序、图类型、表列 **名称** |
| 正文隔离 | 参考文档的组件名/接口/数值 **不得**进入 outline 正文 |
| SEC-DIFF L2 | 定义列：Ref ID / Project ID / Δ Type / Δ Description / Project Evidence |
| Δ Type 枚举 | Added / Removed / Modified / Scope-changed |

### 4.3 强制 L1 清单

SEC-SCOPE、SEC-INPUT、SEC-SWCTX、SEC-UPTRACE、SEC-LOGARCH、SEC-PHYSARCH、SEC-COMP、SEC-IF、SEC-ALLOC、SEC-DIAG、SEC-RES、SEC-VERIF、SEC-ASSUMP、SEC-REVIEW；With-Reference 加 SEC-DIFF。

## 本步 Review / Checklist 要点

### ASPICE SWE.2 大纲对齐 Checklist（L1/L2 须覆盖）

| SWE.2 BP | 大纲章节 | L2 须含 |
|---|---|---|
| **BP1 静态架构** | SEC-LOGARCH、SEC-COMP、SEC-IF | 组件表、接口表（含 Direction 列） |
| **BP2 动态架构** | SEC-PHYSARCH、SEC-RES | 任务/调度表、模式转换槽位 |
| **BP5 追溯** | SEC-UPTRACE、SEC-ALLOC | SwRS 摘要表、分配矩阵 |
| **BP6 一致性** | SEC-UPTRACE + SEC-ALLOC 并列 | 追溯与分配列定义齐全 |
| **BP7 沟通** | SEC-SCOPE、SEC-REVIEW、SEC-OPEN | 范围、审查、开放项槽位 |

### ISO 26262-6 大纲 Checklist

- [ ] SEC-SAFE-ARCH 为可选 L1，若有 TSR 输入则设 L2 占位
- [ ] 大纲 **无** HARA/ASIL/SG/TSR 新编章节
- [ ] 大纲 **无** 详细设计/单元设计/代码章
- [ ] SEC-DIAG 与 SEC-RES 分列，支撑安全相关约束与资源隔离表述（引用级）

### 强制 L1 / 三表列 Checklist

- [ ] 强制 L1 齐全：SCOPE、INPUT、SWCTX、UPTRACE、LOGARCH、PHYSARCH、COMP、IF、ALLOC、DIAG、RES、VERIF、ASSUMP、REVIEW
- [ ] **软件组件表**列：SWA-COMP ID、Layer、Responsibility、Boundary、Linked SwRS、Task hint、Evidence、Status
- [ ] **软件接口表**列：SWA-IF ID、Type、**Direction**、Counterpart、Protocol、Linked components、Linked SwRS、Evidence、Status
- [ ] **分配矩阵**列：SwRS ID、SWA-COMP ID、Allocation type、Rationale、Interface impact、Status
- [ ] 缺口 L2 标 `evidence: pending`，无材料不得标 `complete`
- [ ] `outline_l1.md` 与 `template_structure.json` 一致

### From-Scratch 专属 Checklist

- [ ] 无 source 的 L2 全部 `evidence: pending`
- [ ] 分配矩阵可零行，但列定义必须完整
- [ ] 不设 SEC-DIFF（除非另有纯形状 sample）
- [ ] SEC-SAFE-ARCH 通常 pending 占位

### With-Reference 专属 Checklist

- [ ] L1 含 **SEC-DIFF**
- [ ] SEC-DIFF L2 列：Ref ID / Project ID / Δ Type / Δ Description / Project Evidence
- [ ] Δ Type 枚举：Added / Removed / Modified / Scope-changed
- [ ] 历史 SwAD 内容 **未**进入大纲正文或表内预填数据
- [ ] 可借参考的章节顺序/图类型，但槽位仍为 pending 或待 EVD

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 大纲完整性 | 无材料 L2 不得 complete | 形状可借参考，正文槽位 pending |
| Direction 列 | 接口表强制存在 | 不得继承参考方向数据 |
| 文档纯净性 | 无 HARA/详细设计章 | 无参考安全/设计章渗入 |
| SEC-DIFF | 通常无 | **必须**存在且列完整 |

### P0 失效项

| 失效 | 后果 |
|---|---|
| 接口表无 Direction 列 | 后续集成/VC 失败 |
| 含 HARA/ASIL/SG/TSR/详细设计/代码 L1/L2 | 文档类型漂移 |
| 历史 SwAD 正文抄进大纲 | 事实来源违规 |
| With-Reference 缺 SEC-DIFF L2 | Δ 分析无法执行 |

### P1 失效项

- Layer 列未定义或枚举不全
- SEC-VERIF 无验证方法槽位
- outline 与 template_structure.json 字段不一致

### 一句话归纳

**Checklist 核心**：SWE.2 核心章齐全、三表列完整（含 Direction）、无越权章、无未证据化正文。  
**Review 核心**：From-Scratch 查 pending 诚实；With-Reference 查 SEC-DIFF 与参考正文隔离。

## A1 / A2 / B

**A1**：L1 覆盖 SWE.2；三表列齐全；With-Reference 含 SEC-DIFF。  
**A2**：补 L2、对齐 JSON。  
**B**：大纲仅为槽位，不含未证据化事实。
