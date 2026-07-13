# SyRS 子 skill · Step 7 · 保守草稿

骨架：`skills/workflow-steps/step-conservative-draft/SKILL.md`。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点

- 按 `section_tasks.json` 成稿 → `draft/full_draft.md`。
- 只用 `allowed_evidence`；核对 L1→L2→L3→原文。
- **禁止**：HARA、ASIL、SG、TSR、TSC、SwRS 终稿、ASPICE/ISO 合规措辞。

## SyRS 方法论（本步定位）

本步对应 **阶段 5：保守成稿**。

### 阶段 5 · 撰写（本步执行）

| 节 | 写法要点 |
|---|---|
| SEC-STAKE | SWRS/RFQ 需求摘要；每条有上游 ID |
| SEC-FUNC | 每条 SYS-F：shall 表述、**Linked upstream ID**、验证方法候选 |
| SEC-IF | 每条 SYS-IF：**Direction**、Counterpart、可验证表述 |
| SEC-PERF | 性能/时序限值有 source 或 open |
| SEC-ENV | 温度、电压、EMC 等有来源或 open |
| SEC-DIAG | 诊断/降级系统层表述；非 DTC 实现细节终稿 |
| SEC-SAFE | **仅引用** FSR/SG source；不做 HARA |
| SEC-TRACE | SWRS↔SyRS 追溯矩阵；下游架构列可 pending |
| SEC-VERIF | 验证方法标 **候选** 或 open |

### 成功标准（成稿视角）

- 每条 SYS-F/IF 有唯一 ID，且追溯到 source 中上游需求（或 open）。
- 接口含方向与对端；无 sample/reference 支撑。
- 验证方法标候选/待确认，除非 source/HITL 明确支持。
- 需求措辞有来源或显式 open。
- **无 HARA/ASIL/SG/TSR/TSC/SwRS**；无 forbidden final claims。

### SYS-F 表字段（成稿必查）

| 列 | 通过条件 |
|---|---|
| SYS-F ID | 唯一 |
| Requirement statement | shall、可验证；无危害新结论 |
| Linked upstream ID | 至少一个 SWRS/RFQ ID 或 open |
| Verification method | 候选或已确认，非静默「已充分」 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

### SYS-IF 表字段（成稿必查）

| 列 | 通过条件 |
|---|---|
| SYS-IF ID | 唯一 |
| Direction | In/Out/Bidirectional 有来源或 open |
| Counterpart | 对端明确或 open |
| Requirement statement | 可验证；含失效/超时行为（若 source 有） |

### 重要边界

- **SyRS ≠ HARA/FSR**：不写危害、ASIL、SG 新结论
- **SyRS ≠ TSC/SwRS**：不写技术安全机制或软件需求终稿
- **禁止**：SyRS approved、ASPICE SYS.2 satisfied、ISO 26262 compliant 等

## 本步 Review / Checklist 要点

### 通用 Checklist（每次 run 必查）

- [ ] 每个 TASK 的 `outputs` 都落到 `draft/full_draft.md` 对应 L2，无遗漏
- [ ] 每条需求语句使用 **`shall`** 句式（中文 SyRS 可用「应」对应），**单条单义**（一句不超过一项行为）
- [ ] 每条需求**可验证**（含可测量/可观察的条件、对象、结果）
- [ ] 缺证据章节使用 `[PENDING]` / `NEEDS_USER_CONFIRMATION` 标记，**不**静默填值
- [ ] 草稿引用的 EVD ID 必须在 `evidence_map.json` 中存在
- [ ] 表格行与 `section_tasks.json` 中的输出条目一一对应

### SYS-F 成稿字段 Checklist

| 列 | 通过条件 |
|---|---|
| SYS-F ID | 唯一，命名一致 |
| Requirement statement | shall + 单条单义 + 可验证；**无**危害/ASIL 新结论 |
| Linked upstream ID | ≥1 个 SWRS/RFQ/HITL ID，或 `NEEDS_USER_CONFIRMATION` |
| Priority | Must/Should，有 source 或 open |
| Verification method | 候选（Test/Review/Analysis/Inspection）或 open |
| Evidence source | EVD 引用 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

### SYS-IF 成稿字段 Checklist（**Direction 强制**）

| 列 | 通过条件 |
|---|---|
| SYS-IF ID | 唯一 |
| Direction | **In / Out / Bidirectional**，**P0** 不得空白；缺则写 `NEEDS_USER_CONFIRMATION` |
| Counterpart | 对端明确或 open |
| Type / Signal | CAN / LIN / Eth / 机械 / HMI 等 |
| Requirement statement | 含范围、超时、失效行为（若 source 有） |
| Failure behavior | 信号失效/丢失时系统层行为或 open |
| Evidence source | EVD 引用 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

### SEC-PERF / SEC-ENV / SEC-DIAG 成稿 Checklist

- [ ] 性能限值：数字 + 单位 + 工况；缺工况标 `NEEDS_USER_CONFIRMATION`
- [ ] 环境限值：温度/电压/EMC/振动至少 1 个有源或显式 open
- [ ] 诊断：仅系统层降级/警示行为；**不**写 DTC 数值实现细节终稿
- [ ] 所有限值有 EVD 或 open；**不**继承 sample / 参考 SyRS 数字（**P0**）

### SEC-SAFE 成稿 Checklist（若有 FSR/SG 输入）

- [ ] SEC-SAFE 行：**仅引用** FSR/SG ID + 对应 SYS-F/IF + source（EVD）
- [ ] **不**新增 hazard / S/E/C / ASIL 列
- [ ] 引用边界明确：只覆盖 fsr_source 中显式列出的 FSR/SG
- [ ] 若无 fsr_source：本节写 "Safety inputs pending"，不编造

### SEC-TRACE 成稿 Checklist（ASPICE SYS.2 BP5）

- [ ] 至少完成 **上游 → SyRS** 单向追溯（必备）
- [ ] **SyRS → 上游** 反向列存在；缺时显式 open
- [ ] 下游列（架构/IDD/FSR）预留 `pending`，不强填
- [ ] 孤儿需求（无上游）显式标 `orphan` 并进 SEC-OPEN

### SEC-DIFF 成稿 Checklist（**仅 With-Reference**，强制存在）

- [ ] SEC-DIFF 表至少含一行；**禁止**只写「同参考」（**P0**）
- [ ] 每行：参考 ID（REF-Fxx） / 本项目 ID（SYS-Fxx） / 差异类型（Added/Removed/Modified/Renamed/Scope-changed） / 差异描述 / **本项目证据来源**
- [ ] 差异描述具体到接口/限值/工况层面，非抽象「优化」
- [ ] 平台/变型差异类别（如「新增网络安全日志」「取消机械备份」）有对应行

### 写作语言规范 Checklist

- [ ] shall / 应：用于强制需求；should / 宜：用于建议；may / 可：用于允许
- [ ] **避免**模糊词：高效、合理、足够、稳定、用户友好
- [ ] **避免**多重 shall 嵌套：「应在 X 时 shall 输出 Y」 → 拆为两条
- [ ] 数字必须含单位
- [ ] 主体明确：「ECU 应…」「驾驶员可…」，非「系统应…」笼统

### Forbidden Content（草稿层 P0 扫描）

- [ ] 草稿**不出现**：hazard、hazardous event、S/E/C、ASIL、Safety Goal、safe state(新)、TSR、TSC、SwRS 表
- [ ] 草稿**不出现**：approved / validated / compliant / ISO 26262 compliant / ASPICE Level X / production ready / risk accepted
- [ ] 不把 reference 中的公司模板措辞直接写为本项目结论

### ASPICE / ISO 26262 维度 Checklist

- [ ] **ASPICE SYS.2 BP1** → SEC-STAKE 表每条 Customer Req ID 有摘要与映射
- [ ] **ASPICE SYS.2 BP2** → SEC-FUNC + SEC-IF + SEC-PERF + SEC-ENV + SEC-DIAG 至少各 1 条或显式 gap
- [ ] **ASPICE SYS.2 BP3** → SEC-VERIF 含可行性/可测试性候选说明，或 open
- [ ] **ASPICE SYS.2 BP5** → SEC-TRACE 完成上游→SyRS
- [ ] **ISO 26262-3 §5 接口** → SEC-FUNC / SEC-IF / SEC-ENV 内容可作 IDD 输入
- [ ] **ISO 26262-3 §7 接口** → SEC-SAFE 仅引用，不分析

### From-Scratch 专属 Checklist

- [ ] 大量 `[PENDING]` / `NEEDS_USER_CONFIRMATION` 正常，不为关闭而填值
- [ ] 接口方向真不明 → `Direction: NEEDS_USER_CONFIRMATION`
- [ ] SEC-SAFE 全章 placeholder 时显式声明「FSR 链上游待提供」
- [ ] 不超出 `allowed_evidence`；EVD 缺则进 SEC-OPEN

### With-Reference 专属 Checklist

- [ ] 参考 SyRS 措辞**不**出现在 SYS-F/IF 表，除非已有本项目 EVD
- [ ] SYS-F/IF 表的 `Evidence source` 列**不**包含参考 SyRS file_id（**P0**）
- [ ] SEC-DIFF 必有具体差异点（见前节）
- [ ] 客户已确认「沿用」时，须 HITL ID 作 source，而非引参考 SyRS

### 本步 Review 要点（双情景对比）

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 编造风险 | 静默填 SYS-xx / 限值 | 参考措辞无 EVD 进表 |
| Direction 列 | 缺则 open | 缺则 open；不得抄参考 SyRS |
| SEC-DIFF | 不存在 | 必存且具体 |
| SEC-SAFE | placeholder 多 | 不抄参考 SyRS |
| 表与 TASK 对齐 | 每行可回溯 TASK ID | 同上 + Δ 行可回溯 TASK-DIFF |

### 常见 P0

| 错误 | 后果 |
|---|---|
| SYS-xx 无上游却标 confirmed | 不可追溯 |
| 含 HARA / ASIL / SG / TSR | 文档类型漂移 |
| SYS-IF 无方向且标已确认 | SYS.3/集成困难 |
| 写「已批准 / ASPICE 合规 / ISO 合规 / 可量产」 | 越权结论 |
| 参考 SyRS 措辞无 EVD 写入正文 | 事实来源违规 |
| 性能/环境限值直接抄 sample 数字 | 事实来源违规 |
| SEC-DIFF 缺失或泛泛（仅 With-Reference） | 变型差异未管理 |

### 常见 P1

- 模糊词混入需求语句
- 多重 shall 嵌套
- 数字缺单位
- SEC-TRACE 反向列空白且无 open
- 验证方法默认 Test 而无理由

## A1 / A2 / B

**A1**：无超出 `allowed_evidence` 的表述；无 HARA/TSC 泄漏；每条 SYS-F 有上游列；SEC-IF 有 Direction。  
**A2**：按 TASK 重跑缺证据节；修正 forbidden / shall 句式 / Direction 缺失。  
**B**：无 forbidden final claims；SEC-DIFF（若 With-Reference）具体且有 EVD。
