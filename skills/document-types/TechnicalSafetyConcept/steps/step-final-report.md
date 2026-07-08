# TSC 子 skill · Step 13 · 最终报告

骨架：`skills/workflow-steps/step-final-report/SKILL.md`。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点

- 打包 `final/final_report.md`、`final/delivery_summary.md`（review-ready，**非批准**）。
- conservative status：`ready_for_human_review` / `finalized_with_open_items` / `blocked_pending_confirmation`。

## TSC 方法论（本步定位）

本步对应 **阶段 8：定稿与下游交接**。

### 阶段 8 · 定稿与下游交接（本步执行）

1. 输出 **review-ready TSC 包**（**非**正式 sign-off）。
2. 明确交接给：**系统设计**、**HW 安全概念**、**SW 安全概念**、**安全验证计划**。
3. 记录版本、变更、未决项，供下游引用；下游 **不得**悄悄闭合 open。

### 与相邻文档的交接关系

| 下游文档 | 从 TSC 接收 | TSC 不做 |
|---|---|---|
| 系统设计 | TSR、机制概念、架构分配 | 详细设计决策 sign-off |
| HSC | 机制、HW 接口约束 | HSC 终稿 |
| SSC | 机制、SW 接口约束 | SSC 终稿 |
| 安全验证报告 | TSR、验证方法候选、追溯矩阵 | 「已充分验证」结论 |

### 阶段 7 · 交付（本步 artifact）

1. 正文 + 追溯矩阵摘要 + open 清单 + 审查/验证摘要（**非 sign-off**）
2. 声明：**非 HSC/SSC**、**非 TSC 批准**、**非合规认证**

### 阶段 8 · 下游交接（HSC/SSC deferred）

| 交接物 | 说明 |
|---|---|
| TSR-xx 需求表 | 系统设计、HW/SW 安全需求分解输入 |
| 安全机制概念 | HSC/SSC 机制细化输入 |
| 故障处理与安全状态策略 | 详细设计与 V&V 输入 |
| SG/FSR/TSR 追溯矩阵 | 验证与确认基线 |
| ASIL 继承/分解说明 | 分配约束 |
| 验证方法候选 | V&V 规划输入 |
| **open 项** | 下游（含未来 HSC/SSC）**不得**悄悄闭合 |

```
TSC 报告（Clause 8）
    ↓（交接）
系统设计 / HSC / SSC / 集成验证 …  ← 本仓库 HSC/SSC deferred
```

### 交付包结构

1. 文档元信息与范围（非 HSC/SSC、非批准）
2. TSC 正文（SEC-ARCH … SEC-TSR … SEC-MECH …）
3. 证据与追溯矩阵摘要
4. open / NEEDS_USER_CONFIRMATION 清单
5. 审查/验证结论摘要
6. 状态声明与下游说明

### 一句话总结

在已确认 FSR/SG 与架构上下文之下，用 **有来源、可追溯 FSR/SG、架构可分配、机制可解释、FTTI 显式、验证方法显式、有 open 项** 的方式整理 TSC 候选包；**只组织技术层需求、机制与故障处理概念，不做 HSC/SSC，不做 TSC 批准或合规认证**。

### 触发方式（本仓库）

运行期只使用用户明确选择的 task file；本子 skill 不列出 demo task 路径。

`task_type: TechnicalSafetyConcept` 加载本目录子 skill。

## 本步 Review / Checklist 要点

### 交付 Checklist

- [ ] 无 approved/compliant/量产/forbidden 措辞
- [ ] open 清单完整
- [ ] 声明 **HSC/SSC deferred**
- [ ] 下游交接：TSR-xx、机制概念、追溯矩阵、ASIL、验证候选、open 项
- [ ] 状态：`ready_for_human_review` / `finalized_with_open_items`（**非** approved）

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| delivery | gap 统计按 SEC 分类 | 含**参考边界声明**（参考 TSC 未作事实） |
| 交接 | 明示 open 清单 | 明示：下游**不得**用参考 TSC 闭合 open |

### Forbidden Claims（交付禁止）

- TSC is approved
- requirements complete and compliant
- ready for production release

### 常见 P0

| 错误 | 后果 |
|---|---|
| 越权批准措辞 | 交付边界错误 |
| 交付未声明参考边界（With-Reference） | 下游误用参考 TSC |

## A1 / A2 / B

**A1**：无 forbidden 措辞；open 完整；交接明示。  
**A2**：补全 delivery 字段。  
**B**：final 不替代人工 TSC 评审。
