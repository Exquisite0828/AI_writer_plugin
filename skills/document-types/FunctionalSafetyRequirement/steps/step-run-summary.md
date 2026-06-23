# FSR 子 skill · Step 14 · 运行总结

骨架：`skills/workflow-steps/step-run-summary/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点

- 生成 `run_summary.md`、`session_trace.jsonl`、`hitl_decisions.jsonl`、`reusable_patterns.md`。
- 中性叙事；可复用模式**不含**具体 FSR/SG 事实。

## FSR 方法论（本步定位）

本步对应 **追溯与学习**；对本次 FSR run 做中性总结。

### 完整过程回顾（本 run 映射）

| 工程阶段 | step | stage |
|---|---|---|
| 阶段 0：启动对齐 | Step 1 | ingest |
| 阶段 1：材料与索引 | Step 2–3 | ingest |
| 阶段 2：定大纲 | Step 4 | outline |
| 阶段 3：写作计划 | Step 5 | evidence_planning |
| 阶段 4：证据·引用·任务 | Step 6 | evidence_planning |
| 阶段 5：成稿 | Step 9 | draft |
| 阶段 6：审查与验证 | Step 10–11 | review |
| 阶段 7：修订与交付 | Step 12–13 | finalize |
| 学习 | Step 14–15 | learning |

### 过程总览（叙事）

```
上游（Item 定义、HARA/SG 确认）
  → 准备（SG 与追溯 source、材料分类与 gap）
  → 规划（大纲、写作计划、SG 追溯矩阵）
  → 撰写（SG 追溯、FSR-xx、ASIL、验证方法）
  → 质量（追溯/tier/无 TSC 审查、验证修订、review-ready）
  → TSC 概念阶段（deferred，非本 run）
```

### gap 分类（Clause 7 对齐）

| 分类 | 典型 gap |
|---|---|
| SEC-SG | SG source 不全 |
| SEC-FSR | 需求分解依据不足 |
| SEC-ASIL | ASIL 继承无 source |
| SEC-VERIF | 验证方法无依据 |
| TSC 泄漏 | 草稿误含 TSC（应修订） |

### 与 IDD 对比（流程级备忘）

| 维度 | IDD | FSR |
|---|---|---|
| 标准 | Clause 5 | Clause 7（FSC） |
| 核心产出 | F-xx、边界、IF | FSR-xx、SG 追溯、ASIL |
| 禁止 | hazard、ASIL、SG | TSC、批准终论 |

### 一句话归纳（写入 summary）

**Checklist 核心**：每条 FSR 链 SG、ASIL 有来源、验证显式、无 TSC、无批准措辞。  
**Review 核心**：追溯一致、tier 合规、sample 未当事实、缺口显式。

## 本步 Review / Checklist 要点

### 本步 Checklist

- [ ] Step 10/11 结论摘要已记录
- [ ] gap 按 **SEC-SG / SEC-FSR / SEC-ASIL / SEC-VERIF** 分类
- [ ] 可复用模式**不含** FSR/SG 事实
- [ ] `document_status` 保守
- [ ] **With-Reference 额外**：记录「参考 FSR 误用风险」是否出现（流程信号，**非**需求事实）

### 情景差异

| 维度 | With-Reference 额外 |
|---|---|
| 流程信号 | 参考 FSR 是否被误标 source / 渗入 matrix / 无 Δ 节等 |

## A1 / A2 / B

**A1**：无批准语义；gap 已分类。  
**A2**：补 trace/HITL。  
**B**：summary 与 FSR 边界一致。
