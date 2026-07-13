# Software Architecture 子 skill · Step 7 · 保守草稿

骨架：`skills/workflow-steps/step-conservative-draft/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点

- 按 `section_tasks.json` 成稿 → `draft/full_draft.md`。
- **仅**使用各 TASK 的 `allowed_evidence`。
- 产出 review-ready 草稿，非详细设计终稿、非合规结论。

## Software Architecture 方法论（本步定位）

### 7.1 本步在八阶段方法链中的位置

本步对应 **阶段 5：保守成稿**。把 EVD 转化为可审查的 SwAD 正文，是 ASPICE SWE.2 文档化的核心产出步骤。

**方法原则**：

1. **有 EVD 才写事实**；无 EVD 写 `[PENDING]` 或 `NEEDS_USER_CONFIRMATION`。
2. **写架构，不写实现**：描述组件、接口、任务、资源预算，不写类/函数/算法/代码。
3. **逐表逐行可追溯**：每个 SWA-COMP / SWA-IF / 分配行可指回 EVD 或 open。

### 7.2 阶段 5 · 撰写方法（按章节）

#### SEC-SWCTX · 软件上下文

- 写明：ECU 软件范围、App/RTE/BSW/OS 分层、运行模式、与 System Architecture 边界。
- 来源：software_context + current_system_architecture EVD。
- **禁止**：写具体 BSW 配置参数值（除非 source 明确）。

#### SEC-UPTRACE · 上游追溯

- 列表摘要 SWR-F / SWR-IF，每条带 ID 与一句话意图。
- 建立「SwRS → 架构入口」导航，非完整分配（分配在 SEC-ALLOC）。

#### SEC-LOGARCH · 逻辑软件架构

- 功能块图（文字或 mermaid 描述）：块名、职责、数据流方向。
- 逻辑块与候选 SWA-COMP 的映射可标注 `candidate`。
- **方法**：从 SwRS 功能需求归纳逻辑块，**一块一职责**。

#### SEC-PHYSARCH · 物理/战术架构

- 组件在 RTE/BSW/OS 上的落地：Runnable、Task、BSW 模块关系。
- 模式转换：Init → Run → Sleep 等（有 source 才写）。
- **汽车控制器典型内容**：Task 名、周期、优先级、Runnable 映射（有 EVD 才填值）。

#### SEC-COMP · 软件组件清单

- 每行：SWA-COMP ID、Layer、Responsibility、Boundary、Linked SwRS。
- 组件粒度指导：对齐 SwRS 可分配单元，通常 App SWC 级，不把每个函数当组件。
- 缺证据行：Confirmation status = NEEDS_USER_CONFIRMATION。

#### SEC-IF · 软件接口架构

- 每行 **必须**有 Direction（Provider/Consumer/Bidirectional 或 open）。
- RTE Port：注明 Port名、数据元素、对端组件。
- 服务接口：注明调用方向与触发方式（有 source 才写）。

#### SEC-ALLOC · SwRS 分配矩阵

- 每条 SwRS 至少一行分配或 explicit orphan/open。
- Rationale 列：引用 EVD 摘要或写 NEEDS_USER_CONFIRMATION。
- Shared allocation：须说明共享边界与职责划分来源。

#### SEC-DIAG · 诊断与降级软件架构

- 描述 **组件层** 故障检测→存储→上报→降级路径，不写 Dcm 函数实现。
- 与 Dem/Dcm 关系用架构语言，不用代码 API。

#### SEC-SAFE-ARCH · 安全相关（若有）

- **仅引用** TSR/软件安全 source 中已有约束。
- 链到 SWA-COMP / SWA-IF / 分区策略，不新做 ASIL 分析。

#### SEC-RES · 资源与实时

- ROM/RAM/栈、任务 WCET 线索、CPU 负载预算：数值须带单位，有 EVD 才写。
- 无时序 source 不编 10ms/20ms 默认值。

#### SEC-VERIF · 验证方法候选

- 列 **候选** 方法：架构评审、资源分析、集成测试、静态分析/MISRA 等。
- 写「建议」或「候选」，不写「已验证通过」。

#### SEC-DIFF · Δ-Analysis（仅 With-Reference）

- 每行必须有：参考 ID、本项目 ID、Δ Type、差异描述、**本项目 evidence**。
- **禁止**只写「与参考相同」。

### 7.3 两种情景成稿策略

#### From-Scratch

| 策略 | 说明 |
|---|---|
| 容忍空表 | 无 EVD 的表保留表头 + 0 行或全 open 行 |
| 不关 open | 不为美观填默认组件名/周期/内存 |
| 显式 gap 段 | SEC-OPEN 汇总 unresolved |

#### With-Reference

| 策略 | 说明 |
|---|---|
| 参考不进表 | 历史 SwAD 组件/接口不出现在 COMP/IF/ALLOC 表 |
| SEC-DIFF 必填 | 至少一行具体差异 |
| 措辞隔离 | 可参考写章节引导语，事实表只含本项目 EVD |
| 沿用须 EVD | 「沿用参考」须有 T0 HITL 或本项目 source EVD |

### 7.4 写作语言规范

- 用「应描述」「定义为」「分配给」，不用「已实现」「已验证」。
- 避免模糊词：「高效」「合理」「足够」。
- 数值带单位：ms、KB、% CPU、MHz。
- 禁止：HARA、ASIL、SG、TSR 新编、类图、伪代码、生产批准措辞。

## 本步 Review / Checklist 要点

### ASPICE SWE.2 成稿 Checklist（按章节）

| 章节 | SWE.2 BP | 成稿检查项 |
|---|---|---|
| SEC-SWCTX | BP1/BP7 | 分层、边界、运行模式有 EVD 或 open |
| SEC-UPTRACE | BP5/BP6 | 每条 SWR-F/IF 有 ID 与摘要或 open |
| SEC-LOGARCH | BP1 | 逻辑块职责清晰；一块一职责 |
| SEC-PHYSARCH | BP2 | 任务/Runnable/BSW 结构有来源或 open |
| SEC-COMP | BP1 | SWA-COMP ID 唯一；Layer/Boundary/Linked SwRS 齐全或 open |
| SEC-IF | BP1 | **Direction** 列无空白 confirmed；对端/类型有来源或 open |
| SEC-ALLOC | BP5/BP6 | 每条 SwRS 有组件落点或 orphan/open；Rationale 有 EVD |
| SEC-DIAG | BP1/BP2 | 组件层诊断链，非函数实现 |
| SEC-SAFE-ARCH | ISO 26262-6 | 仅引用 TSR；无新 HARA/ASIL/机制设计 |
| SEC-RES | BP2 | 数值带单位；有 EVD 或 open |
| SEC-VERIF | BP3/BP7 | 验证方法为**候选**；无「已验证」 |
| SEC-DIFF | — | **仅 With-Reference**；具体差异 + 本项目 evidence |

### 软件组件表 Checklist（8 项）

- [ ] SWA-COMP ID 唯一且符合命名规则
- [ ] Layer ∈ {App, RTE, BSW, OS, CDD, …} 或 open
- [ ] Responsibility 明确，无模糊词
- [ ] Boundary = In scope / External / Shared 或 open
- [ ] Linked SwRS ≥1 或 NEEDS_USER_CONFIRMATION
- [ ] Task/scheduling hint 有 EVD 或 open
- [ ] Evidence source 为 T0/T1 file_id
- [ ] Confirmation status 与 EVD 一致

### 软件接口表 Checklist（8 项）

- [ ] SWA-IF ID 唯一
- [ ] **Direction** ∈ {Provider, Consumer, Bidirectional, NEEDS_USER_CONFIRMATION}
- [ ] Counterpart 明确或 open
- [ ] Type（RTE Port/Service/Internal API 等）有来源或 open
- [ ] Linked components / Linked SwRS 可追溯
- [ ] 无 Direction 时 **不得**标 confirmed（**P0**）
- [ ] Evidence source 不含历史 SwAD file_id
- [ ] 失效行为有 source 或 open

### 分配矩阵 Checklist（6 项）

- [ ] 每条上游 SwRS 至少映射 1 组件或 explicit orphan
- [ ] Allocation rationale 有 EVD 摘录或 NEEDS_USER_CONFIRMATION
- [ ] Shared allocation 有边界说明来源
- [ ] Interface impact 列与 SEC-IF 一致或 open
- [ ] 无 SwRS 行标 confirmed 却无上游 EVD（**P0**）
- [ ] 双向：每个 SWA-COMP 至少链 1 SwRS 或说明 orphan

### 写作语言与边界 Checklist

- [ ] 用「定义为」「分配给」「应描述」，不用「已实现」「已验证」
- [ ] 避免模糊词：高效、合理、足够、稳定
- [ ] 资源/时序数字带单位（ms、KB、% CPU）
- [ ] **无** HARA / ASIL / SG / TSR 新编 / 类图 / 伪代码 / 代码片段
- [ ] **无** `approved` / `compliant` / `production ready` / `ASPICE satisfied`
- [ ] 草稿引用的 EVD ID 均在 `evidence_map.json` 中存在

### From-Scratch 专属 Checklist

- [ ] 大量 `[PENDING]` / `NEEDS_USER_CONFIRMATION` 为正常
- [ ] 不为关闭 open 而填默认任务周期、栈大小、内存值
- [ ] 空表保留表头可接受
- [ ] SEC-OPEN 汇总与 unresolved 一致

### With-Reference 专属 Checklist

- [ ] SEC-DIFF ≥1 行，且**禁止**只写「同参考」
- [ ] 每行 Δ：Ref ID / Project ID / Δ Type / 描述 / **本项目 Evidence**
- [ ] 历史 SwAD 措辞不出现在 COMP/IF/ALLOC 表（除非有本项目 EVD）
- [ ] Evidence source 列无历史 SwAD file_id
- [ ] 「沿用参考」句须有 T0 HITL 或本项目 EVD

### 本步 Review 要点（9 维度）

| 维度 | Review 要点 |
|---|---|
| 与 SwRS 一致 | 组件/接口/分配是否与 SwRS 一致；有无无来源架构决策 |
| 逻辑-物理一致 | SEC-LOGARCH 与 SEC-PHYSARCH 术语/组件名不矛盾 |
| 接口完整性 | Direction、Counterpart、Type、边界齐全或 open |
| 追溯完整 | SwRS↔SWA-COMP 双向可查或 open |
| 资源来源 | 内存/周期/栈有 EVD 或 open |
| 安全边界 | SEC-SAFE-ARCH 仅引用；无 HARA/TSR 泄漏 |
| 证据匹配 | 正文每事实行可指 EVD 或 open |
| 参考边界 | sample 未进事实表 |
| 文档边界 | 无详细设计/代码/批准措辞 |

### 双情景 Review 对比

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| open 密度 | 高为正常 | 可较低，但须逐条 EVD |
| 编造检测 | 无 EVD 的 confirmed 行 | 参考措辞无 EVD 进表 |
| SEC-DIFF | 无 | **必查**具体性 |
| Direction | 缺则 open | 不得抄参考方向 |

### P0 失效项

| 失效 | 后果 |
|---|---|
| 组件/分配无上游却标 confirmed | 不可追溯 |
| 含 HARA/ASIL/SG/TSR/详细设计/代码 | 文档类型漂移 |
| 接口无 Direction 且 confirmed | 集成困难 |
| 历史 SwAD 无 EVD 写入正文表 | 事实违规 |
| 批准/ASPICE/ISO 合规措辞 | 越权 |

### P1 失效项

- Layer 与 PHYSARCH 表述不一致
- 分配缺 Rationale 列内容
- SEC-VERIF 无 status/候选标注

### 一句话归纳

**Checklist 核心**：三表逐行可追溯、Direction 强制、仅 allowed_evidence、无实现/安全/批准泄漏。  
**Review 核心**：From-Scratch 查静默填值；With-Reference 查 SEC-DIFF 与参考未渗入事实表。

## A1 / A2 / B

**A1**：草稿保守、可追溯、无实现泄漏。  
**A2**：删违规正文、补 open。  
**B**：每行可追 allowed_evidence 或 open。
