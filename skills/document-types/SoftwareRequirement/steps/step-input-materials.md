# SwRS 子 skill · Step 1 · 输入材料

骨架：`skills/workflow-steps/step-input-materials/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 创建 `runs/<run_id>/` 并确认 `task_type: SoftwareRequirement`
- 登记每份输入的 `file_id`、path、title、format、role、`is_fact_source`
- 固定 **当前项目架构 vs 历史项目架构参考** 的 tier 边界
- 声明 SwRS critical claims 需要 T0/T1 或 `NEEDS_USER_CONFIRMATION`

## 输入分类 Checklist

- [ ] `system_requirement` / `syrs` 已登记为 `source`
- [ ] **当前项目** `SystemArchitecture` 已登记为 `source`
- [ ] **历史项目** `SystemArchitecture` 报告已登记为 `sample` 或 `reference`，绝不为 `source`
- [ ] 接口规范 / CAN 矩阵 / 诊断接口已登记或显式 gap
- [ ] 平台/芯片/OS/BSW 约束已登记或显式 gap
- [ ] TSR / 软件安全输入（若有）已登记并注明“仅供引用”
- [ ] SwRS 模板为 `template`
- [ ] SWE.1 / ISO 26262 检查清单为 `checklist`
- [ ] `task_brief` 已声明：不写 HARA、TSC、Software Architecture 终稿、批准/合规结论

## 事实来源边界 Checklist

- [ ] `fact source != sample`
- [ ] 历史项目 `SystemArchitecture` 只可用于章节形状、列定义、差异启发
- [ ] 历史项目资料不得支撑 `SWR-F-xx`、`SWR-IF-xx`、周期、超时、内存、CPU、故障响应
- [ ] 若用户口头确认“沿用历史方案”，仍需 T0 HITL 记录，不能直接引用 sample

## From-Scratch

- [ ] 无当前项目架构输入时，登记 `knowledge_gaps`
- [ ] 无接口规范时，不得默认接口方向/周期
- [ ] 无软件安全输入时，`SEC-SAFE-SW` 预期为 open

## With-SystemArchitecture-Reference

- [ ] 历史项目 `SystemArchitecture` 的 `file_id` 与本项目 source 分离
- [ ] `task_brief` 明示：参考架构仅作 shape/reference
- [ ] 预声明 `SEC-DIFF`，用于记录“本项目相对参考架构/参考需求的差异”

## Review 要点

| 检查点 | 通过条件 |
|---|---|
| 上游输入完备性 | 至少有 SyRS 或等价上游需求；缺则明确阻塞 |
| 架构输入边界 | 当前项目架构是 source；历史项目架构不是 |
| tier 正确性 | template/checklist/reference/sample 均 `is_fact_source=false` |
| 文档边界 | 已声明非架构终稿、非安全分析、非批准 |

## 常见 P0

- 无上游需求却直接启动写作
- 历史项目 `SystemArchitecture` 报告标成 `source`
- 用 reference 代替本项目接口/平台事实
- 未声明关键 open 项就开跑

## A1 / A2 / B

**A1**：role/tier 正确、上游已登记、历史架构边界清楚。  
**A2**：补登记输入、修正 role、补 `knowledge_gaps`。  
**B**：确保后续所有 step 都能区分“当前项目架构 source”与“历史项目架构参考”。
