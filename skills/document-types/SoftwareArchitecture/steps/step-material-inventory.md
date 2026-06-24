# Software Architecture 子 skill · Step 2 · 材料清单

骨架：`skills/workflow-steps/step-material-inventory/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点

- 解析每份材料，产出 `inputs/input_inventory.json`。
- **source** 摘要须覆盖：上游 SwRS、候选组件、候选接口、分配线索、任务/调度、诊断/降级、资源预算、安全引用。
- **sample** 仅入 `style_hint`，**禁止**写入组件/接口/分配/资源事实字段。
- 失败/缺失如实标记。

## Software Architecture 方法论（本步定位）

### 2.1 本步在八阶段方法链中的位置

本步对应 **阶段 1：材料消化** 第一环。在建立索引（Step 3）之前，把各 source 中的 **候选架构信息** 结构化提取出来。

**方法原则**：本步产出的是 **candidate**（候选），不是 **confirmed**（已确认）架构。所有组件/接口/分配在 inventory 中默认 `status=candidate_only`，除非 source 明确写明且可摘录。

### 2.2 阶段 1 · 材料消化（本步执行）

#### 通用提取顺序（建议按此顺序读 source）

```text
1. SwRS（SWR-F / SWR-IF）     → 功能意图、接口约束、分配线索
2. 当前项目 System Architecture → 系统边界、运行模式、外部接口上下文
3. 软件分层说明               → App/RTE/BSW/OS 边界
4. RTE/接口规范               → 端口、服务、方向、对端
5. BSW/OS/平台约束            → 任务、调度、内存、芯片限制
6. 诊断说明                   → DTC 链、降级模式线索
7. TSR/软件安全输入（若有）    → 仅摘要可引用约束，不扩展
```

#### From-Scratch 方法要点

| 主题 | 提取方法 | 缺口处理 |
|---|---|---|
| 候选组件 | 从 SwRS 功能块 + 分层说明归纳 **名称级** 候选 | 无依据则不命名，标 gap |
| 候选接口 | 从 SWR-IF + RTE 规范提取，方向不明标 `unknown` | 不默认 Provider/Consumer |
| 候选分配 | SwRS ID → 候选组件映射，标 `allocation_status=candidate_only` | 无 source 不填 |
| 任务/调度 | 从 OS 配置/平台文档提取周期、优先级 **线索** | 无数值则 `[PENDING]` |
| 资源预算 | 提取 ROM/RAM/栈 **线索** | 禁止从 reference 推断 |

**禁止**：用 ASPICE/ISO reference 文档中的示例组件名填 inventory。

#### With-Reference 方法要点

| 动作 | 方法说明 |
|---|---|
| 历史 SwAD 解析 | 仅提取：章节标题、图类型、表头列名、术语习惯 → `style_hint` |
| 差异线索登记 | 对比本项目 SwRS 与参考 SwAD 的 **结构差异线索**（非事实）：如「参考有 X 组件类，本项目 SwRS 未提及」→ 供 SEC-DIFF |
| 事实字段隔离 | 参考文档中的 SWA-COMP/IF/任务周期/内存值 **不得**进入 inventory 事实字段 |
| 变型差异 | 芯片/OS/BSW 代际差异记 `variant_delta_hint`，不写成已确认架构 |

### 2.3 各 role 提取重点

| role | 须提取 | 禁止 |
|---|---|---|
| swrs_source | SWR-F/IF ID、功能摘要、接口约束、分配线索 | 标为架构已确认 |
| current_system_architecture | 系统边界、运行模式、外部接口 | 当作软件详细设计 |
| software_context | 分层、变型、软件边界 | 当作单元设计 |
| rte_bsw_constraints | BSW 模块、OS 任务、调度线索 | 标为已批准任务表 |
| interface_spec | 接口名、方向、对端、RTE 类型 | 无方向标 confirmed |
| platform_constraints | 内存/栈/时序预算线索 | 当作详细设计终稿 |
| diagnostic_constraints | 诊断、降级、故障链路线索 | 当作函数实现规格 |
| tsr_or_safety_sw_excerpt | 显式软件架构约束片段 | 扩展为新 HARA/TSR |
| swad_reference (sample) | 章节结构、图表形状 | 提取具体组件/资源值 |

### 2.4 ASPICE SWE.2 对齐（本步应能支撑的后续 BP）

| SWE.2 方向 | 本步应提取的候选信息 |
|---|---|
| 静态架构 | 候选组件、Layer、接口清单 |
| 动态架构 | 任务/Runnable/模式切换线索 |
| 追溯准备 | SwRS ID 与候选组件的初步映射 |
| 资源 | 内存/时序/调度预算线索 |

## 本步 Review / Checklist 要点

### ASPICE SWE.2 材料消化 Checklist（本步提取应对齐）

| SWE.2 方向 | 本步须提取的候选信息 | 通过条件 |
|---|---|---|
| **BP1 静态架构** | 候选组件、Layer、接口清单 | 来自 source 摘要或 gap |
| **BP2 动态架构** | 任务/Runnable/模式切换线索 | 来自 BSW/OS 或 gap |
| **BP5 追溯准备** | SwRS ID ↔ 候选组件映射 | `candidate_only`，非 confirmed |
| **BP6 一致性准备** | SwRS 与架构上下文不矛盾线索 | 冲突记 gap，不静默调和 |
| **资源/约束** | 内存/时序/调度预算线索 | 有摘录或 `[PENDING]` |

### ISO 26262-6 材料消化 Checklist

- [ ] TSR/软件安全输入仅摘要 **可引用** 约束片段，未扩展为新分析
- [ ] 安全相关候选信息标 `safety_ref_only`，非 `safety_confirmed`
- [ ] 未从 sample 提取 ASIL、安全机制、分区策略作为本项目事实

### 主题提取覆盖 Checklist（9 主题）

| 主题 | 提取要点 | 缺失处理 | 对应章节 |
|---|---|---|---|
| 上游 SwRS | SWR-F/IF ID、功能摘要 | gap | SEC-UPTRACE |
| 逻辑架构 | 功能块、职责、数据流 | gap | SEC-LOGARCH |
| 物理/战术架构 | 组件、任务、BSW 层 | gap | SEC-PHYSARCH |
| 软件接口 | 名称、方向、对端、RTE 类型 | gap | SEC-IF |
| 分配 | SwRS→组件候选映射 | gap | SEC-ALLOC |
| 任务/调度 | 任务名、周期、优先级线索 | gap | SEC-RES |
| 诊断/降级 | 检测、上报、降级链路 | gap | SEC-DIAG |
| 资源约束 | 内存/栈/CPU/时序线索 | gap | SEC-RES |
| 安全引用 | TSR/软件安全约束摘要 | gap | SEC-SAFE-ARCH |

### 通用 Checklist（8 项）

- [ ] 每份材料有 `parse_status`（success / partial / failed）
- [ ] source 摘要覆盖上述 9 主题或显式 gap
- [ ] 候选组件/接口/分配均为 `candidate_only` / `unknown`，**非** `confirmed`
- [ ] sample / 历史 SwAD **未流入** 组件/接口/分配/资源事实字段
- [ ] 解析失败项在 inventory 中标记，未静默跳过
- [ ] 接口方向不明 → `direction=unknown_pending_confirmation`
- [ ] 分配无 source → `allocation_status=candidate_only`
- [ ] inventory 与 manifest role 一致

### From-Scratch 专属 Checklist

- [ ] 各主题缺失均标 gap，**禁止**用 reference 推断填值
- [ ] 无 SwRS 分配线索时，不编造 `SWA-COMP` 名称
- [ ] 无 OS 配置时，任务/周期字段为 `[PENDING]`，非默认值
- [ ] 预期：inventory 中 candidate 行数多、confirmed 行数少

### With-Reference 专属 Checklist

- [ ] 历史 SwAD 解析结果 **仅**入 `style_hint`（章节、图名、表列）
- [ ] `variant_delta_hint` 已登记（芯片/OS/BSW 变型差异线索）
- [ ] 参考组件/接口/任务周期/内存值 **未**写入事实字段（**P0**）
- [ ] 结构差异线索（参考有而本项目 SwRS 无）记入 `delta_hints`，非事实

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 解析完整性 | 主题缺即 gap | 历史 SwAD 只到 `style_hint` |
| 候选态 | 全部 candidate/unknown | candidate 来源**仅**本项目 source |
| 资源字段 | 缺 source → `[PENDING]` | 不得用历史 SwAD 数字填资源 |
| 安全边界 | 无 HARA/ASIL 进 inventory | 参考安全机制不可照抄 |
| 失败处理 | parse_status 如实 | 同上 |

### P0 失效项

| 失效 | 后果 |
|---|---|
| 历史 SwAD 组件/接口照抄进 inventory | 事实来源违规 |
| 从 sample/reference 推断资源预算 | 越权事实 |
| 解析失败静默跳过 | 不可追溯 |
| 接口方向凭经验默认 In/Out | 后续分配错误 |
| 候选标为 confirmed | 后续无法保留 open |

### P1 失效项

- 摘要缺 file_id / source 段落引用
- 9 主题中部分主题无 gap 也无内容
- Layer 字段与 software_context 不一致未标注

### 一句话归纳

**Checklist 核心**：9 主题候选提取完整、全为 candidate 态、sample 未污染事实字段。  
**Review 核心**：From-Scratch 查 gap 诚实；With-Reference 查历史 SwAD 是否渗入 inventory 事实。

## A1 / A2 / B

**A1**：parse_status 齐全；主题为候选态；sample 隔离。  
**A2**：重解析、补摘要、修正 candidate 状态。  
**B**：摘要可支撑 Step 3 索引与 Step 4 大纲槽位规划。
