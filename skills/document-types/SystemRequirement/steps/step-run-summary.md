# SyRS 子 skill · Step 14 · 运行总结

骨架：`skills/workflow-steps/step-run-summary/SKILL.md`。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点

- 生成 `run_summary.md`、`session_trace.jsonl`、`hitl_decisions.jsonl`、`reusable_patterns.md`。
- 中性叙事；可复用模式**不含**具体 SYS-xx/接口/限值事实。

## SyRS 方法论（本步定位）

本步对应 **追溯与学习**；对本次 SyRS run 做中性总结。

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
上游（SWRS、RFQ、架构、接口规范）
  → 准备（材料分类与 gap）
  → 规划（大纲、写作计划、追溯矩阵）
  → 撰写（SYS-F、SYS-IF、性能/环境/诊断、追溯）
  → 质量（追溯/tier/无 HARA 审查、验证修订、review-ready）
  → 下游（IDD、SYS.3、FSR 链 … 非本 run）
```

### gap 分类（SYS.2 对齐）

| 分类 | 典型 gap |
|---|---|
| SEC-STAKE | SWRS 不全 |
| SEC-FUNC | 功能需求分解依据不足 |
| SEC-IF | 接口方向/对端缺失 |
| SEC-PERF | 性能限值无 source |
| SEC-ENV | 环境约束无 source |
| SEC-DIAG | 诊断规范缺失 |
| SEC-TRACE | 上游 ID 映射不全 |
| SEC-VERIF | 验证方法无依据 |
| HARA 泄漏 | 草稿误含 HARA/ASIL（应修订） |

### 与 IDD 对比（流程级备忘）

| 维度 | IDD | SyRS |
|---|---|---|
| 标准 | ISO 26262-3 §5 | ASPICE SYS.2 |
| 核心产出 | F-xx、边界、IF | SYS-F、SYS-IF、追溯矩阵 |
| 上游 | SyRS（对 IDD） | SWRS/RFQ（对 SyRS） |
| 禁止 | hazard、ASIL、SG | HARA、TSR、TSC、批准终论 |

### 一句话归纳（写入 summary）

**Checklist 核心**：每条 SYS-xx 链上游、接口有方向、验证显式、无 HARA/TSR、无批准措辞。  
**Review 核心**：追溯一致、tier 合规、sample 未当事实、缺口显式。

## 本步 Review / Checklist 要点

### run_summary.md 强制字段 Checklist

- [ ] **§1 Run metadata**：run_id、task_type、document_status、start/end timestamp、operator（HITL 操作者标识或匿名）
- [ ] **§2 输入概览**：source / template / checklist / reference / sample 计数；sample file_id 显式列出
- [ ] **§3 阶段映射**：13 step 状态（done / skipped / failed）与 artifact 链接
- [ ] **§4 关键统计**：SYS-F / SYS-IF / SEC-PERF / SEC-DIAG 条数；NEEDS_USER_CONFIRMATION 数；EVD 数；HITL 决策数
- [ ] **§5 gap 分类**：按 SEC-* 分类统计
- [ ] **§6 P0 / P1 关闭情况**：Step 10 / 11 findings 关闭状态
- [ ] **§7 流程信号**：本 run 出现的风险（如「参考 SyRS 险被升格 source」「Direction 列大面积 open」）
- [ ] **§8 与 SyRS 边界一致性声明**：非批准、非合规

### artifact 链接 Checklist

- [ ] `trace/session_trace.jsonl`：每步开始/结束、artifact 写入、HITL 触发记录
- [ ] `trace/hitl_decisions.jsonl`：每条 HITL 决策含 `decision_id`、`question`、`decision`、`actor`、`timestamp`、`evidence_or_basis`
- [ ] `learning/reusable_patterns.md`：仅含**流程/写法**模式（如「SYS-IF Direction 缺失高发」），**不含**具体需求/接口/限值事实
- [ ] artifact 链接（相对路径）在 run_summary 可点击

### gap 分类 Checklist（SYS.2 对齐）

| 分类 | 典型 gap | 统计字段 |
|---|---|---|
| SEC-STAKE | 客户/RFQ 不全 | `gap_stake_count` |
| SEC-FUNC | 功能分解依据不足 | `gap_func_count` |
| SEC-IF | 接口方向/对端缺失 | `gap_if_direction_count` |
| SEC-PERF | 性能限值无 source | `gap_perf_count` |
| SEC-ENV | 环境约束无 source | `gap_env_count` |
| SEC-DIAG | 诊断规范缺失 | `gap_diag_count` |
| SEC-SAFE | FSR/SG 输入缺失 | `gap_safe_count` |
| SEC-TRACE | 上游 ID 映射不全 | `gap_trace_count` |
| SEC-VERIF | 验证方法无依据 | `gap_verif_count` |
| HARA/TSR 泄漏 | 草稿误含；修订是否关闭 | `forbidden_leak_count`（应为 0） |

### 流程信号 Checklist（中性叙述，**不含**项目事实）

- [ ] **Sample 升格风险**：是否出现 sample/参考 SyRS 被误标 source 的修正记录
- [ ] **Direction 列**：SYS-IF Direction 缺失/重新确认的次数
- [ ] **HITL 频次**：哪些章节 HITL 最密集
- [ ] **Forbidden 措辞清洗**：Step 11/12 触发的 forbidden 词条数与位置
- [ ] **With-Reference**：参考 SyRS 误用迹象（误标 source / 渗入 matrix / Δ 缺失）次数

### reusable_patterns.md 规则 Checklist

- [ ] **可写入**：流程教训、checklist 改进点、Δ-Analysis 方法学
- [ ] **不可写入**：具体 SYS-F 措辞、接口数值、限值、客户 ID、ECU 标识
- [ ] **不可写入**：本项目 OEM/客户名（除非已 HITL 同意）

### ASPICE / ISO 维度 Checklist

- [ ] **ASPICE SYS.2 BP4**：客户沟通 open 项在 §5 / §6 体现
- [ ] **ASPICE SYS.2 BP5**：双向追溯统计（上游孤儿、SyRS 孤儿）
- [ ] **ISO 26262 接口**：SEC-SAFE gap 是否在 §5 记录
- [ ] 状态枚举与 final_report 一致；无 approved / compliant

### From-Scratch 专属 Checklist

- [ ] §5 gap 计数较大属预期；§7 信号注明「初版 SyRS gap 多为正常」
- [ ] HITL 决策预期数量大；§4 HITL 数与 §6 P0 关闭数交叉一致

### With-Reference 专属 Checklist

- [ ] §7 必含「参考 SyRS 误用风险」段：曾否被升格 / 是否进 matrix / Δ-Analysis 是否齐全
- [ ] §4 含 Δ 统计：Added / Removed / Modified / Renamed / Scope-changed
- [ ] reusable_patterns 可写 Δ-Analysis **方法学**，**不**写本次 Δ 具体内容

### 双情景 Review 重点对比

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| §5 gap 计数 | 多正常 | 也可多，但应有更多 conservative_candidate 完成项 |
| §7 流程信号 | 重点防静默填值 | 重点防参考 SyRS 渗入 |
| reusable_patterns | 流程教训 | 加 Δ-Analysis 方法学 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| run_summary 含批准/合规措辞 | 越权语义 |
| reusable_patterns 含具体 SYS-xx / 接口 / 限值 | 项目事实泄漏 |
| HITL pending 被记录为 confirmed 而无 decision 条目 | 控制失效 |
| 状态字段为 `approved` / `compliant` | 越权 |

### 常见 P1

- §4 计数与 final_report 不一致
- §3 step 状态有 done 但无 artifact 链接
- HITL decisions 缺 `actor` 字段

## A1 / A2 / B

**A1**：无批准语义；gap 已分类；artifact 链接齐全。  
**A2**：补 trace / HITL / §7 信号。  
**B**：summary 与 SyRS 边界一致；reusable_patterns 无项目事实。
