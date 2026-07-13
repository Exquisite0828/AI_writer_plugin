# Software Architecture 子 skill · Step 8 · 审查

骨架：`skills/workflow-steps/step-review/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点

- 对照 template、SWE.2 checklist、证据审查 `draft/full_draft.md`。
- 产出 `review/*`（findings、checklist 结果）。
- 审查结论为 **review-ready 评估**，**不等于** ASPICE 评估通过或软件架构正式批准。

## Software Architecture 方法论（本步定位）

### 8.1 本步在八阶段方法链中的位置

本步对应 **阶段 6：审查与验证** 中的 **内容审查**（软件架构师 / 软件工程师视角）。

**方法原则**：审查不是「把 open 关掉」，而是验证：(1) 有证据的写得对；(2) 没证据的标得诚实；(3) 没有越权内容。

### 8.2 阶段 6 · 内容审查方法

#### ASPICE SWE.2 七维审查法

| 维度 | SWE.2 意图 | 审查章节 | 审查动作 |
|---|---|---|---|
| D1 静态架构完整性 | 组件与分层定义完整 | SEC-LOGARCH、SEC-COMP | 每个逻辑块有组件落点或 open |
| D2 动态架构完整性 | 任务/调度/模式可理解 | SEC-PHYSARCH、SEC-RES | 任务表有来源或 open |
| D3 接口完整性 | 软件元素间接口明确 | SEC-IF | Direction、对端、类型齐全或 open |
| D4 追溯一致性 | SwRS ↔ 架构双向可追溯 | SEC-UPTRACE、SEC-ALLOC | 每条 SwRS 有分配或 orphan 说明 |
| D5 逻辑-物理一致 | 逻辑块与战术落地不矛盾 | LOGARCH vs PHYSARCH | 交叉比对术语与组件名 |
| D6 约束一致性 | 资源/诊断与架构一致 | SEC-DIAG、SEC-RES | 预算与诊断链有 source |
| D7 边界纯净性 | 无越权内容 | 全文 | 无 HARA/TSR/详细设计/批准措辞 |

#### 内容审查 12 项（执行清单）

| # | 检查项 | 通过条件 |
|---|---|---|
| 1 | 文档目的与范围 | 声明非 HARA/TSC/详细设计、非批准 |
| 2 | 输入 role 正确 | sample 未当事实 |
| 3 | 软件上下文 | 分层/边界与 source 一致或 open |
| 4 | SwRS 摘要 | SWR-F/IF 映射可见或 open |
| 5 | 逻辑架构 | 分解清晰、职责单一 |
| 6 | 物理/战术架构 | 组件/任务/BSW 一致 |
| 7 | 组件清单 | ID、Layer、职责、Linked SwRS 齐全 |
| 8 | 软件接口 | Direction、Counterpart、类型齐全或 open |
| 9 | 分配矩阵 | SwRS→组件可解释或 open |
| 10 | 诊断/资源 | 有来源或 open |
| 11 | SEC-SAFE-ARCH | 仅引用，不新分析 |
| 12 | Forbidden claims | 无批准/合规/量产措辞 |

#### From-Scratch 审查重点

- **gap 诚实性**：缺章、空表、大量 open 不应被判为失败（除非 P0 违规）。
- **静默填值检测**：重点查 COMP/IF/ALLOC/RES 是否有无 EVD 的 confirmed 行。
- **不降低 open 密度**：review 不得建议「为通过而关闭 open」。

#### With-Reference 审查重点

- **SEC-DIFF 存在性**：缺则 P0 建议。
- **参考污染检测**：COMP/IF/ALLOC 的 Evidence source 是否含历史 SwAD file_id。
- **Δ 质量**：每行是否有本项目 evidence；是否仅写「同参考」。
- **差异覆盖**：Added/Removed/Modified/Scope-changed 是否检视。

### 8.3 审查产出

- `review/review_report.json`：每项 D1–D7 + 12 项结论。
- findings 分级：P0（阻断）/ P1（应修）/ P2（建议）。
- P0 交 Step 10 修订；无法修则保持 open 并记录。

## 本步 Review / Checklist 要点

### ASPICE SWE.2 BP1–BP7 完整对照 Checklist

| BP | 章节 / 维度 | 审查重点 |
|---|---|---|
| **BP1**：静态架构规格 | SEC-LOGARCH、SEC-COMP、SEC-IF | 组件、Layer、接口、Direction、边界有来源或 open |
| **BP2**：动态架构规格 | SEC-PHYSARCH、SEC-RES | 任务/调度/模式、资源预算有来源或 open |
| **BP3**：架构分析 | SEC-VERIF、全文一致性 | 验证候选记录；逻辑-物理一致；无冲突未记 open |
| **BP4**：架构开发 | SEC-COMP、SEC-ALLOC | 分配可解释；组件职责与 SwRS 对齐 |
| **BP5**：双向追溯 | SEC-UPTRACE、SEC-ALLOC | SwRS↔SWA-COMP 双向；orphan 显式 |
| **BP6**：SwRS 与架构一致 | SEC-UPTRACE、SEC-ALLOC、SEC-IF | 无无来源架构决策；接口与 SWR-IF 一致或 open |
| **BP7**：沟通约定架构 | SEC-SCOPE、SEC-OPEN、SEC-REVIEW | 范围清楚；open 完整；非批准措辞 |

### ISO 26262-6 内容审查 Checklist

- [ ] SEC-SAFE-ARCH（若有）仅为 TSR/软件安全 **显式引用**，无新 HARA/ASIL 分析
- [ ] 无 hazard / S/E/C / ASIL / Safety Goal / TSR(新编) / 安全机制终稿字样
- [ ] 软件架构内容 **足以**作为下游详细设计输入（组件、接口、约束），但 **不含**详细设计本身
- [ ] 若上游有 TSR：架构引用与 TSR 不冲突；冲突显式 SEC-OPEN
- [ ] 无「故障探测已充分」「安全完整性已满足」类未证据化断言

### SwAD 内容审查 16 项 Checklist

| # | 检查项 | 通过条件 |
|---|---|---|
| 1 | 文档目的与范围 | 声明非 HARA/TSC/详细设计、非批准 |
| 2 | 输入材料 role | sample/reference 未当事实 |
| 3 | writing_scenario | 与 manifest 一致 |
| 4 | 软件上下文 SEC-SWCTX | 分层/边界与 source 一致或 open |
| 5 | SwRS 摘要 SEC-UPTRACE | SWR-F/IF 映射可见或 open |
| 6 | SWA-COMP 唯一 ID | 每条有 ID，规则一致 |
| 7 | SWA-COMP → SwRS 追溯 | 每条链 ≥1 SwRS 或 open |
| 8 | SWA-IF Direction 与对端 | Direction、Counterpart 齐全或 open |
| 9 | 分配矩阵 SEC-ALLOC | 每条 SwRS 有组件或 orphan；Rationale 有来源或 open |
| 10 | 逻辑-物理一致 | LOGARCH 与 PHYSARCH 不矛盾 |
| 11 | 诊断/资源 SEC-DIAG/RES | 有来源或 open；数值带单位 |
| 12 | SEC-SAFE-ARCH（若有） | 仅引用，无新安全分析 |
| 13 | 验证方法 SEC-VERIF | 候选或 open，无「已充分验证」 |
| 14 | SwAD 纯净性 | 无 HARA/ASIL/SG/TSR/详细设计/代码 |
| 15 | 开放项 SEC-OPEN | NEEDS_USER_CONFIRMATION 完整汇总 |
| 16 | Forbidden claims | 无批准/ASPICE 合规/ISO 合规/量产措辞 |

### 内容审查 10 维度表（架构师/同行视角）

| 维度 | Review 要点 |
|---|---|
| 与 SwRS 一致 | 组件/接口/分配是否与 SwRS 一致；有无无来源决策 |
| 与系统架构一致 | SEC-SWCTX 与当前项目 System Architecture 边界一致 |
| 接口完整性 | 名称、Type、**Direction**、Counterpart、协议、边界齐全或 open |
| 逻辑-物理一致 | 逻辑块名与战术组件/任务映射一致 |
| 分配可解释性 | Rationale 可追溯到 SwRS 或 HITL |
| 资源来源 | 内存/栈/周期/CPU 有 EVD 或 open |
| 诊断链路 | 检测→上报→降级在组件层明确或 open |
| 证据匹配 | critical claim 有 T0/T1；citation 可到 L3 |
| 缺口诚实性 | open 未被 review 建议「关闭」 |
| 文档边界 | review-ready，非合规认证或正式批准 |

### From-Scratch 专属 Checklist

- [ ] gap 诚实：缺章/空表/大量 open **不**判为失败（除非 P0）
- [ ] 静默填值检测：COMP/IF/ALLOC/RES 无 EVD 却 confirmed → P0
- [ ] 大量 `NEEDS_USER_CONFIRMATION` 不被建议批量关闭
- [ ] SEC-OPEN 数量与 matrix 中 open 一致

### With-Reference 专属 Checklist

- [ ] SEC-DIFF **必存**（缺即 **P0** 建议）
- [ ] SEC-DIFF ≥1 行且具体到组件/接口/资源差异
- [ ] COMP/IF/ALLOC 的 Evidence source **不含**历史 SwAD file_id
- [ ] 客户「沿用参考」须 HITL ID，非参考 SwAD 引用
- [ ] Δ 四类 Added/Removed/Modified/Scope-changed 已检视
- [ ] 参考边界与 task_brief 声明一致

### P0 失效项

| 失效 | 后果 |
|---|---|
| sample/历史 SwAD 支撑 critical claim | 事实来源违规 |
| 组件/分配无上游且 confirmed | 不可追溯 |
| HARA/ASIL/SG/TSR/详细设计/代码 章节或字段 | 文档类型漂移 |
| 接口无 Direction 且 confirmed | 集成困难 |
| 「架构已批准/ASPICE 合规/ISO 26262 compliant/可量产」 | 越权结论 |
| With-Reference 无 SEC-DIFF 或仅「同参考」 | Δ 未管理 |
| SEC-SAFE-ARCH blanket 引用全部 TSR | 安全边界错误 |

### P1 失效项

- 逻辑-物理术语不一致
- 分配矩阵缺 Rationale 列内容
- 资源数值缺单位
- SEC-VERIF 无候选/status 标注
- TASK 周期与 SEC-RES 矛盾无 SEC-OPEN

### 双情景 Review 重点对比

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 审查重点 | gap 诚实；open 未被掩盖 | 参考 SwAD 是否渗入事实表 |
| Direction | 缺则强求 open | 不得继承参考方向 |
| SEC-DIFF | — | **必查**具体性；缺建议 P0 |
| SEC-SAFE-ARCH | 多 open 可接受 | 不可抄参考安全引用 |
| 完整性 | 不得越权「批准」 | Δ 不得把参考当本项目结论 |

### 一句话归纳

**Checklist 核心**：BP1–BP7 全覆盖、16 项内容审查、三表可追溯、Direction 强制、无安全/设计/批准泄漏。  
**Review 核心**：与 SwRS/系统架构一致、tier 合规、open 诚实、With-Reference 必有具体 SEC-DIFF。

## A1 / A2 / B

**A1**：16 项 checklist 有结论；ASPICE BP1–BP7 全部覆盖；P0 无遗漏。  
**A2**：按 findings 编修订单交 Step 10。
**B**：review 非 sign-off；状态 `passed_with_open_items` 或 `failed`。
