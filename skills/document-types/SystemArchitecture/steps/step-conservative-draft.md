# System Architecture 子 skill · Step 9 · 保守草稿

骨架：`skills/workflow-steps/step-conservative-draft/SKILL.md`。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点

- 按 `section_tasks.json` 成稿 → `draft/full_draft.md`。
- 只用 `allowed_evidence`；核对 L1→L2→L3→原文。
- **禁止**：HARA、ASIL、SG、TSR、TSC 终稿、SwRS/HwRS 终稿、ASPICE/ISO 合规措辞。

## System Architecture 方法论（本步定位）

本步对应 **阶段 5：保守成稿**。

### 阶段 5 · 撰写（本步执行）

| 节 | 写法要点 |
|---|---|
| SEC-REQTRACE | 上游 SyRS requirement 摘要；每条有上游 ID |
| SEC-LARCH | 逻辑功能块、职责、关系 |
| SEC-PARCH | 物理/技术模块、平台、通信结构 |
| SEC-ELEM | 每条元素：名称、职责、边界、linked requirements |
| SEC-IF | 每条接口：**Direction**、Counterpart、协议、边界 |
| SEC-ALLOC | requirement → element 分配矩阵；理由有来源 |
| SEC-DIAG | 诊断 / 降级链路；非详细实现 |
| SEC-SAFE-ARCH | **仅引用** FSR/TSC 架构约束；不做新分析 |
| SEC-RES | 资源与平台约束；数值有来源或 open |
| SEC-VERIF | 验证方法标 **候选** 或 open |

### 成功标准（成稿视角）

- 每条元素 / 接口 / 分配矩阵行有唯一 ID，且追溯到 source 中上游需求或架构 source（或 open）。
- 接口含方向与对端；无 sample/reference 支撑。
- 分配理由标来源或待确认，除非 source/HITL 明确支持。
- **无 HARA/ASIL/SG/TSR/TSC/SwRS/HwRS**；无 forbidden final claims。

## 本步 Review / Checklist 要点

### 通用 Checklist

- [ ] 每个 TASK 的 `outputs` 都落到 `draft/full_draft.md` 对应 L2
- [ ] 每条架构元素 / 接口 / 分配语句可验证、可审查
- [ ] 缺证据章节使用 `[PENDING]` / `NEEDS_USER_CONFIRMATION`
- [ ] 草稿引用的 EVD ID 必须在 `evidence_map.json` 中存在

### 架构元素表 Checklist

- [ ] ELEM ID 唯一
- [ ] Responsibility 明确、非模糊词
- [ ] Linked requirements 至少 1 条或 open
- [ ] Boundary 明确（In scope / External / Shared）

### 接口架构表 Checklist

- [ ] IF-ARCH ID 唯一
- [ ] **Direction** = In / Out / Bidirectional / NEEDS_USER_CONFIRMATION
- [ ] Counterpart 明确或 open
- [ ] 协议 / 媒介有来源或 open
- [ ] Failure behavior 有 source 或 open

### 分配矩阵 Checklist

- [ ] 每条上游 requirement 至少映射到 1 个元素或显式 orphan/open
- [ ] Allocation rationale 有 EVD 或 HITL
- [ ] Shared allocation 明确说明边界

### SEC-DIFF（仅 With-Reference）Checklist

- [ ] SEC-DIFF 至少一行；**禁止**只写“同参考”
- [ ] 每行：参考 ID / 本项目 ID / 差异类型 / 差异描述 / **本项目证据来源**

### From-Scratch 专属 Checklist

- [ ] 大量 `[PENDING]` / `NEEDS_USER_CONFIRMATION` 正常，不为关闭而填值
- [ ] 分配 / 接口方向真不明 → open

### With-Reference 专属 Checklist

- [ ] 参考架构措辞**不**出现在元素/接口/分配表，除非已有本项目 EVD
- [ ] Evidence source 列**不**包含参考架构 file_id

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 编造风险 | 静默填元素/分配/资源值 | 参考措辞无 EVD 进表 |
| Direction 列 | 缺则 open | 缺则 open；不得抄参考架构 |
| SEC-DIFF | 不存在 | 必存且具体 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 架构元素/分配无上游却标 confirmed | 不可追溯 |
| 含 HARA / ASIL / SG / TSR | 文档类型漂移 |
| 接口无方向且标已确认 | 集成/分配困难 |
| 写“已批准 / ASPICE 合规 / ISO 合规 / 可量产” | 越权结论 |
| 参考架构内容无 EVD 写入正文 | 事实来源违规 |

## A1 / A2 / B

**A1**：无超出 `allowed_evidence` 的表述；无 HARA/TSC 泄漏；每条元素/接口/分配有上游列或 open；接口有 Direction。  
**A2**：按 TASK 重跑缺证据节；修正 forbidden / Direction 缺失。  
**B**：无 forbidden final claims；SEC-DIFF（若 With-Reference）具体且有 EVD。
