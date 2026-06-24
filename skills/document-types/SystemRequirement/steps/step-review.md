# SyRS 子 skill · Step 10 · 审查

骨架：`skills/workflow-steps/step-review/SKILL.md`。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点

- 对照 template、checklist、证据审查 `draft/full_draft.md`。
- 产出 `review/*`。
- 审查结论为 **review-ready 评估**，**不等于** ASPICE 评估通过或 SyRS 正式批准。

## SyRS 方法论（本步定位）

本步对应 **阶段 6：审查与验证** 中的 **内容审查**（系统工程师/同行视角）。

### ASPICE SYS.2 三类评审对齐

| 评审类型 | 关注点 | 本步对应检查 |
|---|---|---|
| **干系人需求分析**（BP1） | SWRS/RFQ 是否被分析并映射 | SEC-STAKE、SEC-TRACE |
| **系统需求规格**（BP2） | SYS-F/IF 是否结构化、可验证 | SEC-FUNC、SEC-IF |
| **需求分析**（BP3） | 一致性、可行性、可测试性 | 全文一致性、验证方法 |
| **双向追溯**（BP5） | 上游↔SyRS | SEC-TRACE |

### 阶段 6 · 内容审查（本步执行）

1. 每条 SYS-F/IF 是否链到上游 SWRS/RFQ？
2. 接口是否含**方向**与对端？
3. 性能/环境/诊断限值是否来自 source/HITL？
4. sample/reference 是否被误当事实？
5. 是否有 **HARA/ASIL/SG/TSR 泄漏**？
6. 完整性/充分性是否被越权「批准」？

### 要回答的问题（审查核对）

| 问题 | 通过条件 |
|---|---|
| 每条 SYS-xx 是什么？ | shall 表述清晰，有来源或 open |
| 追溯到哪个上游需求？ | Linked upstream ID 有效 |
| 接口方向与对端？ | Direction/Counterpart 有效或 open |
| 如何验证？ | 候选或已确认，非静默充分 |
| 还缺什么？ | open 完整 |

## 本步 Review / Checklist 要点

### ASPICE SYS.2 BP1–BP5 完整对照 Checklist

| BP | 章节 / 维度 | 审查重点 |
|---|---|---|
| **BP1**：干系人需求分析 | SEC-STAKE | 客户/法规/约束需求是否被识别、摘要、映射；每条有上游 ID |
| **BP2**：系统需求规格 | SEC-FUNC / SEC-IF / SEC-PERF / SEC-ENV / SEC-DIAG / SEC-SAFE | 结构化、shall、单条单义、可验证、含 source |
| **BP3**：需求分析 | SEC-VERIF + 全文一致性 | 一致性（无冲突）、可行性、可测试性记录 |
| **BP4**：与干系人沟通 | SEC-OPEN | OEM/客户 open 项记录、待确认通信项 |
| **BP5**：双向追溯 | SEC-TRACE | 上游↔SyRS 双向；缺向必须显式 open |

### SyRS 内容审查 14 项 Checklist

| # | 检查项 | 通过条件 |
|---|---|---|
| 1 | 文档目的与范围 | 声明非 HARA/FSR/TSC/SwRS、非批准 |
| 2 | 输入材料 role | sample / reference 未当事实 |
| 3 | ECU / 产品标识 | 与 source 一致或 open |
| 4 | 干系人需求摘要（BP1） | SWRS/RFQ 映射可见或 open |
| 5 | SYS-F 唯一 ID | 每条有 ID，编号规则一致 |
| 6 | SYS-F → 上游追溯（BP5） | 每条链到 ≥1 上游 ID 或 open |
| 7 | SYS-IF 方向与对端 | Direction、Counterpart 齐全或 open |
| 8 | 性能 / 环境 / 诊断 | 限值有来源或 open |
| 9 | SEC-SAFE（若有） | 仅引用 FSR/SG，无新 HARA |
| 10 | 追溯矩阵双向（BP5） | 上游↔SyRS 双向；缺向显式 open |
| 11 | 验证方法（BP3） | 候选或已确认，无静默「已充分」 |
| 12 | SyRS 纯净性 | 无 HARA/ASIL/SG/TSR/TSC/SwRS 终稿 |
| 13 | 开放项（BP4） | NEEDS_USER_CONFIRMATION 完整、SEC-OPEN 汇总 |
| 14 | Forbidden claims | 无批准 / ASPICE 合规 / ISO 合规措辞 |

### 内容审查 9 维度表（同行/系统工程师视角）

| 维度 | Review 要点 |
|---|---|
| 与需求一致 | SYS-F/IF 是否与 SWRS/RFQ 一致；有无无来源的需求 |
| 与架构一致 | 边界与系统架构/子系统划分一致；无越界需求 |
| 接口完整性 | 名称、类型、**方向**、对端、信号、失效行为齐全 |
| 边界双向性 | SEC-IF 是否同时覆盖 In / Out / Bidirectional |
| 限值来源 | 性能/环境/诊断数字均有 source 或 open，无 sample 支撑 |
| 工况事实性 | 工况描述为事实，未做 E 评级或危害推断 |
| 证据匹配 | critical claim 有 T0/T1 证据；citation 可追溯到 L3 |
| 缺口诚实性 | 缺证据保留 `NEEDS_USER_CONFIRMATION` / `[PENDING]` |
| 文档边界 | 审查结论是 review-ready，非合规认证或正式批准 |

### 写作语言规范 Review

- [ ] 每条需求使用 **shall / 应**；无模糊词（高效、合理、足够、稳定、用户友好）
- [ ] 单条单义；无多重 shall 嵌套
- [ ] 数字含单位
- [ ] 主体明确（ECU / 驾驶员 / OEM 接口），非「系统」泛指
- [ ] 中英文混排时术语一致

### ISO 26262 接口审查 Checklist

- [ ] SEC-FUNC / SEC-IF / SEC-ENV / SEC-DIAG 内容**足以**作为下游 IDD 输入（功能、边界、接口、工况、约束）
- [ ] SEC-SAFE 内容仅为 FSR/SG 显式引用，**不**新做 HARA
- [ ] 若上游已有 FSR：SYS-F/IF 与 FSR 不冲突；有冲突显式登记 SEC-OPEN
- [ ] 无 hazard / S/E/C / ASIL / Safety Goal / safe state(新) / TSR 字样

### From-Scratch 专属 Checklist

- [ ] gap 是否诚实：缺章节直接 open，未用 reference 填
- [ ] 大量 `NEEDS_USER_CONFIRMATION` 不应被 review「关闭」
- [ ] SEC-OPEN 总数与 critical claim 中 `NEEDS_USER_CONFIRMATION` 一致

### With-Reference 专属 Checklist

- [ ] SEC-DIFF 必存（缺即 **P0** 建议）
- [ ] SEC-DIFF 至少一行，且**具体到接口/限值/工况**
- [ ] SYS-F/IF / SEC-PERF / SEC-ENV / SEC-DIAG 的 Evidence source 列**不含**参考 SyRS file_id
- [ ] 客户已确认「沿用」的需求须 HITL ID 而非参考 SyRS 引用
- [ ] 平台/变型差异类别（新增 / 删除 / 修改 / 范围变化）齐全

### P0 失效项

| 失效 | 后果 | 级别 |
|---|---|---|
| sample / 参考 SyRS 支撑 SYS-xx / 限值 | 事实来源违规 | P0 |
| SYS-xx 无上游链接且标已确认 | 不可追溯 | P0 |
| 含 HARA / ASIL / SG / TSR 章节或字段 | 文档类型漂移 | P0 |
| SYS-IF 无 Direction 且标已确认 | 集成/架构困难 | P0 |
| 写「SyRS 已批准 / ASPICE 合规 / ISO 26262 compliant / 可量产」 | 越权结论 | P0 |
| reference 证明本项目需求 | tier 违规 | P0 |
| With-Reference 无 SEC-DIFF 或仅写「同参考」 | 变型差异未管理 | P0 |
| SEC-SAFE blanket 引用全部 FSR/SG | 安全边界错误 | P0 |

### P1 失效项

- 追溯矩阵反向（SyRS→上游）列空白且无 open
- 验证方法无 status 列
- SEC-STAKE 与 SEC-FUNC 需求冲突无 SEC-OPEN 记录
- 边界仅 In 缺 Out 说明
- 模糊词混入需求语句
- 接口失效行为未记

### 双情景 Review 重点对比

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 审查重点 | gap 是否诚实，open 是否被掩盖 | 参考 SyRS 是否渗入 SYS-F/IF 事实 |
| Direction | 缺则强求 open，不得静默 | 同上；不得继承参考 SyRS |
| SEC-DIFF | — | **必查具体性**；缺即建议 P0 |
| SEC-SAFE | 多 open 可接受 | 不可抄参考 SyRS 的 SEC-SAFE 引用 |
| 完整性 | 不得越权「批准」 | Δ 节不得把参考当本项目结论 |

### 一句话归纳

**Checklist 核心**：每条 SYS-xx 链上游、接口有方向、验证显式、追溯双向、无 HARA/TSR、无批准措辞。  
**Review 核心**：与 SWRS/架构一致、tier 合规、sample 未当事实、缺口显式、结论不越权批准、With-Reference 必有具体 Δ。

## A1 / A2 / B

**A1**：14 项 checklist 有结论；ASPICE BP1–BP5 全部覆盖；P0 无遗漏。  
**A2**：按 findings 编修订单交 Step 12。  
**B**：review 非合规批准；状态 `passed_with_open_items` 或 `failed`。
