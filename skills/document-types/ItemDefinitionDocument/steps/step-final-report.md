# IDD 子 skill · Step 13 · 最终报告

骨架：`skills/workflow-steps/step-final-report/SKILL.md`。领域规则：`skills/document-types/ItemDefinitionDocument/SKILL.md`。

## 本步目的要点

- 打包 `final/final_report.md`、`final/delivery_summary.md`（review-ready，**非批准**）。
- 汇总：IDD 版本、输入材料、F-xx/IF-xx/边界覆盖统计、open 项数量、HITL 待确认列表。
- 声明：本文档为 Item 定义候选包，供 HARA/安全概念输入；**不等于** ISO 26262 合规认证。
- conservative status：`ready_for_human_review` / `finalized_with_open_items` / `blocked_pending_confirmation`。

## IDD 方法论（本步定位）

本步对应 **阶段 7：修订与交付** 的 **交付** 环节，以及 **阶段 8：进入 HARA 的交接**。

### 阶段 7 · 交付（本步执行）

1. **打包 review-ready 交付物**：
   - 正文（revised draft 或汇编）
   - 证据与引用矩阵摘要
   - 开放问题与 `NEEDS_USER_CONFIRMATION` 清单
   - 审查/验证结论摘要（机器检查，**非专业 sign-off**）
2. **声明状态**：`ready_for_human_review` / `finalized_with_open_items`，**不等于**正式 sign-off。
3. **保留变更记录**引用。

### 阶段 8 · 进入 HARA 的交接（本步须明示）

IDD 定稿（或带 open 项评审通过）后，向 HARA 传递：

| 交接物 | 说明 |
|---|---|
| F-xx 功能清单 | HARA 分析对象的功能基线 |
| 系统边界 | In/Out scope |
| IF-xx 接口 | 含方向的接口定义 |
| OS-xx 工况与模式 | HARA 场景输入 |
| 假设清单 | 分析前提 |
| 误用清单 | §5.4.4 b 输入 |
| **明确的 open 项** | HARA **不得**悄悄填掉 |

```
Item Definition 报告
    ↓（交接）
危害分析与风险评估（HARA，ISO 26262-3 第 6 章）
    ↓
功能安全概念（FSC，第 7 章）…
```

### 一句话总结（交付边界）

**Item Definition 报告的本质**：在 HARA 之前，用 **有来源、有边界、有接口方向、有误用、有 open 项** 的方式，把 Item「是什么」写清楚；**只描述事实与范围，不做危害判断，不做合规批准**。

## 交付包建议结构

1. 文档元信息与范围（SEC-DOC、SEC-SCOPE）
2. Item 定义正文（SEC-IDENT … SEC-MISUSE，或引用 revised draft）
3. 证据与引用矩阵摘要（F/IF/边界 coverage）
4. 开放问题与 `NEEDS_USER_CONFIRMATION` 清单
5. 审查/验证结论摘要（机器检查，非专业 sign-off）
6. 状态声明与后续建议（如：进入 HARA 前须关闭的 open 项）

## 本步 Review / Checklist 要点

本步打包最终交付物；须体现 Step 10/11 审查结论，并遵守审查边界声明。

### 交付前 Checklist

- [ ] `final_report.md` 无 forbidden claims（已批准/已合规/可量产）
- [ ] open 项与 `NEEDS_USER_CONFIRMATION` 清单完整列出
- [ ] 审查/验证结论摘要已纳入（机器检查，非 sign-off）
- [ ] F-xx/IF-xx/边界覆盖统计与 evidence matrix 摘要一致
- [ ] HARA 交接清单明示（含 open 项不得被 HARA 悄悄填掉）
- [ ] 状态为保守表述（见下文）

### 审查结论的边界声明

IDD 交付状态**只能**是：

- `ready_for_human_review`
- `finalized_with_open_items`
- `blocked_pending_confirmation`

**不能**使用 `validated`、`approved`、`ISO 26262 compliant`。

`final_report.md` 是 **review-ready 包**，不等于 formal sign-off，也不等于可自动进入 HARA。

### 本步 Review 要点

| 维度 | 检查项 | 级别 |
|---|---|---|
| 措辞边界 | 无 approved/compliant/production-ready | P0 |
| 缺口完整 | open 项全部列出 | P0 |
| HARA 交接 | 七类交接物 + open 项明示 | P1 |
| 证据摘要 | matrix 摘要与正文一致 | P1 |
| 审查追溯 | 含 Step 10/11 结论摘要 | P1 |

### 一句话归纳

**Checklist 核心**：Clause 5 七类内容齐全或有 open；接口有方向；边界 In/Out 双向；误用独立成节；全文无 HARA 内容。  
**交付核心**：review-ready，不做危害判断，不做合规批准。

### Forbidden Final Claims（交付包禁止出现）

- item definition is approved / 定义已批准
- boundaries are final / 边界已最终确认
- ISO 26262 compliant / 已满足合规
- ready for production / 可量产

## A1 / A2 / B

**A1**：无 approved/compliant 措辞；open 项完整列出；HARA 交接清单明示。  
**A2**：补全 delivery 字段、交接说明。  
**B**：final 不替代人工 Item 定义评审；不等于 HARA 输入自动合格。
