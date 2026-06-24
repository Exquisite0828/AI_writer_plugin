# SyRS 子 skill · Step 2 · 材料清单

骨架：`skills/workflow-steps/step-material-inventory/SKILL.md`。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点

- 解析每份材料，产出 `inputs/input_inventory.json`。
- **source** 摘要须覆盖：干系人需求片段、候选 SYS-F/IF、性能/环境/诊断线索、架构边界、安全引用片段。
- **sample** 仅入 `style_hint`，**禁止**写入 SYS-xx/限值事实字段。
- 失败/缺失如实标记。

## SyRS 方法论（本步定位）

本步对应 **阶段 1：材料消化** 第一环——在索引（Step 3）前结构化解析。

### 阶段 1 · 材料消化（本步执行）

1. 解析 SWRS、RFQ、架构、接口规范、诊断规范等。
2. 从 **source** 提取 **候选 SYS-F-xx / SYS-IF-xx**（未定稿）。
3. **样例 SyRS** 只提取表头、章节粒度，不复制需求/接口/限值内容。

### 各 role 提取重点

| role | 须提取 | 禁止 |
|---|---|---|
| swrs_source / rfq | 需求 ID、功能描述、约束片段 | 标为 SyRS 已确认 |
| interface_spec | 信号、方向、对端线索 | 无方向标为已确认 |
| system_architecture | ECU 边界、子系统上下文 | 当作架构终稿 sign-off |
| diagnostic_spec | DTC、降级模式线索 | 当作诊断实现规格 |
| fsr_source（若有） | 显式 FSR/SG 引用片段 | 扩展为新 HARA/ASIL 判断 |
| syrs_reference | 写法要点、SYS.2 检查标题 | 当作项目需求事实 |
| sample | 表头、SYS-F/IF 列定义 | 提取具体需求/接口/限值 |

### 七大主题线索（inventory 摘要宜覆盖）

| 主题 | 典型来源 | 用途 |
|---|---|---|
| 功能 | SWRS、RFQ | SYS-F-xx 候选 |
| 接口 | 接口规范、CAN 矩阵 | SYS-IF-xx 候选 |
| 性能 | SWRS、技术规范 | SEC-PERF |
| 环境 | ODD、安装/电气规范 | SEC-ENV |
| 诊断 | 诊断规范 | SEC-DIAG |
| 法规 | 法规清单 | SEC-LEGAL |
| 追溯 | SWRS ID 映射 | SEC-TRACE |

## 本步 Review / Checklist 要点

### 通用 Checklist（每次 run 必查）

- [ ] 每份材料 `parse_status` 明确：`ok` / `partial` / `failed`，失败有原因
- [ ] source 摘要必须含 **七大主题 + 安全引用**（功能 / 接口 / 性能 / 环境 / 诊断 / 法规 / 追溯 / 安全引用）
- [ ] 每条 **候选 SYS-F-xx** 摘要含：候选表述、来源文档与段落、`status=candidate`
- [ ] 每条 **候选 SYS-IF-xx** 摘要含：信号名、方向线索（In/Out/未知）、对端线索、`status=candidate`
- [ ] **优先级线索**（Must/Should/Nice-to-have、shall/should/may）按出现位置记录
- [ ] sample / 参考 SyRS 仅入 `style_hint`（章节结构、表头列名），**禁止**写入 SYS-xx/限值事实字段
- [ ] 候选 SYS-xx **未标** confirmed，仅候选状态
- [ ] parse 失败/无法读取的材料显式登记，不静默跳过

### 七大主题提取覆盖度 Checklist

| 主题 | 提取要点 | 缺失处理 |
|---|---|---|
| 功能 | 候选 SYS-F-xx ID 候选、shall/will 句式、运行模式 | 标 gap → SEC-FUNC |
| 接口 | 信号名/类型、方向 In/Out、对端、超时/失效行为线索 | 标 gap → SEC-IF |
| 性能 | 时序、采样率、精度、带宽数值 | 标 gap → SEC-PERF |
| 环境 | 温度/电压/EMC/振动数值 | 标 gap → SEC-ENV |
| 诊断 | DTC 列表、降级模式、limp-home 线索 | 标 gap → SEC-DIAG |
| 法规 | 法规编号、章节引用 | 标 gap → SEC-LEGAL |
| 安全引用 | 既有 FSR/SG ID 与表述（仅引用） | 无则 SEC-SAFE 留 open |

### ASPICE / ISO 26262 维度 Checklist

- [ ] **ASPICE SYS.2 BP1**：客户/干系人需求摘要可被映射为 SEC-STAKE 表行
- [ ] **ASPICE SYS.2 BP5**：上游 ID（SWRS-xxx 等）已按 task_brief 命名规则提取
- [ ] **ISO 26262-3 §5（下游 IDD）**：摘要含 Item 功能、边界、接口、工况线索
- [ ] **ISO 26262-3 §7（下游 FSR）**：若有 FSR 输入，仅摘要 FSR ID / SG ID，**不做新 HARA 判断**

### From-Scratch 专属 Checklist

- [ ] 七大主题任一缺失须标 gap，**禁止**用 reference 推断填值
- [ ] 限值（电压/温度/时序）数字必须有 source 段落引用，否则 `status=open`
- [ ] 接口方向不明时显式标 `direction=unknown_pending_confirmation`

### With-Reference 专属 Checklist

- [ ] 参考 SyRS 解析结果仅入 `style_hint`（章节、列名）；**禁止**任何 SYS-ID / 限值 / 接口方向写入事实字段（**P0**）
- [ ] 参考 SyRS 与本项目 source **分 inventory 条目**，不得合并
- [ ] 参考 SyRS 中的需求 ID 改写为 `REF-Fxx`（仅供 Δ-Analysis 引用），避免与本项目 SYS-F-xx 冲突
- [ ] 平台/变型差异线索（接口变化、新增功能、删除功能）已登记，供 SEC-DIFF 写作计划使用

### 本步 Review 要点（双情景对比）

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 解析完整性 | 七大主题须显式 ok/gap | 参考 SyRS 解析只到 `style_hint` |
| 候选 SYS-xx | 大量 candidate 状态 | candidate 来源**仅**本项目 SWRS，不得来自参考 SyRS |
| 限值字段 | 缺 source → `[PENDING]` | 不得用参考 SyRS 数字填限值 |
| 优先级线索 | shall 强、should 弱 | 不得继承参考 SyRS 的优先级判断 |
| Δ 线索 | — | 已登记新增/删除/修改候选 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 参考 SyRS 需求照抄进 inventory 事实字段 | 事实来源违规（**P0**） |
| 从 reference / sample 推断未列出限值数字 | 越权事实 |
| 解析失败静默跳过 | 不可追溯 |
| 接口方向凭经验默认 In/Out | 后续集成错误 |
| FSR 摘要被扩展为新 HARA / ASIL 判断 | 文档类型漂移 |

### 常见 P1

- 候选 SYS-xx 未标 candidate 状态，下游误以为 confirmed
- 优先级线索未提取（shall/should 全归一），影响 SEC-FUNC Priority 列
- 法规章节引用粒度过粗

## A1 / A2 / B

**A1**：parse_status 齐全；七大主题覆盖；sample 未流入事实字段。  
**A2**：重解析失败项、补主题摘要、修正 candidate 状态。  
**B**：摘要可直接支撑 SEC-STAKE/SEC-FUNC/SEC-IF/SEC-TRACE。
