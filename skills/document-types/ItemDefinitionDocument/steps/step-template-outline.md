# IDD 子 skill · Step 4 · 模板大纲

骨架：`skills/workflow-steps/step-template-outline/SKILL.md`。领域规则：`skills/document-types/ItemDefinitionDocument/SKILL.md`。

## 本步目的要点

### 阶段 A · L1

- 读 `task_brief`、IDD template（L1→L2→L3）、sample IDD（T4，仅形状）。
- 合并默认 L1（SEC-DOC … SEC-REVIEW，见根 SKILL），产出 `outline_l1.md` + `template_structure.json` L1 节点。
- **不写**功能/边界正文；**不含** SEC-HAZ/HE/SEC/SG 等 HARA 章。

### 阶段 B · L2

- 逐 L1 定 L2；例：
  - SEC-FUNC：功能总述；F-xx 功能表
  - SEC-BOUNDARY：In scope；Out of scope
  - SEC-IF：IF-xx 接口表（含方向列）
  - SEC-ENV：环境与物理约束
  - SEC-OPS：工况表 OS-xx；模式说明
  - SEC-MISUSE：误用场景表
- 缺口 L2 标 `evidence: pending` → `outline_l2.md` + level=2 节点。

## IDD 方法论（本步定位）

本步对应 **阶段 2：定大纲（先 L1，后 L2）**——确定报告结构与每章小节，**不写正文**。

### 阶段 2 · 定大纲

1. **L1**：确定报告有哪些章（与 ISO 26262-3 Clause 5 及 OEM/Tier1 实践对齐）。
2. **L2**：每章拆小节，例如：
   - 功能章：功能总述 + F-xx 表
   - 边界章：In scope 表 + Out of scope 表
   - 接口章：IF-xx 表（**强制含「方向」列**）
   - 工况章：OS-xx 表 + 模式说明
   - 误用章：误用场景表
3. 对尚无材料的 L2 标 **pending**，不强行写满。

### 报告建议结构（L1 与 Clause 5 关联）

| section_id | 章节 | 内容要点 | Clause 5 关联 | 强制 |
|---|---|---|---|:---:|
| SEC-DOC | 文档信息与修订历史 | 版本、作者、状态 | 文档治理 | |
| SEC-SCOPE | 目的、范围与读者 | 本文档用途、适用 Item、读者 | 分析范围 | ★ |
| SEC-REF | 参考文件 | SyRS、架构、标准（含版本号） | 可追溯 | |
| SEC-TERMS | 术语与缩略语 | Item、ODD、接口等 | 一致性 | |
| SEC-IDENT | Item 标识 | 名称、版本、变型、适用产品 | §5.4.1 | ★ |
| SEC-FUNC | 功能描述 F-xx | 每条功能的名称与行为描述 | §5.4.2 | ★ |
| SEC-BOUNDARY | 系统边界 | In scope / Out of scope | §5.4.3 | ★ |
| SEC-IF | 外部接口 IF-xx | 传感器/执行器/总线/机械/人机，**含方向** | §5.4.3 | ★ |
| SEC-ENV | 运行环境与约束 | 温度、电压、速度范围等 | §5.4.4 | ★ |
| SEC-OPS | 运行工况与模式 | OS-xx、操作模式（供 HARA 用，**不写危害**） | HARA 输入 | ★ |
| SEC-ASSUMP | 假设与依赖 | 对其它系统/驾驶员/环境的假设 | §5.4.4 | ★ |
| SEC-MISUSE | 合理可预见误用 | 误用场景与相关功能 | §5.4.4 b | ★ |
| SEC-DEP | Item 间交互与依赖 | 与其它 Item/ECU 的耦合 | 系统上下文 | |
| SEC-OPEN | 开放问题 | 缺材料、待 HITL 项 | 诚实缺口 | |
| SEC-REVIEW | 审查总结 | 覆盖度、open 项、状态声明（**非批准结论**） | 审查 | ★ |

**禁止**：在大纲中加入 HARA 危害章（hazard、HE、S/E/C、ASIL、Safety Goal）。

## 本步 Review / Checklist 要点

本步产出将在 Step 8 审查「强制 L1 覆盖」与「无 HARA 章渗入」时被对照。

### 强制章节结构 Checklist（L1）

| section_id | 章节 | 强制 |
|---|---|:---:|
| SEC-SCOPE | 目的、范围与读者 | ★ |
| SEC-IDENT | Item 标识 | ★ |
| SEC-FUNC | 功能与 F-xx | ★ |
| SEC-BOUNDARY | 系统边界 | ★ |
| SEC-IF | 外部接口 | ★ |
| SEC-ENV | 运行环境与约束 | ★ |
| SEC-OPS | 工况与模式 | ★ |
| SEC-ASSUMP | 假设与依赖 | ★ |
| SEC-MISUSE | 合理可预见误用 | ★ |
| SEC-REVIEW | 审查总结 | ★ |

审查时还应确认：**不含** HARA 危害章（SEC-HAZ/HE/SEC/SG 等）。

### 与本步相关的 L2 结构检查

- [ ] SEC-BOUNDARY 拆分为 In scope + Out of scope 两个 L2
- [ ] SEC-IF 的 IF-xx 表 L2 **含方向列**定义
- [ ] SEC-MISUSE 独立 L2，未合并进 SEC-ASSUMP
- [ ] 无材料 L2 标 `evidence: pending`，未标 complete
- [ ] 大纲正文无 F-xx/边界具体值（sample 未升格事实）

### 本步 Review 要点

| 维度 | 检查项 | 级别 |
|---|---|---|
| L1 完备性 | 强制 ★ 章全覆盖 | P0 |
| IDD 纯净性 | 无 HARA 危害章 | P0 |
| 边界双向性 | In + Out 双 L2 | P1 |
| 接口方向列 | IF 表 L2 含方向列 | P0 |
| 误用独立性 | MISUSE 独立 L2 | P0 |
| 缺口显式 | pending L2 已标注 | P1 |

## 常见错误（本步重点防）

| 错误 | 后果 | 级别 |
|---|---|---|
| 大纲含 HARA 危害章 | 文档类型混淆 | P0 |
| 边界 L2 只有 In 没有 Out | 范围膨胀，HARA 范围失控 | P1 |
| IF-xx 表 L2 无方向列定义 | Clause 5 / 审查 P0 | P0 |
| 无材料 L2 强行标 complete | 后续静默填值 | P0 |
| 从 sample 复制 F-xx/边界进大纲正文 | 事实来源违规 | P0 |

## A1 / A2 / B

**A1**：L1 覆盖 Clause 5 相关章；无 HARA 危害章；L2 与 template/sample 形状一致；缺口 L2 标 pending。  
**A2**：补 L2、对齐 JSON/outline。  
**B**：三 artifact 一致；sample 未升格事实；IF 表含方向列定义。
