# IDD 子 skill · Step 7 · 保守草稿

骨架：`skills/workflow-steps/step-conservative-draft/SKILL.md`。领域规则：`skills/document-types/ItemDefinitionDocument/SKILL.md`。

## 本步目的要点

- 按 `section_tasks.json` 逐 TASK 成稿，汇编 `draft/full_draft.md`。
- 只用 `allowed_evidence` 中 EVD；核对时 L1→L2→L3→原文。
- **IDD 正文内容**：F-xx 表、边界表、IF-xx 表（含方向）、环境约束、OS-xx/模式、假设、误用表、开放项。
- 缺证据保持 `NEEDS_USER_CONFIRMATION` / `[PENDING]`，不推断。
- **禁止**：hazard、HE、S/E/C、ASIL、SG、风险可接受等 HARA 措辞。

## IDD 方法论（本步定位）

本步对应 **阶段 5：撰写 Item Definition 正文**——按章节任务 **保守成稿**，只写有证据支撑的内容。

### 阶段 5 · 撰写正文（本步执行）

| 节 | 写法要点 |
|---|---|
| F-xx | 一条功能一行；描述**行为**，不写危害；缺描述标 pending |
| 边界 | 明确 In/Out；与架构图一致；**双向**说明 |
| IF-xx | 名称、类型、**方向**、对端、信号/机械说明 |
| 环境 | 参数 + 范围 + 单位 + 来源 |
| 工况 OS-xx | 描述场景事实（道路、速度、天气等），**不做 E 评级** |
| 误用 | 场景 + 相关功能 + 是否待确认；**单独成节** |
| 假设 | 显式列出，不隐含在正文里 |

### 重要边界（成稿时反复自检）

- Item Definition **不是** HARA：不写 hazard、S/E/C、ASIL、Safety Goal。
- Item Definition **不是** 合规批准书：不写「已满足 ISO 26262」「定义已最终批准」。
- **禁止**：在 IDD 里写 hazard、ASIL、Safety Goal、「风险可接受」等 HARA 语言。

### 成功标准（成稿视角）

- 功能、边界、接口、环境、工况、假设、误用均有来源或显式 open。
- 接口 **有方向**（输入/输出/双向）和对端。
- 边界 **In 与 Out 双向**说明。
- 误用 **单独可见**，不藏在假设里。
- 全文 **无危害分析结论**。

## 表格与字段要求（Clause 5 对齐）

| 节 | 建议列/内容 | Clause 5 |
|---|---|---|
| SEC-IDENT | Item 名称、版本、变型、适用产品 | §5.4.1 |
| SEC-FUNC | F-ID、名称、描述、来源、状态 | §5.4.2 |
| SEC-BOUNDARY | 子系统/功能、In/Out、说明 | §5.4.3 |
| SEC-IF | IF-ID、名称、类型、**方向**、对端、信号/机械说明 | §5.4.3 |
| SEC-ENV | 参数、范围、单位、来源 | §5.4.4 |
| SEC-OPS | OS-ID、描述、道路/速度/环境（事实性，**非 E 评级**） | HARA 输入 |
| SEC-ASSUMP | 假设 ID、描述、依赖对象、状态 | §5.4.4 |
| SEC-MISUSE | 场景 ID、误用描述、相关功能、状态 | §5.4.4 b |

## 本步 Review / Checklist 要点

本步产出 `draft/full_draft.md` 是 Step 8 内容审查与 Step 9 VC-3/VC-4 的直接对象。

### Clause 5 内容 Checklist（成稿自检）

| # | 检查项 | Clause | 通过条件 |
|---|---|---|---|
| 1 | Item 标识 | §5.4.1 | 名称、版本、变型、适用产品已写清，或有 open |
| 2 | 功能描述 F-xx | §5.4.2 | 每条有来源或 `NEEDS_USER_CONFIRMATION` |
| 3 | 系统边界 | §5.4.3 | In/Out 双向；与架构一致 |
| 4 | 外部接口 IF-xx | §5.4.3 | 含**方向**和对端 |
| 5 | 运行环境与约束 | §5.4.4 | 有来源或 open |
| 6 | 运行工况与模式 | HARA 输入 | 事实性描述；无 E 评级、无危害 |
| 7 | 假设与依赖 | §5.4.4 | 显式列出；不与误用混写 |
| 8 | 合理可预见误用 | §5.4.4 b | 单独成节或有 open |
| 9 | Item 间交互 | 系统上下文 | 有说明或 open |
| 10 | 文档治理 | — | 目的/范围、参考文件含版本号、术语、修订历史 |
| 11 | 开放问题 | — | 缺材料、待 HITL 项完整列出 |
| 12 | IDD 纯净性 | — | 无 hazard/HE/S/E/C/ASIL/SG/风险可接受 |

### 表格字段 Review 要点（成稿细查）

| 节 | 建议必查列 |
|---|---|
| SEC-FUNC | F-ID、名称、描述、来源、状态 |
| SEC-BOUNDARY | 子系统/功能、In/Out、说明 |
| SEC-IF | IF-ID、名称、类型、**方向**、对端、信号/机械说明 |
| SEC-ENV | 参数、范围、单位、来源 |
| SEC-OPS | OS-ID、描述、道路/速度/环境（**非 E 评级**） |
| SEC-MISUSE | 场景 ID、误用描述、相关功能、状态 |
| SEC-ASSUMP | 假设 ID、描述、依赖对象、状态 |

### 本步 Review 要点

| 维度 | 检查项 | 级别 |
|---|---|---|
| 证据匹配 | 正文不超出 `allowed_evidence` | P0 |
| 缺口诚实性 | 缺证据保留 `NEEDS_USER_CONFIRMATION` | P0 |
| Forbidden Claims | 无「已批准」「已合规」措辞 | P0 |
| IDD 纯净性 | 无 HARA 语言 | P0 |

## 常见错误（本步重点防）

| 错误 | 后果 | 级别 |
|---|---|---|
| IDD 里写 hazard / ASIL | 文档类型混淆，审查不通过 | P0 |
| 接口无方向 | 后续接口危害、故障传播分析困难 | P0 |
| 边界只有 In 没有 Out | 范围膨胀，HARA 范围失控 | P1 |
| 误用缺失或藏在假设里 | 不符合 §5.4.4 b | P0 |
| 缺材料时静默填默认值 | 不可追溯、HITL 失效 | P0 |
| 写「定义已批准」「已合规」 | 越权结论 | P0 |

## A1 / A2 / B

**A1**：无超出证据表述；无 HARA 泄漏；接口有方向列；边界 In/Out 双向。  
**A2**：按 TASK 重跑缺证据节。  
**B**：critical 段标 HITL；无 forbidden final claims。
