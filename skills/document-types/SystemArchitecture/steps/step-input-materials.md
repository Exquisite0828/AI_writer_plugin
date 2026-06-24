# System Architecture 子 skill · Step 1 · 输入材料

骨架：`skills/workflow-steps/step-input-materials/SKILL.md`（`task_type: SystemArchitecture`）。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点

- 创建 `runs/<run_id>/`，写入 manifest、`task_brief`；确认 `task_type: SystemArchitecture`。
- 登记 task.yaml 每份输入：`file_id`、path、title、format、`role`。
- **source**：SyRS、系统上下文、接口规范、平台约束、诊断说明、既有 FSR/TSC 摘要（若有）→ `is_fact_source=true`。
- **template**：架构模板 → T2。
- **checklist / reference**：SYS.3 检查项、ASPICE/ISO 写法参考 → T2/T3，`is_fact_source=false`。
- **sample**：参考架构文档 → T4，**仅形状**。
- 声明 System Architecture critical claims 须 `requires_human_confirmation`。
- **底线**：不得把 sample 中的架构元素/接口/分配当作本项目事实；不得把 reference 当架构事实。

## System Architecture 方法论（本步定位）

### 1.1 开发与标准语境中的位置

```text
干系人/客户需求（SWRS、RFQ、法规）
    ↓
System Requirement / SyRS（SYS.2）
    ↓
System Architecture（SYS.3）← 本类型
    ↓
├─→ Item Definition / HARA / FSR（下游功能安全接口）
├─→ TSC（若已有安全上游输入）
└─→ SwRS / HwRS / 详细设计
```

**System Architecture 核心作用**：把控制器产品「如何被拆分成可理解、可分配、可验证的架构元素，元素之间如何交互，需求如何分配到元素与接口」写成 **可追溯、可验证、可审查** 的架构条目。

### 1.2 本仓库定位

- document-type skill 层，走统一 **13 步** workflow。
- 产出 **review-ready** System Architecture 候选包，**不是**架构批准书、ASPICE 评估通过或 ISO 26262 合规认证。
- **明确不做**：HARA、FSR 新编、TSC 终稿、SwRS/HwRS 终稿。

### 1.3 重要边界

| 文档 | System Architecture 与之关系 |
|---|---|
| SyRS | 上游：需求分解与元素分配锚点 |
| Item Definition | 下游：可反向引用架构边界，但本类型不输出 IDD |
| HARA / FSR | **禁止**写危害、ASIL、SG、FSR 新结论 |
| TSC | 仅可在 SEC-SAFE-ARCH 引用已有约束，**不**写 TSR/机制终稿 |
| SwRS / HwRS | 下游；本类型不写软件/硬件需求终稿 |
| ASPICE 评估 | 不能写「SYS.3 已满足」「Level X 达成」 |

本步是流程入口，对应 **阶段 0：启动与范围对齐**。

### 阶段 0 · 启动与范围对齐（本步执行）

1. **明确架构边界**：本 ECU 控制器 / 子系统架构 vs 整车 E/E 架构。
2. **确定读者**：系统架构师、系统工程师、软件/硬件负责人、功能安全接口人。
3. **收集输入**，标注 role；登记缺失（如无 SyRS → gap）。
4. **声明非目标**：不写 HARA/FSR/TSC/SwRS 终稿；不写批准/合规结论。

### 要回答的问题（本步须为后续奠基）

| 问题 | 对应内容 | 本步动作 |
|---|---|---|
| 本文档范围是什么？ | 适用 ECU、变型、边界、不含 TSC/SwRS | task_brief 声明 |
| 基于哪些输入？ | SyRS、接口规范、平台约束 | 登记 source |
| 每条架构分配追溯哪个上游需求？ | SyRS requirement linkage | 登记 syrs_source |
| 还缺什么？ | 开放项 | `knowledge_gaps` |

## 本步 Review / Checklist 要点

### 通用 Checklist

- [ ] `task_type: SystemArchitecture` 已确认
- [ ] manifest 每份输入：file_id、path、title、format、role 齐全
- [ ] 至少有 1 份 `syrs_source` 或等价上游系统需求 source（**P0** 若全无且无 HITL）
- [ ] 接口规范、平台约束、诊断说明登记或 gap
- [ ] system_architecture_template / checklist / reference → `is_fact_source=false`
- [ ] 参考架构文档（若有）→ `role=sample`，`is_fact_source=false`
- [ ] task_brief 明示：**非** HARA / FSR / TSC / SwRS / HwRS 终稿、**非** ASPICE / ISO 合规认证
- [ ] 缺失项写入 `knowledge_gaps.md`，不静默跳过

### ASPICE / ISO 26262 接口准备 Checklist

- [ ] **ASPICE SYS.3**：上游 SyRS / System Requirement 材料齐全或登记 gap
- [ ] **ASPICE SYS.3**：接口、资源、诊断 source 至少部分存在
- [ ] **ISO 26262-3 §5 接口**：架构边界可供下游 IDD / HARA 参考
- [ ] **ISO 26262-3 / 4 接口**：若有 FSR / TSC 输入，仅作 SEC-SAFE-ARCH 引用

### From-Scratch 专属 Checklist

- [ ] 无参考架构文档时不得把历史项目文档悄悄登记为 sample
- [ ] 上游 SyRS 版本、日期、签发方明确登记
- [ ] 缺口（无接口/无平台/无诊断）显式登记，不试图用 reference 补

### With-Reference 专属 Checklist

- [ ] 参考架构文档 **必须** `role=sample`，**P0** 不得标 source
- [ ] 参考架构文档与本项目 SyRS / 接口规范 **分 file_id 登记**
- [ ] task_brief notes 明确：**参考架构文档仅作结构/图表参考，架构事实来源不变**
- [ ] task_brief 预声明 **SEC-DIFF（Δ-Analysis）** 章节

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 上游 source 完备性 | 缺即 gap，不得用 reference 补 | 参考架构 **不能**替代 SyRS source |
| sample 边界 | 若有 sample，仅形状 | 参考架构 **不得**升格为 source（P0） |
| 安全输入处理 | 通常无 TSC 输入 → SEC-SAFE-ARCH 留 open | 参考架构中的安全机制不可照抄 |
| manifest 完整性 | role/tier/file_id 齐全 | 参考与本项目 source **分 file_id 登记** |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 无 SyRS 且无 gap 开跑 | 无分配与追溯锚点 |
| sample/参考架构标为 source | 事实来源违规 |
| 把 reference 标为架构事实 | tier 违规 |

## A1 / A2 / B

**A1**：manifest 完整；sample/reference `is_fact_source=false`；SyRS source 或 gap 已处理。  
**A2**：补登材料、修正 role、登记 gap。  
**B**：核对 role/tier/gap；sample 未升格为 source。
