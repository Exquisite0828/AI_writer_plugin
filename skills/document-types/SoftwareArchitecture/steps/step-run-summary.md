# Software Architecture 子 skill · Step 14 · 运行总结

骨架：`skills/workflow-steps/step-run-summary/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点

- 生成 `run_summary.md`、`session_trace.jsonl`、`hitl_decisions.jsonl`、`reusable_patterns.md`。
- 对本次 SwAD run 做 **中性** 过程总结，供流程改进，不含项目架构事实。

## Software Architecture 方法论（本步定位）

### 14.1 本步在八阶段方法链中的位置

本步对应 **阶段 8：追溯与学习**。方法论目标是回答：

1. 本次 run 走了哪种情景（from_scratch / with_reference）？
2. 哪些 SEC 缺口最密集？
3. 哪些流程信号值得进入 candidate profile（Step 15）？

**方法原则**：run_summary 描述 **过程**，不固化 **产品架构事实**。

### 14.2 阶段 8 · 运行总结方法

#### run_summary 叙事结构（建议顺序）

```text
1. Run 元信息（run_id、task_type、writing_scenario、状态、时间）
2. 输入概览（source/template/sample 计数）
3. 13 步执行映射（每步状态 + artifact 链接）
4. 关键统计（组件/接口/分配/open/HITL 数）
5. gap 按 SEC 分类表
6. P0/P1 关闭情况
7. 流程信号（见下表）
8. 边界一致性声明（非批准、非合规）
```

#### 流程信号（Software Architecture 特有）

| 信号 | 含义 | 后续动作 |
|---|---|---|
| swrs_gap_dense | SEC-UPTRACE/ALLOC gap 多 | 提示补 SwRS 后再跑 |
| direction_missing_dense | SEC-IF Direction open 多 | 提示补接口规范 |
| resource_pending_dense | SEC-RES 全 pending | 提示补平台/OS 配置 |
| reference_misuse_risk | With-Reference 且曾出现 sample 进 matrix | 加强 Step 6 检查 |
| hitl_pending_blocked | 阻断性 HITL 未决 | 状态 blocked |
| safe_arch_all_open | 无 TSR 输入 | 正常，记入说明 |

#### gap 分类表（写入 run_summary）

| SEC | 典型 gap |
|---|---|
| SEC-UPTRACE | SwRS 不全 |
| SEC-LOGARCH | 逻辑分解依据不足 |
| SEC-PHYSARCH | 任务/BSW 信息缺失 |
| SEC-IF | 接口方向/对端缺失 |
| SEC-ALLOC | 分配理由无 source |
| SEC-DIAG | 诊断链路缺失 |
| SEC-RES | 资源/时序预算无 source |
| SEC-SAFE-ARCH | TSR/软件安全约束缺失 |
| SEC-DIFF | With-Reference 下 Δ 不完整 |

#### From-Scratch 总结要点

- 注明「初版 SwAD gap 密集为预期」。
- 统计 open 密度，不作为质量失败依据。
- reusable_patterns 可提炼：输入完备性检查、Direction 列强制等。

#### With-Reference 总结要点

- 必含「历史 SwAD 误用风险」评估段。
- Δ 统计：Added / Removed / Modified / Scope-changed 各多少行。
- reusable_patterns 可写 Δ-Analysis 方法学，**不写**本次具体差异内容。

### 14.3 reusable_patterns 可写 / 不可写

| 可写 | 不可写 |
|---|---|
| SWE.2 检查项模板 | 本项目 SWA-COMP 名称 |
| Direction 列验证规则 | 本项目任务周期值 |
| Δ-Analysis 列定义 | 本次具体 Δ 条目 |
| From-Scratch open 密度说明 | 客户「沿用参考」的具体决定 |

## 本步 Review / Checklist 要点

### run_summary 强制字段 Checklist（12 项）

- [ ] run_id、task_type、`writing_scenario`、document_status
- [ ] start/end timestamp
- [ ] 输入概览：source/template/checklist/reference/sample 计数
- [ ] 13 步状态映射与 artifact 链接
- [ ] 关键统计：组件数、接口数、分配行数、open 数、HITL 数
- [ ] gap 按 SEC-* 分类表（见下）
- [ ] P0/P1 关闭情况摘要
- [ ] 流程信号段（direction_missing、reference_misuse 等）
- [ ] 边界声明：非批准、非 ASPICE/ISO 合规认证
- [ ] `session_trace.jsonl` 与 13 步事件一致
- [ ] `hitl_decisions.jsonl` 与 manifest/HITL 一致
- [ ] 全文无 approved/compliant/量产措辞

### gap 分类 Review 表

| SEC | 典型 gap | 记入 run_summary |
|---|---|---|
| SEC-UPTRACE | SwRS 不全 | 是 |
| SEC-LOGARCH | 逻辑分解不足 | 是 |
| SEC-PHYSARCH | 任务/BSW 缺失 | 是 |
| SEC-IF | Direction/对端缺失 | 是 |
| SEC-ALLOC | 分配理由无 source | 是 |
| SEC-DIAG | 诊断链路缺失 | 是 |
| SEC-RES | 资源预算无 source | 是 |
| SEC-SAFE-ARCH | TSR 缺失 | 是 |
| SEC-DIFF | With-Reference Δ 不完整 | 是 |

### 流程信号 Checklist

- [ ] `swrs_gap_dense` — 若 SEC-UPTRACE/ALLOC gap 多，已记录
- [ ] `direction_missing_dense` — 若 SEC-IF open 多，已记录
- [ ] `resource_pending_dense` — 若 SEC-RES 全 pending，已记录
- [ ] `reference_misuse_risk` — With-Reference 且曾 sample 进 matrix 时必记
- [ ] `hitl_pending_blocked` — 阻断性 HITL 未决时标 blocked

### reusable_patterns 边界 Checklist

- [ ] **可写**：SWE.2 检查项、Direction 规则、Δ 列定义、open 密度说明
- [ ] **不可写**：SWA-COMP 名、任务周期值、本次 Δ 具体内容、客户沿用决定

### From-Scratch 专属 Checklist

- [ ] 注明「初版 SwAD gap 密集为预期」
- [ ] open 密度与 SEC 分类一致
- [ ] 无「参考误用风险」段（或注明 N/A）

### With-Reference 专属 Checklist

- [ ] 必含「历史 SwAD 误用风险」评估段
- [ ] Δ 统计：Added/Removed/Modified/Scope-changed 行数
- [ ] reusable_patterns 仅方法学，无本次 Δ 事实

### 本步 Review 要点

| 维度 | 通过条件 |
|---|---|
| 中性叙事 | 描述过程，不评价「架构已通过」 |
| 完整性 | 12 强制字段 + gap 分类 + 流程信号 |
| 事实隔离 | patterns 无项目架构事实 |
| 情景一致 | writing_scenario 与全文叙述一致 |

### P0 失效项

| 错误 | 后果 |
|---|---|
| summary 含批准/合规语义 | 越权 |
| reusable_patterns 含组件/资源事实 | 项目泄漏 |
| 13 步状态与 artifact 不一致 | 追溯断裂 |

### 一句话归纳

**Checklist 核心**：run_summary 12 字段齐全、gap 按 SEC 分类、流程信号记录、无批准语义。  
**Review 核心**：From-Scratch 说明 open 预期；With-Reference 必评估参考误用风险与 Δ 统计。

## A1 / A2 / B

**A1**：中性叙事；gap 分类；无事实泄漏。  
**A2**：补 trace/HITL/流程信号。  
**B**：summary 与 SwAD 边界一致。
