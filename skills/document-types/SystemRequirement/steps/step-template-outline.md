# SyRS 子 skill · Step 4 · 模板大纲

骨架：`skills/workflow-steps/step-template-outline/SKILL.md`。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点

### 阶段 A · L1

- 读 task_brief、SyRS template（T2）、sample SyRS（T4，仅形状）。
- 产出 `outline_l1.md` + `template_structure.json`。
- **不写** SyRS 正文；**不含** HARA/FSR/TSC/SwRS 章。

### 阶段 B · L2

- SEC-STAKE：干系人需求摘要表
- SEC-FUNC：SYS-F-xx 功能需求表
- SEC-IF：SYS-IF-xx 接口需求表（**含方向列**）
- SEC-PERF / SEC-ENV / SEC-DIAG：性能、环境、诊断表
- SEC-TRACE：追溯矩阵（SWRS↔SyRS）
- 缺口 L2 标 `evidence: pending`

## SyRS 方法论（本步定位）

本步对应 **阶段 2：定大纲（先 L1，后 L2）**——落实 ASPICE SYS.2 与控制器 SyRS 典型结构。

### 报告建议结构（章节）

| 章节 | 内容要点 | 标准关联 |
|---|---|---|
| 文档目的与范围 | 读者、适用 ECU、**不含 HARA/TSC/批准** | SYS.2 |
| 输入材料与假设 | 输入清单、source 边界 | 可追溯 |
| ECU/产品标识 | 名称、Part No、变型 | — |
| 干系人需求摘要 | SWRS/RFQ 映射入口 | SYS.2 BP1 |
| **功能需求 SYS-F-xx** | **核心交付物** | SYS.2 BP2 |
| **接口需求 SYS-IF-xx** | 含方向、对端 | SYS.3 输入 |
| 性能与实时性 | 时序、精度、带宽 | — |
| 环境与运行约束 | 温度、电压、EMC | — |
| 诊断与降级 | DTC、降级模式（系统层） | — |
| 安全相关系统需求 | **引用** FSR/SG，非 HARA | ISO 26262 接口 |
| 需求追溯矩阵 | 上游↔SyRS↔下游预留 | SYS.2 BP5 |
| 验证方法候选 | 建议验证方式 | SYS.2 BP3 |
| 假设、限制与开放确认 | 缺口、NEEDS_USER_CONFIRMATION | — |
| 审查摘要 | 非专业批准 | — |

### 强制 L1（section_id）

| section_id | 标题 | 强制 |
|---|---|:---:|
| SEC-SCOPE | 目的、范围与读者 | ★ |
| SEC-INPUT | 输入材料与 source 边界 | ★ |
| SEC-IDENT | ECU/产品标识 | ★ |
| SEC-STAKE | 干系人需求摘要 | ★ |
| SEC-FUNC | 功能需求 SYS-F-xx | ★ |
| SEC-IF | 接口需求 SYS-IF-xx | ★ |
| SEC-PERF | 性能与实时性 | ★ |
| SEC-ENV | 环境与运行约束 | ★ |
| SEC-DIAG | 诊断与降级 | ★ |
| SEC-TRACE | 需求追溯矩阵 | ★ |
| SEC-VERIF | 验证方法候选 | ★ |
| SEC-ASSUMP | 假设与依赖 | ★ |
| SEC-REVIEW | 审查总结 | ★ |

### SYS-F 需求表建议列（L2 须定义）

| 列 | 说明 |
|---|---|
| SYS-F ID | 唯一标识 |
| Requirement statement | 具体、可验证 shall 表述 |
| Linked upstream ID | 关联 SWRS/RFQ ID |
| Priority | Must/Should 或项目分级 |
| Verification method | 验证方法候选 |
| Evidence source | T0/T1 来源 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

### SYS-IF 接口表建议列（L2 须定义）

| 列 | 说明 |
|---|---|
| SYS-IF ID | 唯一标识 |
| Interface name | 接口名称 |
| Type | CAN/LIN/机械/电源/HMI 等 |
| Direction | In / Out / Bidirectional（**强制**） |
| Counterpart | 对端 ECU/模块/驾驶员 |
| Requirement statement | 可验证表述 |
| Linked upstream ID | 上游追溯 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

**禁止**：HARA、ASIL、SG、TSR、TSC、SwRS 终稿 L1/L2。

## 本步 Review / Checklist 要点

### 通用 Checklist（每次 run 必查）

- [ ] **强制 L1** 齐全：SCOPE、INPUT、IDENT、STAKE、FUNC、IF、PERF、ENV、DIAG、TRACE、VERIF、ASSUMP、REVIEW（其余为 optional）
- [ ] L1 章节顺序与上游 ASPICE SYS.2 / 公司 SyRS 模板一致
- [ ] **大纲不含正文**；L2 仅声明小节与表格列定义
- [ ] **无** HARA / ASIL / SG / TSR / TSC / SwRS / HwRS 章节（**P0**）
- [ ] 缺口 L2 标 `evidence: pending` 且关联 `knowledge_gaps`
- [ ] `template_structure.json` 与 `outline_l1.md` / `outline_l2.md` 一致
- [ ] SEC-OPEN 节点存在，用于汇总 NEEDS_USER_CONFIRMATION

### SEC-STAKE 表列定义 Checklist（ASPICE SYS.2 BP1）

| 列 | 通过条件 |
|---|---|
| Customer Req ID | 客户原始 ID，唯一 |
| Description | 客户需求摘要（保留原文或翻译） |
| Source | 文档 file_id + L3 location |
| Priority | Must / Should / Nice-to-have（来自 source） |
| Affects (SYS-F/IF) | 候选映射本项目 SYS-xx |
| Status | analyzed / pending / NEEDS_USER_CONFIRMATION |

### SYS-F 功能需求表列定义 Checklist（ASPICE SYS.2 BP2）

| 列 | 通过条件 |
|---|---|
| SYS-F ID | 唯一，命名规则在 task_brief 固定 |
| Requirement statement | shall 句式、单条单义、可验证 |
| Linked upstream ID | 至少 1 个 Customer Req ID 或 HITL ID（或 open） |
| Priority | Must / Should |
| Verification method | Test / Review / Analysis / Inspection（候选） |
| Allocated to (optional) | 下游架构元素槽位（pending OK） |
| Evidence source | file_id + L3 location |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

### SYS-IF 接口需求表列定义 Checklist（**强制 Direction 列**）

| 列 | 通过条件 |
|---|---|
| SYS-IF ID | 唯一 |
| Interface name | 名称 |
| Type | CAN / LIN / FlexRay / Ethernet / 机械 / 电源 / HMI / 诊断 |
| **Direction** | **In / Out / Bidirectional**，**P0** 不得空白 |
| Counterpart | 对端 ECU / 模块 / 驾驶员 / 物理实体 |
| Signal/message | 信号或报文标识 |
| Requirement statement | 可验证，含失效/超时/范围（若 source 有） |
| Failure behavior | 信号失效时系统层行为（或 open） |
| Linked upstream ID | 上游 ID |
| Evidence source | file_id + L3 location |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

### SEC-PERF / SEC-ENV / SEC-DIAG 表列建议

- **SEC-PERF**：ID / 指标（时序/精度/带宽） / 限值 / 工况 / Source / Status
- **SEC-ENV**：ID / 维度（温度/电压/EMC/振动） / 范围 / 适用工况 / Source / Status
- **SEC-DIAG**：ID / DTC 或事件 / 检测条件 / 降级行为 / Source / Status（**仅系统层**，不写 DTC 实现）

### SEC-TRACE 矩阵 Checklist（ASPICE SYS.2 BP5）

| 列 | 通过条件 |
|---|---|
| Upstream ID（SWRS/RFQ/HITL） | 唯一 |
| SyRS ID（SYS-F / SYS-IF / SYS-PERF…） | 至少 1 个或 open |
| Direction (Upstream→SyRS) | 双向追溯需另列 SyRS→Upstream |
| Down­stream slot（架构 / IDD / FSR） | 可 pending |
| Trace status | full / partial / orphan |

### SEC-SAFE Checklist（若有 FSR/SG 输入）

- [ ] SEC-SAFE 仅作 **引用** 节，列：FSR/SG ID、表述摘要、对应 SYS-F/IF、Source、Status
- [ ] **不**新增 hazard / S/E/C / ASIL / Safety Goal 列
- [ ] 与 SEC-FUNC / SEC-IF 的对应关系显式

### SEC-DIFF（仅 With-Reference）Checklist

- [ ] L1 含 **SEC-DIFF**（或 SEC-DELTA）章
- [ ] 列定义：参考 ID / 本项目 ID / 差异类型（Added / Removed / Modified / Renamed / Scope-changed） / 差异说明 / 证据来源（本项目 source） / Status
- [ ] **不得**在 SEC-DIFF 之外让参考 SyRS 内容出现在 SYS-F/IF 等事实表中
- [ ] task_brief 平台/变型差异类别均预留 SEC-DIFF 行槽位

### 通用大纲 Forbidden Checklist

- [ ] 大纲**不得**含 SEC-HAZ、SEC-HE、SEC-SEC（S/E/C）、SEC-ASIL、SEC-SG、SEC-TSR、SEC-MECH、SEC-SWREQ、SEC-HWREQ
- [ ] 大纲**不得**包含「合规结论」「批准结论」等节标题
- [ ] 文档信息节不写 "Approved by"、"Compliant"，仅写 "Reviewed by / Status: draft|ready_for_human_review"

### ASPICE / ISO 26262 维度对照 Checklist

| 标准维度 | 大纲承接位置 |
|---|---|
| ASPICE SYS.2 BP1（客户/干系人需求分析） | SEC-STAKE |
| ASPICE SYS.2 BP2（系统需求规格） | SEC-FUNC / SEC-IF / SEC-PERF / SEC-ENV / SEC-DIAG |
| ASPICE SYS.2 BP3（需求分析） | SEC-REVIEW 评审记录占位、SEC-VERIF |
| ASPICE SYS.2 BP4（通信） | SEC-OPEN（含与 OEM 的 open 项） |
| ASPICE SYS.2 BP5（双向追溯） | SEC-TRACE |
| ISO 26262-3 §5（下游 IDD 输入） | SEC-FUNC / SEC-IF / SEC-ENV / SEC-DIAG 提供事实 |
| ISO 26262-3 §7（FSR 接口） | SEC-SAFE 引用 |
| ISO 26262-4（TSC/系统设计接口） | SEC-TRACE 预留下游列；**不**写 TSC 章 |

### 本步 Review 要点（双情景对比）

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 大纲完整性 | 无材料 L2 不得标 complete | 形状可借参考 sample，但**正文槽位**仍 pending 到有 EVD |
| SYS-IF Direction | 强制列存在 | 同上；不得继承参考 SyRS 的方向数据 |
| SEC-SAFE | 通常 open | 不得抄参考 SyRS 的 SEC-SAFE 内容 |
| SEC-DIFF | 不存在 | **必须存在**且列定义齐全 |
| 法规章 | 按 source 决定是否纳入 L1 | 不得直接继承参考 SyRS 的法规列表 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 大纲含 HARA / ASIL / SG / TSR 章 | 文档类型漂移（**P0**） |
| SYS-IF 无 Direction 列 | 后续 SYS.3/集成困难（**P0**） |
| 参考 SyRS 需求/接口/限值抄进大纲正文 | 事实来源违规（**P0**） |
| 强制 L1 缺 SEC-TRACE / SEC-STAKE | ASPICE SYS.2 BP1/BP5 不可满足 |
| With-Reference 无 SEC-DIFF | 变型差异不可管理 |

### 常见 P1

- SYS-F 表无 Verification method 列
- SEC-TRACE 列定义只覆盖上游→SyRS 单向
- 模板版本号未在 SEC-DOC 强制
- SEC-OPEN 占位缺失

## A1 / A2 / B

**A1**：L1 覆盖 SYS.2 章；无 HARA/TSC；SYS-F/IF 表列完整；With-Reference 含 SEC-DIFF。  
**A2**：补 L2、对齐 JSON/outline、修正缺列。  
**B**：三 artifact 一致；sample 未升格事实；下游 IDD/FSR 接口槽位预留。
