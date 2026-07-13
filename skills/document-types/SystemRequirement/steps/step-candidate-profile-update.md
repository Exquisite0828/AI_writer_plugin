# SyRS 子 skill · Step 13 · 候选 profile 更新

骨架：`skills/workflow-steps/step-candidate-profile-update/SKILL.md`。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点

- 产出 `candidate_profile_update.yaml`、`candidate_skill_patch.md`、`promotion_report.md`。
- 状态 **`proposed` / `inactive`**。
- **不得**把本次 run 的 SYS-xx/接口/限值写入通用 profile。

## SyRS 方法论（本步定位）

从本次 run 提炼 **可复用流程/checklist 信号**，不固化项目事实。

### 可提炼信号（ASPICE SYS.2 → checklist）

| 信号 | 可提案 | 规则 |
|---|---|---|
| 上游链接列强制 | SYS-F 表 Linked upstream ID 列 | SYS.2 BP5 追溯 |
| 接口方向列强制 | SYS-IF 表 Direction 列 | 集成/架构输入 |
| 对端列强制 | SYS-IF Counterpart 列 | 接口完整性 |
| HARA 防泄漏 | 草稿扫描项 | SyRS 不写 HARA |
| TSR/TSC 防泄漏 | 草稿扫描项 | SyRS 不写 TSC |
| 验证方法「候选」默认 | writing_mode 提醒 | SYS.2 BP3 |
| sample 勿升格 | tier 提醒 | 事实来源 |
| SEC-STAKE 强制 | 干系人需求摘要章 | SYS.2 BP1 |

### SyRS 写作核心原则（patch 可引用）

1. **SyRS ≠ HARA/FSR**
2. **SyRS ≠ TSC/SwRS**
3. **sample 不作 fact source**
4. **每条 SYS-xx 链上游**
5. **接口须有方向与对端**
6. **review-ready ≠ sign-off**

### 与 IDD 关系（流程说明可含）

- SyRS 为 IDD 上游；候选 patch **不得**混入 IDD 的 F-xx/边界事实。
- SyRS 下游为 SYS.3/IDD；patch **不得**预写架构分配终稿。

## 本步 Review / Checklist 要点

### candidate_profile_update.yaml 强制字段 Checklist

- [ ] `status: proposed`
- [ ] `active: false`
- [ ] `applies_to: SystemRequirement`
- [ ] `signals[]`：每条含 `id`、`name`、`evidence_from_run`（**仅** run-level 流程统计，**非** SYS-xx 事实）、`proposed_change_type`（checklist_item / outline_constraint / writing_mode_default / forbidden_term）、`scope`（哪一 step）
- [ ] `requires_human_review: true`
- [ ] `attribution`：本次 run_id，但**不**含客户/项目敏感信息

### 可提案 / 禁止内容矩阵

| 可提案信号 | 写入位置示例 | 禁止内容 |
|---|---|---|
| 上游 ID 链接列强制（SYS.2 BP5） | Step 4 outline 必含 Linked upstream ID | 具体 SWRS-xxx 与 SYS-F-xxx 映射数据 |
| SYS-IF Direction 列强制 | Step 4 / 9 checklist 加 Direction 机器规则 | 具体本项目 CAN/LIN 信号 |
| SYS-IF Counterpart + Failure behavior 列 | Step 4 outline + Step 7 draft checklist | 本项目对端 ECU 名 |
| Forbidden 措辞扫描规则增强 | Step 9 VC-3 词表 | 本项目客户措辞 |
| 性能/限值单位检查 | Step 9 机器规则 | 本项目限值数字 |
| HARA / ASIL / SG / TSR 防泄漏扫描 | Step 9 VC-4 词表 | hazard 模板内容 |
| sample 升格防护（role / is_fact_source） | Step 1 / 9 检查 | 参考 SyRS 内容 |
| ASPICE SYS.2 BP1–BP5 对照表 | Step 4 / 8 模板 | 客户/OEM 项目 |
| With-Reference：SEC-DIFF 强制 | Step 4 / 7 模板 | 本次 Δ 具体内容 |
| With-Reference：Δ-Analysis 方法学（差异类型枚举、列定义） | reusable patterns | 本次差异条目 |
| With-Reference：参考边界声明模板 | Step 11 交付包模板 | 客户名、参考项目名 |
| shall 句式 / 单条单义机器规则 | Step 9 机器规则 | 本次具体语句 |
| writing_mode_hint 默认值 | Step 5 计划默认 | — |

### SyRS 写作核心原则（candidate_skill_patch.md 可引用）

1. **SyRS ≠ HARA/FSR**：草稿/正文/字段中无 hazard / ASIL / SG / TSR
2. **SyRS ≠ TSC/SwRS**：无技术安全机制 / SwRS 表
3. **sample 不作 fact source**：role / is_fact_source 须正确
4. **每条 SYS-xx 链上游**：Linked upstream ID 强制
5. **接口须有方向与对端**：Direction 列强制
6. **review-ready ≠ sign-off**：状态枚举保守
7. **With-Reference**：SEC-DIFF 必存且具体

### Forbidden 写入 Checklist（候选 profile **禁止**包含）

- [ ] 任何本项目 SYS-F-xx / SYS-IF-xx ID 与表述
- [ ] 任何客户/OEM 项目名、ECU 名、Part No
- [ ] 任何本项目限值数字（性能/电压/温度/时序）
- [ ] 本项目 SWRS-xxx 与 SyRS 映射
- [ ] 任何 hazard / ASIL / SG / TSR 模板
- [ ] 任何「approved / compliant / 量产」措辞模板
- [ ] 参考 SyRS 的需求/接口/限值
- [ ] 本次 Δ-Analysis 具体差异条目

### promotion_report.md Checklist

- [ ] 明示候选 status `proposed`，须**人工审查**才启用
- [ ] 列出每条 signal 的 risk / benefit / 与现有 skill 冲突
- [ ] 升级路径建议：哪个 stable skill 文件接收、是否需要新增 checklist 项
- [ ] **不**自动覆盖 stable skill 文件
- [ ] **不**从 `runs/<run_id>/learning/` 路径自动应用

### ASPICE / ISO 维度 Checklist

- [ ] 候选信号区分通用 vs SystemRequirement-only；通用部分（如 shall 检查）可建议提升到 writing-core 候选层
- [ ] ASPICE SYS.2 BP1–BP5 对照表如有增补，标注作为 `outline_constraint` 候选
- [ ] ISO 26262-3 §5/§7 接口约束如有增补，标注 `forbidden_term` 类候选
- [ ] **禁止**：把本次 run 的「合规建议」写入 candidate

### From-Scratch 专属 Checklist

- [ ] 信号偏向「输入完备性」「shall 句式」「HARA 泄漏防护」「SYS-IF Direction」
- [ ] 不要把本 run 「大量 NEEDS_USER_CONFIRMATION 是正常」当作可提案规则——它已是 writing-core 通则

### With-Reference 专属 Checklist

- [ ] 可提案：SEC-DIFF 列定义、差异类型枚举、Δ-Analysis 方法学
- [ ] **禁止**：本次具体差异条目、客户「沿用 / 取消」判断
- [ ] 可提案：参考边界声明模板（Step 11）、参考 SyRS 升格 source 防护（Step 1 / 9）
- [ ] 可提案：matrix `source_file_id ≠ ref_file_id` 机器规则

### 双情景 Review 对比

| 维度 | From-Scratch 信号 | With-Reference 额外信号 |
|---|---|---|
| 输入 | 缺 SWRS 防护 | 参考 SyRS 升格防护 |
| 大纲 | 强制 L1 集合 | SEC-DIFF 强制 |
| 草稿 | shall 句式机器规则 | 参考措辞渗入扫描 |
| 验证 | Direction / forbidden 扫描 | matrix file_id 防护 |
| 交付 | open 完整性 | 参考边界声明 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 把本项目 SYS-xx / 接口 / 限值写入 candidate | 项目事实泄漏 |
| candidate `active: true` | 越权启用 |
| patch 含 hazard / ASIL / SG / TSR 模板 | 文档类型边界破坏 |
| patch 含本次 Δ 具体差异 | 项目事实泄漏 |
| 从 `runs/<run_id>/learning/` 自动应用 patch | 控制失效 |

### 常见 P1

- signals[].`evidence_from_run` 写得过具体
- promotion_report 缺 risk 字段
- 与现有 skill 冲突未列

## A1 / A2 / B

**A1**：candidate `active: false` 且 `status: proposed`；无项目事实泄漏；promotion_report 含人工审查要求。  
**A2**：收紧 patch 范围；删去具体事实；补 risk 字段。  
**B**：promotion_report 须人工审查后启用；候选只补强流程/checklist，不替代项目事实。
