# SyRS 子 skill · Step 11 · 最终报告

骨架：`skills/workflow-steps/step-final-report/SKILL.md`。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点

- 打包 `final/final_report.md`、`final/delivery_summary.md`（review-ready，**非批准**）。
- conservative status：`ready_for_human_review` / `finalized_with_open_items` / `blocked_pending_confirmation`。

## SyRS 方法论（本步定位）

本步对应 **阶段 7 交付** 与 **阶段 8 下游交接（概念）**。

### 阶段 7 · 交付

1. 正文 + 追溯矩阵摘要 + open 清单 + 审查/验证摘要（**非 sign-off**）
2. 声明：**非 HARA/FSR/TSC/SwRS 终稿**、**非 SyRS 批准**、**非 ASPICE/ISO 26262 合规认证**

### 阶段 8 · 下游交接

| 交接物 | 说明 | 下游 |
|---|---|---|
| SYS-F-xx 功能需求表 | 系统功能基线 | Item Definition、SYS.3 架构 |
| SYS-IF-xx 接口需求表 | 含方向、对端 | 系统架构、接口设计 |
| 性能/环境/诊断需求 | 约束基线 | 详细设计、V&V |
| 追溯矩阵 | SWRS↔SyRS↔（预留架构/SwRS） | ASPICE SYS.2 BP5 |
| 验证方法候选 | V&V 规划输入 | 测试计划 |
| **open 项** | 下游**不得**悄悄闭合 | IDD、HARA、架构 |

```
SyRS 报告（ASPICE SYS.2）
    ↓（交接）
Item Definition / 系统架构（SYS.3）/ FSR 链 / SwRS …
```

### 交付包结构

1. 文档元信息与范围（非 HARA/TSC、非批准）
2. SyRS 正文（SEC-STAKE … SEC-FUNC … SEC-IF …）
3. 证据与追溯矩阵摘要
4. open / NEEDS_USER_CONFIRMATION 清单
5. 审查/验证结论摘要
6. 状态声明与下游说明

### 一句话总结

在已登记上游客户需求与项目 source 之下，用 **有来源、可追溯上游、接口有方向、验证方法显式、有 open 项** 的方式整理控制器 SyRS 候选包；**只组织系统层需求与追溯，不做 HARA/FSR/TSC，不做需求批准或 ASPICE/ISO 合规认证**。

### 触发方式（本仓库）

运行期只使用用户明确选择的 task file；本子 skill 不列出 demo task 路径。

`task_type: SystemRequirement` 加载本目录子 skill。

## 本步 Review / Checklist 要点

### 交付包结构 Checklist（`final/final_report.md`）

- [ ] **§1 文档元信息**：版本、状态、作者、修订历史；状态字段 ∈ {`ready_for_human_review`, `finalized_with_open_items`, `blocked_pending_confirmation`}
- [ ] **§2 范围与非范围声明**：明示**非** HARA / FSR / TSC / SwRS / HwRS 终稿；**非** ASPICE 评估通过；**非** ISO 26262 合规认证
- [ ] **§3 输入材料与 source 边界**：列出 source / template / checklist / reference / sample；With-Reference 须**显式声明参考 SyRS 仅作形状**
- [ ] **§4 SyRS 正文**：SEC-STAKE / SEC-FUNC / SEC-IF / SEC-PERF / SEC-ENV / SEC-DIAG / SEC-SAFE（若有）/ SEC-TRACE / SEC-VERIF / SEC-ASSUMP / SEC-DIFF（仅 With-Reference）
- [ ] **§5 追溯矩阵摘要**：上游↔SyRS 双向；下游预留列说明
- [ ] **§6 Open Items Registry**：所有 NEEDS_USER_CONFIRMATION 汇总
- [ ] **§7 审查/验证摘要**：Step 8 / Step 9 结论摘要；**非** sign-off
- [ ] **§8 状态声明与下游交接说明**

### delivery_summary.md Checklist

- [ ] 文档类型：`SystemRequirement`
- [ ] 状态：保守枚举
- [ ] 关键统计：SYS-F / SYS-IF / SEC-PERF / SEC-DIAG 条数；open 数；NEEDS_USER_CONFIRMATION 数；HITL decisions 数
- [ ] gap 按章节分类
- [ ] 下游接收方列表（IDD / HARA / FSR / SYS.3 架构 / SwRS / 测试）
- [ ] 已知风险：缺口、变型差异（With-Reference）

### Forbidden Claims（交付禁止）

- [ ] 不出现：`SyRS is approved` / **「SyRS 已批准」**
- [ ] 不出现：`requirements (are) complete and compliant`
- [ ] 不出现：`ASPICE SYS.2 satisfied` / `ASPICE Level X achieved`
- [ ] 不出现：`ISO 26262 compliant` / **「已满足功能安全合规」**
- [ ] 不出现：`ready for production release` / **「可量产」**
- [ ] 不出现：`risk is accepted` / `validated`

### 下游交接 Checklist

| 交接物 | 接收下游 | 通过条件 |
|---|---|---|
| SYS-F 表 + SYS-IF 表 | IDD（ISO 26262-3 §5） | F-xx / IF-xx 候选可直接派生 |
| SYS-F / SYS-IF / SEC-ENV / SEC-DIAG | 系统架构（ASPICE SYS.3） | 边界、接口、约束可分配到架构元素 |
| SEC-SAFE 引用 | FSR / HARA 链 | 与 fsr_source / SG 一致或 open |
| 追溯矩阵 | ASPICE SYS.2 BP5 审计 | 上游↔SyRS 闭合或显式 open |
| 验证方法候选 | 测试/V&V 团队 | 候选可作测试计划输入 |
| **open 项注记** | 全部下游 | 下游**不得**悄悄闭合 |
| SEC-DIFF（With-Reference） | 变型管理、客户接口 | 变型差异清单 |

### Open Items Registry 格式（强制段）

```
| OI-ID | 类别 | 相关 ID | 描述 | 等待什么 | 优先级 |
|---|---|---|---|---|---|
| OI-001 | 上游确认 | SYS-F-08 | 新增车速带需 OEM 最终标定 | OEM 提供标定 | P0 |
| OI-002 | 接口方向 | SYS-IF-12 | CAN 信号 X 方向待定 | 接口规范 v2.4 | P0 |
| OI-003 | SEC-SAFE | SYS-F-15 | 需链 FSR-03 | FSR 链上游 | P1 |
```

### ASPICE / ISO 维度 Checklist

- [ ] **ASPICE SYS.2 BP1**：交付包含 SEC-STAKE 干系人需求映射
- [ ] **ASPICE SYS.2 BP2**：交付包含结构化系统需求（SYS-F / IF / PERF / ENV / DIAG）
- [ ] **ASPICE SYS.2 BP3**：交付声明 SEC-VERIF 为候选，未越权断言充分
- [ ] **ASPICE SYS.2 BP4**：交付 OEM open 项已记录
- [ ] **ASPICE SYS.2 BP5**：交付追溯矩阵摘要双向或显式 open
- [ ] **ISO 26262-3 §5/§7**：交付明示**非** HARA/FSR 新结论，仅 SEC-SAFE 引用
- [ ] **ISO 26262-4 接口**：交付明示**非** TSC/系统设计 sign-off

### From-Scratch 专属 Checklist

- [ ] gap 按 SEC 分类统计写入 delivery_summary
- [ ] 大量 NEEDS_USER_CONFIRMATION 在 Open Items Registry 显式列出
- [ ] 状态最常为 `finalized_with_open_items` 或 `blocked_pending_confirmation`

### With-Reference 专属 Checklist

- [ ] §3 / delivery_summary **必含**：**参考边界声明**——「参考 SyRS（file_id）仅作形状参考，未支撑本项目任何 SYS-xx / 限值 / 接口事实」
- [ ] §8 下游交接明示：**下游不得用参考 SyRS 闭合 open** 或验证 SYS-xx
- [ ] SEC-DIFF 出现在正文且具体
- [ ] delivery_summary 包含 Δ 统计（Added / Removed / Modified / Renamed / Scope-changed 计数）

### 状态枚举 Checklist

| 状态 | 含义 |
|---|---|
| `ready_for_human_review` | 全文 review-ready，open 数较少，主要待 HITL 批准 |
| `finalized_with_open_items` | 全文已 review，仍有 open 项；交付不阻塞下游 |
| `blocked_pending_confirmation` | 含 P0 级 open（如无 SWRS、Direction 全空），下游应等待 |
| `failed`（仅 verify 用） | 验证不通过 |

**禁止**：`approved`、`validated`、`compliant`、`production_ready`。

### 常见 P0

| 错误 | 后果 |
|---|---|
| 越权批准措辞 | 交付边界错误 |
| Open Items Registry 不完整 | 下游误以为可关闭 open |
| With-Reference 交付未声明参考边界 | 下游误用参考 SyRS |
| 状态字段 `approved` / `compliant` | 越权结论 |
| 下游交接未列 SEC-DIFF（With-Reference） | 变型差异未交接 |

### 常见 P1

- delivery_summary 缺 HITL 决策计数
- 修订历史未列出关键变更
- 法规清单未明确适用范围

## A1 / A2 / B

**A1**：无 forbidden 措辞；Open Items Registry 完整；下游交接明示；状态保守。  
**A2**：补全 delivery 字段；With-Reference 补参考边界声明。  
**B**：final 不替代人工 SyRS 评审；不替代 ASPICE 评估或 ISO 26262 合规认证。
