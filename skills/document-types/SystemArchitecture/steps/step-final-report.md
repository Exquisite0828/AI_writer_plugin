# System Architecture 子 skill · Step 13 · 最终报告

骨架：`skills/workflow-steps/step-final-report/SKILL.md`。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点

- 打包 `final/final_report.md`、`final/delivery_summary.md`（review-ready，**非批准**）。
- conservative status：`ready_for_human_review` / `finalized_with_open_items` / `blocked_pending_confirmation`。

## System Architecture 方法论（本步定位）

本步对应 **阶段 7 交付** 与 **阶段 8 下游交接**。

### 阶段 8 · 下游交接

| 交接物 | 说明 | 下游 |
|---|---|---|
| 架构元素清单 | 模块/职责/边界基线 | 系统设计、SwRS/HwRS |
| 接口架构表 | 方向、对端、协议、边界 | 接口设计、集成 |
| 分配矩阵 | requirement → element | 系统设计、软件/硬件需求分解 |
| 诊断/降级架构 | 系统级故障处理路径 | 详细设计、V&V |
| 资源与平台约束 | CPU/内存/总线/时序约束 | 软件/硬件设计 |
| **open 项** | 下游**不得**悄悄闭合 | 全部下游 |

## 本步 Review / Checklist 要点

### 交付包结构 Checklist

- [ ] 文档元信息与范围（非 HARA/TSC/SwRS/HwRS、非批准）
- [ ] 架构正文（SEC-REQTRACE … SEC-LARCH … SEC-IF … SEC-ALLOC …）
- [ ] 追溯矩阵摘要
- [ ] Open Items Registry
- [ ] 审查/验证摘要（**非 sign-off**）
- [ ] 状态声明与下游说明

### delivery_summary.md Checklist

- [ ] `document_type: SystemArchitecture`
- [ ] 状态为保守枚举
- [ ] 关键统计：元素数、接口数、分配矩阵行数、open 数、HITL 数
- [ ] gap 按章节分类
- [ ] 下游接收方列表（系统设计 / SwRS / HwRS / V&V）

### From-Scratch 专属 Checklist

- [ ] gap 按 SEC 分类统计写入 delivery_summary
- [ ] 大量 NEEDS_USER_CONFIRMATION 在 Open Items Registry 显式列出

### With-Reference 专属 Checklist

- [ ] **参考边界声明**：参考架构文档仅作形状参考，未支撑本项目任何元素/接口/分配事实
- [ ] 下游说明：**不得用参考架构闭合 open**
- [ ] SEC-DIFF 出现在正文且具体

### 常见 P0

| 错误 | 后果 |
|---|---|
| 越权批准措辞 | 交付边界错误 |
| Open Items Registry 不完整 | 下游误以为可关闭 open |
| With-Reference 未声明参考边界 | 下游误用参考架构 |

## A1 / A2 / B

**A1**：无 forbidden 措辞；Open Items Registry 完整；下游交接明示；状态保守。  
**A2**：补全 delivery 字段；With-Reference 补参考边界声明。  
**B**：final 不替代人工架构评审；不替代 ASPICE 评估或 ISO 26262 合规认证。
