# IDD 子 skill · Step 12 · 运行总结

骨架：`skills/workflow-steps/step-run-summary/SKILL.md`。领域规则：`skills/document-types/ItemDefinitionDocument/SKILL.md`。

## 本步目的要点

- 生成 `run_summary.md`、`session_trace.jsonl`、`hitl_decisions.jsonl`、`reusable_patterns.md`。
- **中性叙事**：材料处理、stage gate、HITL、gap 统计；不重下 Item 专业结论。
- 可复用模式：仅流程信号（如「接口方向列常缺」「误用节材料不足」），**不含**具体 F-xx 事实。
- 非交互 run 不伪造 HITL。

## IDD 方法论（本步定位）

本步对应流程 **追溯与学习** 环节，对本次 IDD 运行做中性总结，为后续 run 提供流程改进信号。

### IDD 完整过程回顾（本 run 映射）

| 工程阶段 | 仓库 step | stage |
|---|---|---|
| 阶段 0：启动与范围对齐 | Step 1 输入材料 | ingest |
| 阶段 1：材料消化与索引 | Step 2–3 清单/索引 | ingest |
| 阶段 2：定大纲 | Step 4 模板大纲 | outline |
| 阶段 3：逐段写作计划 | Step 5 大纲分析 | evidence_planning |
| 阶段 4：证据·引用·任务 | Step 6 证据映射 | evidence_planning |
| 阶段 5：撰写正文 | Step 7 保守草稿 | draft |
| 阶段 6：审查与验证 | Step 8–9 | review |
| 阶段 7：修订与交付 | Step 10–11 | finalize |
| 追溯与学习 | Step 12–13 | learning |

### 过程总览（叙事用）

```
准备（范围确认 → 收集材料 → 分类与缺口登记）
  → 规划（L1/L2 大纲 → 写作计划 → 证据映射与引用计划）
  → 撰写（F-xx / 边界 / 接口 / 环境·工况·假设·误用）
  → 质量（Clause 5 审查 → 验证与修订 → review-ready 交付）
  → HARA 概念阶段（交接，非本 run 执行）
```

### gap 统计建议分类（与 Clause 5 对齐）

| 分类 | 典型 gap 模式 |
|---|---|
| SEC-FUNC | SyRS 功能描述不全 |
| SEC-BOUNDARY | 架构缺 Out of scope |
| SEC-IF | 接口规范缺方向 |
| SEC-ENV | 环境约束材料缺失 |
| SEC-OPS | ODD/工况描述不足 |
| SEC-ASSUMP | 假设未显式文档化 |
| SEC-MISUSE | §5.4.4 b 材料缺失 |

## run_summary 建议节

1. 输入与 role 统计（source/template/sample 数量）
2. HITL 记录（或无 HITL 声明）
3. 知识缺口（按 SEC-FUNC/BOUNDARY/IF/MISUSE 等分类）
4. Stage gate 状态（ingest → outline → … → finalize）
5. 可复用 IDD 写作模式（流程级，无项目事实）
6. document_status（保守：`ready_for_human_review` / `finalized_with_open_items` / `blocked`）

### 可复用模式示例（禁止含项目事实）

- 「接口方向列常缺」→ 建议在 Step 4 L2 强制方向列
- 「误用节材料不足」→ 建议 Step 1 登记 gap 并 Step 6 标 confirmation_required
- 「边界仅 In 无 Out」→ 建议 Step 5 拆分 sp-bound-in / sp-bound-out

## 本步 Review / Checklist 要点

本步对本次 run 做中性总结；**不重下** Item 专业结论或审查批准语义。

### run_summary 须记录的审查相关项

- [ ] Step 8 审查结论摘要（checklist 覆盖度、P0/P1 数量）
- [ ] Step 9 验证 status（`passed_with_open_items` / `failed`，无 approved）
- [ ] gap 按 SEC-FUNC/BOUNDARY/IF/ENV/OPS/ASSUMP/MISUSE 分类统计
- [ ] HITL 记录完整（或无 HITL 声明）
- [ ] document_status 为保守表述
- [ ] 可复用模式**不含**具体 F-xx/边界事实

### 审查 gap 分类（与 Clause 5 对齐）

| 分类 | 典型 gap 模式 | Clause |
|---|---|---|
| SEC-FUNC | SyRS 功能描述不全 | §5.4.2 |
| SEC-BOUNDARY | 架构缺 Out of scope | §5.4.3 |
| SEC-IF | 接口规范缺方向 | §5.4.3 |
| SEC-ENV | 环境约束材料缺失 | §5.4.4 |
| SEC-OPS | ODD/工况描述不足 | HARA 输入 |
| SEC-ASSUMP | 假设未显式文档化 | §5.4.4 |
| SEC-MISUSE | §5.4.4 b 材料缺失 | §5.4.4 b |

### 一句话归纳（流程级，写入 summary）

**Checklist 核心**：Clause 5 七类内容齐全或有 open；接口有方向；边界 In/Out 双向；误用独立成节；全文无 HARA 内容。  
**Review 核心**：内容与 SyRS/架构一致、证据 tier 合规、sample 未当事实、缺口显式、措辞保守、结论不越权批准。

### 本步 Review 要点

| 维度 | 检查项 | 级别 |
|---|---|---|
| 中性叙事 | 无专业批准语义 | P0 |
| gap 分类 | 按 SEC 章分类列出 | P1 |
| 无事实泄漏 | 可复用模式不含 F-xx/边界值 | P0 |
| 状态保守 | document_status 非 approved | P0 |

## A1 / A2 / B

**A1**：无专业批准语义；gap 已按 Clause 5 章分类列出；无 F-xx/边界事实泄漏。  
**A2**：补 trace / HITL 记录。  
**B**：summary 与 IDD 边界一致；可复用模式不含项目事实。
