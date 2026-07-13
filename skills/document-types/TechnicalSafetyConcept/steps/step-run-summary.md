# TSC 子 skill · Step 12 · 运行总结

骨架：`skills/workflow-steps/step-run-summary/SKILL.md`。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点

- 生成 `run_summary.md`、`session_trace.jsonl`、`hitl_decisions.jsonl`、`reusable_patterns.md`。
- 中性叙事；可复用模式**不含**具体 TSR/机制/ASIL 事实。

## TSC 方法论（本步定位）

本步对应 **追溯与学习**；对本次 TSC run 做中性总结。

### 8 工程阶段 ↔ 13 step 完整映射

| 工程阶段 | workflow step | 本 run 摘要字段 |
|---|---|---|
| 阶段 0：启动与范围对齐 | Step 1 | scope_gaps |
| 阶段 1：输入清点与来源分级 | Step 2 | tier_compliance |
| 阶段 2：架构与安全元素识别 | Step 3–4 | arch_element_gaps |
| 阶段 3：FSR→TSR 派生 | Step 5–7 | tsr_derivation_gaps |
| 阶段 4：安全机制与故障处理 | Step 5–7 | mech_fault_gaps |
| 阶段 5：接口与 ASIL 分解 | Step 5–7 | iface_asil_gaps |
| 阶段 6：追溯矩阵与验证计划 | Step 6–7 | trace_verif_gaps |
| 阶段 7：评审与独立审查 | Step 8–9 | review_findings |
| 阶段 8：定稿与下游交接 | Step 10–11 | handoff_notes |

### 完整过程回顾（本 run 映射）

| 工程阶段 | step | stage |
|---|---|---|
| 阶段 0：启动对齐 | Step 1 | ingest |
| 阶段 1：材料与索引 | Step 2–3 | ingest |
| 阶段 2：定大纲 | Step 4 | outline |
| 阶段 3：写作计划 | Step 5 | evidence_planning |
| 阶段 4：证据·引用·任务 | Step 6 | evidence_planning |
| 阶段 5：成稿 | Step 7 | draft |
| 阶段 6：审查与验证 | Step 8–9 | review |
| 阶段 7：修订与交付 | Step 10–11 | finalize |
| 学习 | Step 12–13 | learning |

### 过程总览（叙事）

```
上游（Item 定义、HARA/SG、FSR 确认、系统架构）
  → 准备（FSR/SG/架构 source、材料分类与 gap）
  → 规划（大纲、写作计划、追溯矩阵）
  → 撰写（架构、TSR-xx、机制、故障处理、追溯）
  → 质量（追溯/tier/无 HSC/SSC 审查、验证修订、review-ready）
  → HSC/SSC 概念阶段（deferred，非本 run）
```

### gap 分类（Clause 8 对齐）

| 分类 | 典型 gap |
|---|---|
| SEC-FSR | FSR source 不全 |
| SEC-ARCH | 架构 source 缺失 |
| SEC-TSR | FSR→TSR 派生依据不足 |
| SEC-MECH | 机制落点/检测概念无 source |
| SEC-FAULT | FTTI/故障处理无 HARA 依据 |
| SEC-ASIL | ASIL 继承/分解无 source |
| SEC-VERIF | 验证方法无依据 |
| HSC/SSC 泄漏 | 草稿误含 HSC/SSC（应修订） |

### 与 FSR 对比（流程级备忘）

| 维度 | FSR | TSC |
|---|---|---|
| 标准 | Part 3 Clause 7（FSC） | Part 4 Clause 8 |
| 核心产出 | FSR-xx、SG 追溯、ASIL | TSR-xx、机制、架构分配、追溯矩阵 |
| 上游 | SG、HARA 摘要、IDD | FSR、SG、架构、HARA/FTTI |
| 禁止 | TSC、批准终论 | HSC/SSC、批准终论、FSR 复述 |

### 一句话归纳（写入 summary）

**Checklist 核心**：每条 TSR 链 FSR/SG、有架构分配、机制一致、FTTI 有来源、无 HSC/SSC、无批准措辞。  
**Review 核心**：追溯一致、tier 合规、sample 未当事实、缺口显式。

## 本步 Review / Checklist 要点

### 本步 Checklist

- [ ] Step 8/9 结论摘要已记录
- [ ] gap 按 **SEC-FSR / SEC-ARCH / SEC-TSR / SEC-MECH / SEC-FAULT** 分类
- [ ] 可复用模式**不含** TSR/机制/ASIL 事实
- [ ] `document_status` 保守
- [ ] **With-Reference 额外**：记录「参考 TSC 误用风险」是否出现（流程信号，**非**需求事实）

### 情景差异

| 维度 | With-Reference 额外 |
|---|---|
| 流程信号 | 参考 TSC 是否被误标 source / 渗入 matrix / 无 Δ 节等 |

## A1 / A2 / B

**A1**：无批准语义；gap 已分类。  
**A2**：补 trace/HITL。  
**B**：summary 与 TSC 边界一致。
