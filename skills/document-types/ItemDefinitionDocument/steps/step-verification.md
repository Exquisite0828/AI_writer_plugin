# IDD 子 skill · Step 9 · 验证

骨架：`skills/workflow-steps/step-verification/SKILL.md`。领域规则：`skills/document-types/ItemDefinitionDocument/SKILL.md`。

## 本步目的要点

- 确定性检查：artifact 齐全、citation integrity、tier 合规、sample 非事实。
- **IDD REQUIRED_CHECKS 要点**：
  - VC-1：manifest、source_index、template_structure、section_writing_plans、evidence_map、claim_support_matrix、draft、review、unresolved 存在
  - VC-2：critical claim 无 T4/T5；F/IF/边界 EVD 含 L1/L2/L3 provenance
  - VC-3：无「定义已批准」「边界已最终确认」「ISO 26262 compliant」等 forbidden 措辞
  - VC-4：**草稿中无 hazard/ASIL/SG 表或章节**（IDD 纯净性）
  - VC-5：`NEEDS_USER_CONFIRMATION` 保留；candidate inactive
- 失败写入 `verify/failures.md`。

## IDD 方法论（本步定位）

本步对应 **阶段 6：审查与验证** 中的 **形式/合规审查** 环节（安全工程师/机器检查视角）。

### 阶段 6 · 形式/合规验证（本步执行）

1. **样例是否被误当事实**（T4 不得支撑 critical claim）。
2. **是否有「已批准」「已合规」等过度结论**。
3. **开放项是否完整**（`NEEDS_USER_CONFIRMATION` 未静默消除）。
4. **artifact 链是否完整**（manifest → index → plans → EVD → matrix → draft → review）。
5. **IDD 纯净性**：无 HARA 危害/评级内容渗入。

### 成功标准（验证视角）

- 功能、边界、接口、环境、工况、假设、误用 **均有来源或显式 open**。
- 接口 **有方向**和对端。
- 边界 **In 与 Out 双向**说明。
- 误用 **单独可见**。
- 全文 **无危害分析结论**。
- 状态保守：`passed_with_open_items` / `failed`，**无** `validated` 或 `approved`。

## 本步 Review / Checklist 要点

本步是 IDD **形式/合规验证主 skill**（安全工程师/机器检查视角）。内容审查见 Step 8。

### 形式/合规验证要点（VC-1～VC-5）

| 检查编号 | 验证要点 |
|---|---|
| VC-1 | artifact 链完整：manifest → source_index → template_structure → section_writing_plans → evidence_map → claim_support_matrix → draft → review → unresolved |
| VC-2 | critical claim 不得用 T4（sample）/ T5（推断）支撑；F/IF/边界 EVD 须含 L1/L2/L3 provenance |
| VC-3 | 无 forbidden 措辞（见下文） |
| VC-4 | 草稿中无 hazard/ASIL/SG 表或章节（IDD 纯净性） |
| VC-5 | `NEEDS_USER_CONFIRMATION` 未被静默消除；candidate profile 保持 inactive |

### Forbidden Claims（验证必查 · P0）

无充分 T0/T1 与 HITL 时，报告中**禁止出现**：

- item definition is approved / **定义已批准**
- boundaries are final / **边界已最终确认**
- all interfaces are complete and verified
- ISO 26262 compliant / **已满足 Clause 5 合规**
- ready for production / **可量产**
- 将 sample IDD 中的功能/边界/接口照搬为本项目事实

### P0 失效项（验证必查）

| 失效 | 级别 | 后果 |
|---|---|---|
| sample 支撑 F-xx/边界 | P0 | HARA 基线错误 |
| 草稿含 HARA 危害表 | P0 | 文档类型混淆 |
| 接口无方向且标为已确认 | P0 | 后续分析困难 |
| 误用节缺失且无 open | P0 | 不符合 §5.4.4 b |
| 含 forbidden final claims | P0 | 越权结论 |
| 缺材料静默填值（无 EVD 无 open） | P0 | 不可追溯 |
| Item 边界材料缺失且无 gap 登记 | P0 | 输入链断裂 |
| sample 被标为 source | P0 | 事实来源违规 |

### P1 失效项

- 边界只有 In 没有 Out
- 假设隐式而非显式
- 引用文档无版本号
- 接口方向材料缺失但未登记 gap

### 审查结论的边界声明

验证通过后状态只能是保守表述：

- `passed_with_open_items`
- `failed`

**不能**使用 `validated`、`approved`、`ISO 26262 compliant`。不等于 formal sign-off，也不等于可自动进入 HARA。

## 典型 P0

| 失效 | 级别 | 对应常见错误 |
|---|---|---|
| sample 支撑 F-xx/边界 | P0 | 样例当事实 |
| 草稿含 HARA 危害表 | P0 | IDD 里写 hazard/ASIL |
| 接口无方向且标为已确认 | P0 | 接口无方向 |
| 误用节缺失且无 open | P0 | 误用缺失或藏在假设里 |
| 含 forbidden final claims | P0 | 写「已合规」「已批准」 |
| 缺材料静默填值（无 EVD 无 open） | P0 | 不可追溯 |

## Forbidden Final Claims（验证必查）

无充分 T0/T1 与 HITL 时禁止出现：

- item definition is approved / 定义已批准
- boundaries are final / 边界已最终确认
- all interfaces are complete and verified
- ISO 26262 compliant / 已满足 Clause 5 合规
- ready for production / 可量产

## A1 / A2 / B

**A1**：每项 CHECK 有 pass/fail；P0 无遗漏。  
**A2**：修复 blocker 后重验。  
**B**：status 保守（`passed_with_open_items` / `failed`），无 `validated` / `approved`。
