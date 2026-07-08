# Software Architecture 子 skill · Step 1 · 输入材料

骨架：`skills/workflow-steps/step-input-materials/SKILL.md`（`task_type: SoftwareArchitecture`）。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点

- 确认本步 run 元数据与 `task_type: SoftwareArchitecture` 边界；共享 run 起点与 manifest / task_brief ownership 由通用 Step 1 / deterministic engine 负责。
- 登记 task.yaml 每份输入：`file_id`、path、title、format、`role`。
- 判定并登记 `writing_scenario`：`from_scratch` 或 `with_reference`。
- **source**：SwRS、**当前项目** System Architecture、软件分层说明、RTE/BSW/OS 约束、接口规范、诊断说明、既有 TSR/软件安全输入（若有）→ `is_fact_source=true`。
- **template**：SwAD 模板 → T2。
- **checklist / reference**：SWE.2 检查项、ASPICE/ISO 写法参考 → T2/T3，`is_fact_source=false`。
- **sample**：历史项目 SwAD → T4，**仅形状**。
- 声明 Software Architecture critical claims 须 `requires_human_confirmation`。
- **底线**：不得把 sample 中的组件/接口/分配/资源预算当作本项目事实。

## Software Architecture 方法论（本步定位）

### 1.1 开发与标准语境中的位置

```text
System Requirement / SyRS（SYS.2）
    ↓
System Architecture（SYS.3）
    ↓
Software Requirement / SwRS（SWE.1）
    ↓
Software Architecture / SwAD（SWE.2）← 本类型
    ↓
Detailed Design / Unit Design（SWE.3）/ Integration / Test
```

**SwAD 核心作用**：在 SwRS 与系统架构约束之下，把控制器软件「如何分层、如何拆组件、组件如何交互、SwRS 如何分配、资源与实时如何约束」写成 **可追溯、可验证、可审查** 的软件架构条目。

### 1.2 本步在八阶段方法链中的位置

本步对应 **阶段 0：启动与范围对齐**。后续 12 步的质量，取决于本步是否：

1. 正确划定软件架构边界（App vs BSW vs 外部）。
2. 区分 **当前项目 source** 与 **历史 SwAD sample**。
3. 诚实登记缺口，为 From-Scratch 的 open 或 With-Reference 的 Δ-Analysis 奠基。

### 1.3 阶段 0 · 启动与范围对齐（本步执行）

#### 通用方法（两种情景均须执行）

1. **明确 SwAD 边界**
   - 范围：本 ECU 应用软件架构（含 App/RTE/BSW 交互视图）。
   - 不含：详细设计、单元设计、代码、HARA/TSR 新编、ASPICE 合规结论。
2. **确定读者**：软件架构师、软件工程师、集成工程师、功能安全接口人、测试负责人。
3. **收集输入**，逐份标注 role 与 tier。
4. **登记 `writing_scenario`**（见主 skill「情景判定」）。
5. **声明非目标**：在 `task_brief` 边界信息中保留 non-goals。

#### From-Scratch 方法要点

| 动作 | 方法说明 |
|---|---|
| 上游锚点检查 | 至少有 SwRS source 或等价软件需求；无则 **P0 gap**，不得开跑后静默补 |
| 架构上下文 | 当前项目 System Architecture 有则登记 source；无则 gap，不借 reference 补 |
| 平台/接口 | RTE/BSW/接口规范缺则 gap；**禁止**预设默认组件划分或任务周期 |
| 安全输入 | 无 TSR/软件安全输入 → 预声明 SEC-SAFE-ARCH 为 open |
| 预期管理 | task_brief 注明：初稿将大量 `NEEDS_USER_CONFIRMATION` |

#### With-Reference 方法要点

| 动作 | 方法说明 |
|---|---|
| 参考隔离登记 | 历史 SwAD **单独 file_id**，`role=sample`，`is_fact_source=false` |
| source 独立 | 本项目 SwRS、当前项目架构、接口规范 **不得**与历史 SwAD 混 file_id |
| 预声明 Δ | task_brief 预声明 **SEC-DIFF（Δ-Analysis）** 为强制章节 |
| 参考用途限定 | notes 写明：「历史 SwAD 仅作章节/图表形状参考，架构事实仅来自本项目 source」 |
| 口头沿用 | 用户说「跟上个项目一样」→ 记 HITL 待确认项，**不能**把 sample 升格 source |

### 1.4 输入材料登记表（事实来源）

| 类别 | 典型文档 | role | 用于章节 |
|---|---|---|---|
| 软件需求 | swrs.md、SWR-F/IF 清单 | source | SEC-UPTRACE、SEC-ALLOC |
| 当前项目系统架构 | system_architecture.md | source | SEC-SWCTX、SEC-UPTRACE |
| 软件上下文 | software_context.md、分层说明 | source | SEC-SWCTX |
| RTE/BSW/OS | autosar_stack.md、bsw_config、os_cfg | source | SEC-PHYSARCH、SEC-RES |
| 软件接口 | rte_ports.md、service_if.md、internal_api | source | SEC-IF |
| 诊断 | diagnostic_sw.md、dcm_dem 约束 | source | SEC-DIAG |
| 平台资源 | mcu_resource.md、memory_map | source | SEC-RES |
| 安全输入 | tsr_sw.md、safety_sw_req（若有） | source | SEC-SAFE-ARCH **引用** |
| SwAD 模板 | swad_template.md | template | 大纲结构 |
| 检查清单 | swe2_checklist、aspice_swe2 | checklist | 审查 |
| 方法学 | swad_reference.md | reference | 写法，非事实 |
| 历史 SwAD | reference_swad_sample.md | sample | **仅**形状 |

**原则**：`fact source ≠ sample`；reference 不能证明本项目 `SWA-COMP` / `SWA-IF` / 资源预算。

### 要回答的问题（本步须为后续奠基）

| 问题 | 对应内容 | 本步动作 |
|---|---|---|
| 本文档范围是什么？ | 适用 ECU 软件、分层、不含详细设计 | task_brief 声明 |
| 写作情景是什么？ | from_scratch / with_reference | 登记 writing_scenario |
| 基于哪些输入？ | SwRS、当前项目架构、RTE/BSW | 登记 source |
| 每条分配追溯哪个 SwRS？ | SWR-F / SWR-IF linkage | 登记 swrs_source |
| 历史 SwAD 如何使用？ | 仅形状 vs 误当事实 | 单独 sample 登记 |
| 还缺什么？ | 开放项 | `knowledge_gaps.md` |

## 本步 Review / Checklist 要点

### ASPICE SWE.2 / ISO 26262-6 输入就绪 Checklist（本步须落实登记）

| 标准 | 检查项 | 通过条件 |
|---|---|---|
| **SWE.2 BP5/BP6 前置** | 上游 SwRS 已登记 | 有 `swrs_source` 或等价 gap + HITL |
| **SWE.2 BP1/BP2 前置** | 接口/BSW/平台材料 | 有 source 或 gap，不借 reference 补 |
| **SWE.2 BP7 前置** | 模板与检查清单 | template + SWE.2 checklist 已登记，tier 正确 |
| **ISO 26262-6 §7 前置** | 软件边界材料 | software_context 或当前项目架构已登记或 gap |
| **ISO 26262-6 接口** | TSR/软件安全输入 | 有则登记「仅引用」；无则预声明 SEC-SAFE-ARCH open |
| **功能安全边界** | 禁止 HARA 材料当 source 写架构 | 无 HARA 报告被标为架构事实来源 |

### 输入分类登记 Checklist（12 类）

| # | 类别 | role 要求 | 必检 | 用于章节 |
|---|---|---|---|---|
| 1 | SwRS | source | 版本/日期 | SEC-UPTRACE、SEC-ALLOC |
| 2 | 当前项目 System Architecture | source 或 gap | file_id 独立 | SEC-SWCTX、SEC-UPTRACE |
| 3 | 软件分层说明 | source 或 gap | App/RTE/BSW/OS | SEC-SWCTX |
| 4 | RTE/BSW/OS 配置 | source 或 gap | — | SEC-PHYSARCH、SEC-RES |
| 5 | 软件接口规范 | source 或 gap | — | SEC-IF |
| 6 | 诊断/降级说明 | source 或 gap | — | SEC-DIAG |
| 7 | 平台/资源约束 | source 或 gap | — | SEC-RES |
| 8 | TSR/软件安全输入 | source（引用）或 gap | 注明仅引用 | SEC-SAFE-ARCH |
| 9 | SwAD 模板 | template | `is_fact_source=false` | 大纲 |
| 10 | SWE.2 检查清单 | checklist | `is_fact_source=false` | 审查 |
| 11 | 方法学参考 | reference | `is_fact_source=false` | 写法 |
| 12 | 历史 SwAD | sample（With-Reference） | **绝不为 source** | 仅形状 |

### 通用 Checklist（10 项）

- [ ] `task_type: SoftwareArchitecture` 已确认
- [ ] `writing_scenario` 已登记（`from_scratch` / `with_reference`）
- [ ] manifest 每份输入：file_id、path、title、format、role、`is_fact_source` 齐全
- [ ] 至少有 1 份 `swrs_source` 或等价（**P0** 若全无且无 HITL）
- [ ] **当前项目** System Architecture 已登记 source 或显式 gap
- [ ] RTE/BSW/OS、接口规范、诊断、平台约束登记或 gap
- [ ] template / checklist / reference → `is_fact_source=false`
- [ ] `task_brief` 明示：非 HARA/FSR/TSC/详细设计、非 ASPICE/ISO 合规认证
- [ ] critical claims 已声明 `requires_human_confirmation`
- [ ] 缺失项写入 `knowledge_gaps.md`，无静默跳过

### 事实来源边界 Checklist

- [ ] `fact source != sample` 已在 task_brief 声明
- [ ] 历史 SwAD 不得支撑 `SWA-COMP` / `SWA-IF` / 任务周期 / 资源预算
- [ ] reference 不得标为架构事实来源
- [ ] 用户口头「沿用参考」已记 HITL 待确认，未把 sample 升格 source

### From-Scratch 专属 Checklist

- [ ] `writing_scenario=from_scratch` 与输入一致（无历史 SwAD 作 source）
- [ ] SwRS 版本、日期、签发方/状态明确登记
- [ ] 无接口规范时 **未**默认接口方向/任务周期
- [ ] 无 TSR/软件安全输入时，task_brief 预声明 SEC-SAFE-ARCH 为 open
- [ ] task_brief 注明：初稿将大量 `NEEDS_USER_CONFIRMATION`
- [ ] 缺口显式登记，**禁止**用 reference 补事实

### With-Reference 专属 Checklist

- [ ] 历史 SwAD **必须** `role=sample`，`is_fact_source=false`（**P0** 不得标 source）
- [ ] 历史 SwAD 与 SwRS / 当前项目架构 **分 file_id** 登记
- [ ] task_brief 预声明 **SEC-DIFF（Δ-Analysis）** 为强制章节
- [ ] notes 含参考边界声明：「历史 SwAD 仅作章节/图表形状参考」
- [ ] 客户「沿用参考方案」已记 HITL，未直接引用 sample 作事实

### 本步 Review 要点（审查维度）

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 上游 source 完备性 | 缺即 gap，不得用 reference 补 | 历史 SwAD **不能**替代 SwRS source |
| 架构上下文 | 当前项目架构是 source 或 gap | 参考架构 **不得**升格为 source |
| tier 正确性 | template/checklist/reference/sample 均非 fact | 同上；参考与本项目 source 分 file_id |
| 情景一致性 | 无 sample 或 sample 仅 template 形状 | 历史 SwAD 仅 sample |
| 功能安全边界 | 无 HARA 当 source；TSR 仅引用登记 | 参考中的安全机制不可照抄登记 |
| 文档边界 | 已声明非详细设计、非批准、非合规认证 | 同上 + SEC-DIFF 预声明 |

### P0 失效项

| 失效 | 后果 |
|---|---|
| 无 SwRS 且无 gap 开跑 | 无分配与追溯锚点 |
| 历史 SwAD 标为 source | 事实来源违规 |
| 未登记 `writing_scenario` | 后续情景 Checklist 无法分支 |
| reference 标为架构事实 | tier 违规 |
| 解析/登记失败静默跳过 | 不可追溯 |

### 一句话归纳

**Checklist 核心**：SwRS 与当前项目架构锚点就绪、role/tier 正确、情景明确、gap 诚实。  
**Review 核心**：From-Scratch 查输入够不够；With-Reference 查历史 SwAD 是否被误标 source 且 SEC-DIFF 已预声明。

## A1 / A2 / B

**A1**：manifest 完整；writing_scenario 明确；sample 未升格；SwRS/架构 source 或 gap 已处理。  
**A2**：补登材料、修正 role、登记 gap、补 writing_scenario。  
**B**：后续 12 步能区分当前项目 source 与历史 SwAD sample。
