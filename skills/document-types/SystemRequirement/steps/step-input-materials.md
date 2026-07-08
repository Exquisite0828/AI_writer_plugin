# SyRS 子 skill · Step 1 · 输入材料

骨架：`skills/workflow-steps/step-input-materials/SKILL.md`（`task_type: SystemRequirement`）。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点

- 确认本步 run 元数据与 `task_type: SystemRequirement` 边界；共享 run 起点与 manifest / task_brief ownership 由通用 Step 1 / deterministic engine 负责。
- 登记 task.yaml 每份输入：`file_id`、path、title、format、`role`。
- **source**：SWRS/RFQ、架构、接口规范、ODD、诊断规范、法规清单、既有 FSR（若有）→ `is_fact_source=true`。
- **template**：SyRS 模板 → T2。
- **checklist / reference**：SYS.2 检查项、ASPICE/ISO 写法参考 → T2/T3，`is_fact_source=false`。
- **sample**：参考项目 SyRS → T4，**仅形状**。
- 声明 SyRS critical claims 须 `requires_human_confirmation`。
- **底线**：不得把 sample 中的 SYS-F/IF/限值当作本项目事实；不得把 reference 当 SWRS 事实。

## SyRS 方法论（本步定位）

### 1.1 开发与标准语境中的位置

```
干系人/客户需求（SWRS、RFQ、法规）
    ↓
SyRS（ASPICE SYS.2）← 本类型
    ↓
├─→ Item Definition（ISO 26262-3 §5）
├─→ 系统架构（ASPICE SYS.3）
├─→ HARA / FSR（独立下游，本类型不写）
└─→ SwRS / HwRS（本类型不写终稿）
```

**SyRS 核心作用**：把控制器产品「应实现什么、与谁交互、在什么约束下运行」写成 **可追溯、可验证、可审查** 的系统需求条目，并建立与上游客户需求的追溯。

### 1.2 本仓库定位

- document-type skill 层，走统一 **13 步** workflow。
- 产出 **review-ready** SyRS 候选包，**不是**需求批准书、ASPICE 评估通过或 ISO 26262 合规认证。
- **明确不做**：HARA、FSR 新编、TSC、SwRS/HwRS 终稿。

### 1.3 重要边界

| 文档 | SyRS 与之关系 |
|---|---|
| SWRS / RFQ | 上游：干系人需求追溯锚点 |
| Item Definition | 下游：从 SyRS 提取 F-xx、边界、接口 |
| HARA / FSR | **禁止**写危害、ASIL、SG 新结论；SEC-SAFE 仅引用既有 source |
| TSC / SwRS | **禁止**写技术安全机制或软件需求终稿 |
| ASPICE 评估 | 不能写「SYS.2 已满足」「Level X 达成」 |

本步是流程入口，对应 **阶段 0：启动与范围对齐**。

### 阶段 0 · 启动与范围对齐（本步执行）

1. **明确 SyRS 边界**：本 ECU 控制器 vs 整车级；避免与 OEM 整车 SyRS 混写。
2. **确定读者**：系统工程师、软件/硬件负责人、功能安全接口人、客户接口人。
3. **收集输入**，标注 role；登记缺失（如无 SWRS → gap）。
4. **声明非目标**：不写 HARA/FSR/TSC/SwRS 终稿；不写批准/合规结论。

### 要回答的问题（本步须为后续奠基）

| 问题 | 对应内容 | 本步动作 |
|---|---|---|
| 本文档范围是什么？ | 适用 ECU、变型、不含 HARA/TSC | task_brief 声明 |
| 基于哪些输入？ | SWRS、RFQ、架构、接口 | 登记 source |
| 每条 SYS-xx 追溯哪个上游需求？ | SWRS/RFQ 链接 | 登记 swrs_source 等 |
| 还缺什么？ | 开放项 | `knowledge_gaps` |

### 输入材料（事实来源）

| 类别 | 典型文档 | role | 用途 |
|---|---|---|---|
| 客户需求 | swrs_source.md、rfq.md | source | 干系人需求、功能描述 |
| 架构 | system_architecture.md | source | 边界、子系统上下文 |
| 接口 | interface_spec.md、can_matrix | source | SYS-IF-xx、方向 |
| 环境/场景 | odd_scenarios.md | source | SEC-ENV、工况 |
| 诊断 | diagnostic_spec.md | source | SEC-DIAG |
| 安全输入 | fsr_source.md（若有） | source | SEC-SAFE **引用** |
| SyRS 模板 | syrs_template.md | template | 章节与表列结构 |
| 检查清单 | syrs_checklist.md、aspice_sys2 | checklist | SYS.2 完备性 |
| 方法学 | syrs_reference.md | reference | 写法（**不证明项目事实**） |
| 参考 SyRS | reference_syrs_sample.md | sample | **仅**章节/表格形状 |

**原则**：`fact source ≠ sample`；reference 不能证明本项目 SYS-xx/限值。

## 本步 Review / Checklist 要点

### 全局原则（本步须落实登记）

| 原则 | 说明 |
|---|---|
| 追溯锚点 | 每条 SYS-xx 须链到 **本项目 source** 中的上游需求 |
| 事实来源 | 仅 T0/T1；sample/reference **不能**支撑 SYS-xx/限值 |
| 安全边界 | SEC-SAFE 仅引用 FSR/SG source，非新 HARA |
| 功能安全/架构 | 禁止 HARA/TSR/TSC/SwRS 终稿 |
| 措辞/交付 | 禁止批准/ASPICE 合规/量产；交付为 review-ready |

### 输入分类登记 Checklist（七大类 + 安全输入）

| 类别 | 典型材料 | role | 必检字段 | 用于章节 |
|---|---|---|---|---|
| 客户需求 | swrs_source、rfq、客户纪要 | source | 文档版本、客户方 | SEC-STAKE / SEC-FUNC |
| 法规/型式认证 | regulatory_list | source / reference | 法规编号与适用范围 | SEC-LEGAL |
| 架构 | system_architecture | source | 适用 ECU 边界 | SEC-IDENT / SEC-FUNC |
| 接口 | interface_spec、CAN 矩阵 | source | 含方向标记 | SEC-IF |
| 诊断 | diagnostic_spec | source | DTC 范围 | SEC-DIAG |
| 安全输入（可选） | fsr_source、SG 清单 | source | 仅作 SEC-SAFE 引用，**非新 HARA** | SEC-SAFE |
| 标定/平台约束 | calibration_constraints | source | 平台版本 | SEC-ASSUMP |
| 模板/检查 | syrs_template、aspice_sys2_checklist | template/checklist | `is_fact_source=false` | 结构/审查 |
| 方法学 | iso26262_part3_excerpt、aspice_guidance | reference | `is_fact_source=false` | T3 |
| 参考 SyRS（仅 With-Reference） | reference_syrs | **sample** | `is_fact_source=false` | 仅形状 |

### 通用 Checklist（每次 run 必查）

- [ ] `task_type: SystemRequirement` 已确认
- [ ] manifest 每份输入：file_id、path、title、format、role 齐全
- [ ] 每份 source 标注 `is_fact_source=true`；template/checklist/reference/sample 标 `false`
- [ ] **swrs_source / rfq 至少一份**（P0：若全无且无 HITL，禁止开跑）
- [ ] 接口规范登记或 gap（影响 SEC-IF Direction 列）
- [ ] 诊断规范登记或 gap（影响 SEC-DIAG）
- [ ] 法规/标定/平台约束登记或在 task_brief 显式声明不适用
- [ ] 安全输入：若有 `fsr_source` 须 notes 标明「**仅供 SEC-SAFE 引用，不做新 HARA**」
- [ ] task_brief 显式列出 critical claim 列表与对应 `requires_human_confirmation`
- [ ] 缺失项写入 `knowledge_gaps.md`，不静默跳过
- [ ] task_brief 显式声明：**非** HARA/FSR/TSC/SwRS 终稿、**非** ASPICE/ISO 26262 合规认证

### ASPICE / ISO 26262 接口准备 Checklist

- [ ] **ASPICE SYS.2 BP1**：客户/干系人需求材料齐全或登记 gap（无则 SEC-STAKE 不可成稿）
- [ ] **ASPICE SYS.2 BP5**：上游 ID 命名规则在 task_brief 中固定（如 SWRS-xxx → SYS-F-xx）
- [ ] **ISO 26262-3 §5（下游 IDD 接口）**：SyRS 须覆盖 IDD 所需的功能、边界、接口、工况源材料
- [ ] **ISO 26262-3 §7（下游 FSR 接口）**：若有 FSR 上游材料须登记，仅作 SEC-SAFE 引用
- [ ] **ISO 26262-4（下游 TSC/系统设计接口）**：本 SyRS **不写**技术安全机制/TSR；登记界面在 task_brief

### From-Scratch 专属 Checklist

- [ ] 无参考 SyRS 时不得将历史项目文档悄悄登记为 sample
- [ ] 客户需求版本号、日期、签发方明确登记
- [ ] 缺口（无诊断/无接口/无平台）显式登记，不试图用 reference 补
- [ ] critical claim 列表预期大量 `NEEDS_USER_CONFIRMATION`

### With-Reference 专属 Checklist

- [ ] 参考项目 SyRS **必须** `role=sample`，**P0** 不得标 source
- [ ] 参考 SyRS 与本项目 SWRS **分 file_id 登记**，不得合并
- [ ] task_brief notes 明确：**参考 SyRS 仅作结构/列定义参考，需求事实来源不变**
- [ ] task_brief 预声明 **SEC-DIFF（Δ-Analysis）** 章节
- [ ] 平台/变型差异类别（接口/诊断/性能/法规）在 task_brief 列出，供后续 Δ 任务参考

### 本步 Review 要点（双情景对比）

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 上游 source 完备性 | 缺即 gap，不得用 reference 补 | 参考 SyRS **不能**替代 SWRS source |
| sample 边界 | 若有 sample，仅形状 | 参考 SyRS **不得**升格为 source（P0） |
| 安全输入处理 | 通常无 FSR 输入 → SEC-SAFE 留 open | 参考 SyRS 的 SEC-SAFE 内容不可照抄 |
| manifest 完整性 | role/tier/file_id 齐全 | 参考与本项目 source **分 file_id 登记** |
| HITL 预声明 | 大量 critical claim 须 HITL | Δ 项决策须 HITL |

### 常见 P0（本步重点防）

| 错误 | 后果 |
|---|---|
| 无 SWRS / RFQ 且无 gap 开跑 | 无追溯锚点；后续整条流水线作废 |
| sample / 参考 SyRS 标为 source | 事实来源违规；下游 ASPICE 审计失败 |
| reference 标为 SWRS 事实 | tier 违规 |
| fsr_source 被默认升级为新 HARA 判断依据 | 文档类型漂移 |
| 参考 SyRS 与本项目 SWRS 同 file_id 合并登记 | 证据可追溯性丧失 |

### 常见 P1

- 客户文档无版本号 → 后续 review 难以判定 freshness
- 法规清单缺适用范围 → SEC-LEGAL 范围不清
- 平台/芯片版本未登记 → SEC-ASSUMP 假设无源

## A1 / A2 / B

**A1**：manifest 完整；sample/reference `is_fact_source=false`；SWRS source 或 gap 已处理；ASPICE BP1 输入齐全或显式 gap。  
**A2**：补登材料、修正 role、登记 gap、补 task_brief 中的 critical claim 声明。  
**B**：核对 role/tier/gap；sample 未升格为 source；与 IDD/FSR/TSC 的接口在 task_brief 显式列出。
