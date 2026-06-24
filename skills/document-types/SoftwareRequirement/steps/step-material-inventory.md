# SwRS 子 skill · Step 2 · 材料清单

骨架：`skills/workflow-steps/step-material-inventory/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 解析 source，形成 `inputs/input_inventory.json`
- 从本项目 source 提取候选 `SWR-F` / `SWR-IF` / 时序 / 资源 / 诊断需求线索
- sample 只提取 `style_hint`，不进入事实字段

## 提取对象 Checklist

- [ ] 上游系统需求 ID、需求摘要、优先级线索
- [ ] 当前项目架构中的软件分配、运行模式、接口边界
- [ ] 软件接口名、方向、触发条件、周期/超时、对端
- [ ] 性能/时序/资源约束
- [ ] 诊断与降级软件行为
- [ ] 安全相关软件约束引用（若有）

## inventory 字段 Checklist

- [ ] 每份材料有 `parse_status`
- [ ] 候选需求均标 `status=candidate`
- [ ] 每条候选 `SWR-F` 有来源文档与定位
- [ ] 每条候选 `SWR-IF` 有方向线索，未知则记 `unknown_pending_confirmation`
- [ ] sample / 历史项目架构仅进入 `style_hint`
- [ ] 解析失败显式记录，不静默跳过

## ASPICE SWE.1 关注点

- [ ] 软件需求不是简单复制上游系统需求，而是已转换为软件层行为/约束
- [ ] 需求与软件架构设计分离，不把任务/模块实现细节写成需求
- [ ] 每条需求有可追溯上游或 open

## From-Scratch

- [ ] 数值型要求无 source 时不填默认值
- [ ] 接口方向、周期、超时未知时保持 open
- [ ] 软件状态机/模式切换若缺 source，仅记线索不记定论

## With-SystemArchitecture-Reference

- [ ] 历史架构中的模块名/任务周期/接口名不进入事实字段
- [ ] 如参考架构启发出新候选，仅可形成问题清单，不能直接形成 requirement
- [ ] 差异线索单独标为 `delta_hint`

## Review 要点

| 检查点 | 通过条件 |
|---|---|
| 提取覆盖 | 功能、接口、时序、资源、诊断、安全引用至少有线索或 gap |
| 需求层级正确 | 是软件需求，不是系统需求照抄，也不是软件架构设计 |
| sample 边界 | 历史架构/历史 SwRS 未流入事实字段 |
| 诚实缺口 | 缺值保留 open，不“帮用户补齐” |

## 常见 P0

- sample 需求/接口进入 inventory 事实字段
- 直接从参考架构抄任务周期、超时、队列长度
- 把软件设计元素（模块、类、线程分配）当成软件需求

## A1 / A2 / B

**A1**：候选需求来源清楚、sample 未入事实字段。  
**A2**：重解析、回退伪事实、补 `delta_hint`。  
**B**：inventory 要能直接支撑 Step 3 的主题索引与 Step 5 的写作计划。
