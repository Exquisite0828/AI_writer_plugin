# System Architecture 子 skill · Step 2 · 材料清单

骨架：`skills/workflow-steps/step-material-inventory/SKILL.md`。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点

- 解析每份材料，产出 `inputs/input_inventory.json`。
- **source** 摘要须覆盖：上游需求片段、候选架构元素、候选接口、分配线索、诊断/降级链路、平台资源约束、安全引用片段。
- **sample** 仅入 `style_hint`，**禁止**写入架构元素/接口/分配事实字段。
- 失败/缺失如实标记。

## System Architecture 方法论（本步定位）

本步对应 **阶段 1：材料消化** 第一环——在索引（Step 3）前结构化解析。

### 阶段 1 · 材料消化（本步执行）

1. 解析 SyRS、系统上下文、接口规范、平台/资源约束、诊断说明等。
2. 从 **source** 提取 **候选架构元素 / 候选接口 / 候选分配关系**（未定稿）。
3. **样例架构文档** 只提取章节结构、图表列名、术语形状，不复制元素/接口/分配内容。

### 各 role 提取重点

| role | 须提取 | 禁止 |
|---|---|---|
| syrs_source | 上游需求 ID、功能摘要、接口约束、分配线索 | 标为架构已确认 |
| system_context | ECU 边界、变型、外部关系 | 当作详细设计终稿 |
| interface_spec | 接口名、方向、对端、协议线索 | 无方向标为已确认 |
| platform_constraints | 芯片/OS/内存/总线约束 | 当作硬件/软件终稿设计 |
| diagnostic_constraints | 诊断、降级、故障链路线索 | 当作详细实现规格 |
| fsr_or_tsc_excerpt | 显式架构约束片段 | 扩展为新 HARA / TSR 判断 |
| architecture_reference | 写法要点、图表结构 | 当作项目架构事实 |
| sample | 图标题、表头、章节粒度 | 提取具体元素/接口/资源值 |

## 本步 Review / Checklist 要点

### 通用 Checklist

- [ ] 每份材料有 `parse_status`
- [ ] source 摘要覆盖：上游需求、候选元素、候选接口、分配、诊断/降级、资源约束
- [ ] sample/参考架构 **未流入** 元素/接口/分配/资源值事实字段
- [ ] 候选架构元素 / 分配 **未标** confirmed

### 主题提取覆盖 Checklist

| 主题 | 提取要点 | 缺失处理 |
|---|---|---|
| 上游需求 | SyRS requirement ID、功能摘要 | 标 gap → SEC-REQTRACE |
| 逻辑架构 | 功能块、职责、数据流线索 | 标 gap → SEC-LARCH |
| 物理架构 | ECU 内部模块、外设、网络节点 | 标 gap → SEC-PARCH |
| 接口 | 名称、方向、对端、协议 | 标 gap → SEC-IF |
| 分配 | 需求到元素的候选映射 | 标 gap → SEC-ALLOC |
| 诊断/降级 | 检测、上报、降级链路 | 标 gap → SEC-DIAG |
| 资源约束 | CPU/内存/总线/时序线索 | 标 gap → SEC-RES |
| 安全引用 | FSR/SG/TSC 约束摘要（仅引用） | 无则 SEC-SAFE-ARCH 留 open |

### ASPICE / ISO 维度 Checklist

- [ ] **ASPICE SYS.3**：上游需求可映射为候选架构分配关系
- [ ] **ASPICE SYS.3**：接口与元素信息足以支撑架构分解
- [ ] **ISO 26262 接口**：若有 FSR/TSC 输入，仅摘要架构约束，不做新分析

### From-Scratch 专属 Checklist

- [ ] 各主题缺失须标 gap，**禁止**用 reference 推断填值
- [ ] 接口方向不明时显式标 `direction=unknown_pending_confirmation`
- [ ] 分配关系无 source 时标 `allocation_status=candidate_only`

### With-Reference 专属 Checklist

- [ ] 参考架构文档解析结果仅入 `style_hint`（章节、图名、表列）
- [ ] 参考元素 / 接口 / 分配 **不得**写入事实字段（**P0**）
- [ ] 平台 / 变型差异线索已登记，供 SEC-DIFF 使用

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 解析完整性 | 主题缺即 gap | 参考架构只到 `style_hint` |
| 候选元素/接口 | 大量 candidate 状态 | candidate 来源**仅**本项目 source |
| 资源值字段 | 缺 source → `[PENDING]` | 不得用参考架构数字填资源值 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 参考架构元素/接口照抄进 inventory | 事实来源违规 |
| 从 reference / sample 推断资源值 | 越权事实 |
| 解析失败静默跳过 | 不可追溯 |
| 接口方向凭经验默认 In/Out | 后续分配错误 |

## A1 / A2 / B

**A1**：parse_status 齐全；主题覆盖；sample 未流入事实字段。  
**A2**：重解析失败项、补摘要、修正 candidate 状态。  
**B**：摘要可直接支撑 SEC-REQTRACE / SEC-LARCH / SEC-IF / SEC-ALLOC。
