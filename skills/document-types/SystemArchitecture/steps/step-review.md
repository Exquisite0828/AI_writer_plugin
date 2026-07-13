# System Architecture 子 skill · Step 8 · 审查

骨架：`skills/workflow-steps/step-review/SKILL.md`。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点

- 对照 template、checklist、证据审查 `draft/full_draft.md`。
- 产出 `review/*`。
- 审查结论为 **review-ready 评估**，**不等于** ASPICE 评估通过或架构正式批准。

## System Architecture 方法论（本步定位）

本步对应 **阶段 6：审查与验证** 中的 **内容审查**（系统架构师 / 系统工程师视角）。

### ASPICE SYS.3 对照 Checklist

| 维度 | 章节 / 关注点 |
|---|---|
| 架构分解 | SEC-LARCH / SEC-PARCH |
| 接口定义 | SEC-IF |
| 需求到元素分配 | SEC-ALLOC |
| 设计约束 | SEC-RES / SEC-DIAG |
| 追溯 | SEC-REQTRACE / SEC-ALLOC |

### 内容审查 12 项 Checklist

| # | 检查项 | 通过条件 |
|---|---|---|
| 1 | 文档目的与范围 | 声明非 HARA/TSC/SwRS/HwRS、非批准 |
| 2 | 输入材料 role | sample / reference 未当事实 |
| 3 | 上下文与边界 | 与 source 一致或 open |
| 4 | 上游需求摘要 | SyRS 映射可见或 open |
| 5 | 逻辑架构 | 分解清晰、职责明确 |
| 6 | 物理架构 | 模块/平台/网络结构一致 |
| 7 | 架构元素清单 | ID、职责、边界、linked requirements 齐全 |
| 8 | 接口架构 | Direction、Counterpart、协议、边界齐全或 open |
| 9 | 分配矩阵 | requirement → element 关系可见或 open |
| 10 | 诊断/降级与资源约束 | 有来源或 open |
| 11 | 安全架构边界 | SEC-SAFE-ARCH 仅引用，不新做分析 |
| 12 | Forbidden claims | 无批准/ASPICE 合规/ISO 合规措辞 |

## 本步 Review / Checklist 要点

### 审查维度表

| 维度 | Review 要点 |
|---|---|
| 与上游需求一致 | 元素/接口/分配是否与 SyRS 一致；有无无来源架构决策 |
| 逻辑-物理一致性 | SEC-LARCH 与 SEC-PARCH 是否矛盾 |
| 元素完整性 | ELEM ID、职责、边界、linked requirements 是否齐全 |
| 接口完整性 | 名称、类型、**方向**、对端、协议、边界是否齐全 |
| 分配合理性 | requirement → element 是否可解释 |
| 资源约束来源 | CPU/内存/总线/时序等是否有 source |
| 诊断链路 | 故障检测 / 上报 / 降级路径是否明确 |
| 证据匹配 | critical claim 有 T0/T1 证据；citation 可追溯到 L3 |
| 缺口诚实性 | 缺证据保留 `NEEDS_USER_CONFIRMATION` / `[PENDING]` |
| 文档边界 | review-ready，非合规认证或正式批准 |

### From-Scratch 专属 Checklist

- [ ] gap 是否诚实：缺章节直接 open，未用 reference 填
- [ ] 大量 `NEEDS_USER_CONFIRMATION` 不应被 review“关闭”

### With-Reference 专属 Checklist

- [ ] SEC-DIFF 必存（缺即 **P0** 建议）
- [ ] 元素/接口/分配 Evidence source 列**不含**参考架构 file_id
- [ ] 平台/变型差异类别（新增 / 删除 / 修改 / 范围变化）齐全

### P0 失效项

| 失效 | 后果 |
|---|---|
| sample / 参考架构支撑元素/接口/分配/资源 | 事实来源违规 |
| 元素 / 分配无上游链接且标已确认 | 不可追溯 |
| 含 HARA / ASIL / SG / TSR 章节或字段 | 文档类型漂移 |
| 接口无 Direction 且标已确认 | 集成 / 分配困难 |
| 写“架构已批准”“ASPICE 合规” | 越权结论 |
| SEC-SAFE-ARCH blanket 引用全部 FSR/TSC | 安全边界错误 |

### P1 失效项

- 逻辑架构与物理架构术语不一致
- 分配矩阵缺 rationale 列
- 资源约束缺单位

### 一句话归纳

**Checklist 核心**：每条元素 / 接口 / 分配链上游、接口有方向、验证显式、无 HARA/TSR、无批准措辞。  
**Review 核心**：与 SyRS / 接口 / 平台约束一致、tier 合规、sample 未当事实、缺口显式、结论不越权批准。

## A1 / A2 / B

**A1**：内容 checklist 有结论；P0 无遗漏。  
**A2**：按 findings 编修订单交 Step 10。
**B**：review 非合规批准；状态 `passed_with_open_items` 或 `failed`。
