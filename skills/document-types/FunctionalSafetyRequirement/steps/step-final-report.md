# FSR 子 skill · Step 13 · 最终报告

骨架：`skills/workflow-steps/step-final-report/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点

- 打包 `final/final_report.md`、`final/delivery_summary.md`（review-ready，**非批准**）。
- conservative status：`ready_for_human_review` / `finalized_with_open_items` / `blocked_pending_confirmation`。

## FSR 方法论（本步定位）

本步对应 **阶段 7 交付** 与 **阶段 8 下游交接（概念）**。

### 阶段 7 · 交付

1. 正文 + SG 追溯矩阵摘要 + open 清单 + 审查/验证摘要（**非 sign-off**）
2. 声明：**非 TSC**、**非 FSR 批准**、**非合规认证**

### 阶段 8 · 下游交接（TSC 为独立下游文档类型）

| 交接物 | 说明 |
|---|---|
| FSR-xx 需求表 | 系统设计/需求分解输入 |
| SG 追溯矩阵 | 验证与确认基线 |
| ASIL 继承说明 | 分配约束 |
| 验证方法候选 | V&V 规划输入 |
| **open 项** | 下游（含 TSC）**不得**悄悄闭合 |

```
FSR 报告（Clause 7）
    ↓（交接）
TSC / 系统设计 / 需求分解 …  ← TSC 为独立下游文档类型
```

### 交付包结构

1. 文档元信息与范围（非 TSC、非批准）
2. FSR 正文（SEC-SG … SEC-FSR …）
3. 证据与 SG 追溯矩阵摘要
4. open / NEEDS_USER_CONFIRMATION 清单
5. 审查/验证结论摘要
6. 状态声明与下游说明

### 一句话总结

在已确认 SG 之下，用 **有来源、可追溯 SG、ASIL 可解释、验证方法显式、有 open 项** 的方式整理 FSR 候选包；**只组织功能层需求与追溯，不做 TSC，不做需求批准或合规认证**。

### 触发方式（本仓库）

```text
/ai-writing-plugin:write "Run the writing workflow with examples/functional_safety_requirement_demo_fixture/task.yaml"
```

`task_type: FunctionalSafetyRequirement`（或 `fsr`）加载本目录子 skill。

## 本步 Review / Checklist 要点

### 交付 Checklist

- [ ] 无 approved/compliant/量产/forbidden 措辞
- [ ] open 清单完整
- [ ] 声明 **TSC deferred**
- [ ] 下游交接：FSR-xx、SG 矩阵、ASIL、验证候选、open 项
- [ ] 状态：`ready_for_human_review` / `finalized_with_open_items`（**非** approved）

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| delivery | gap 统计按 SEC 分类 | 含**参考边界声明**（参考 FSR 未作事实） |
| 交接 | 明示 open 清单 | 明示：下游**不得**用参考 FSR 闭合 open |

### Forbidden Claims（交付禁止）

- FSR set is approved
- requirements complete and compliant
- ready for production release

### 常见 P0

| 错误 | 后果 |
|---|---|
| 越权批准措辞 | 交付边界错误 |
| 交付未声明参考边界（With-Reference） | 下游误用参考 FSR |

## A1 / A2 / B

**A1**：无 forbidden 措辞；open 完整；交接明示。  
**A2**：补全 delivery 字段。  
**B**：final 不替代人工 FSR 评审。
