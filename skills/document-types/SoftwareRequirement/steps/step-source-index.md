# SwRS 子 skill · Step 3 · 文档目录索引

骨架：`skills/workflow-steps/step-source-index/SKILL.md`。领域规则：`skills/document-types/SoftwareRequirement/SKILL.md`。

## 本步目的要点

- 为每份输入建立 `L1 -> L2 -> L3` 目录树
- 为后续软件需求写作提供唯一导航入口
- 历史项目参考资料只做结构索引，不入事实 topic

## topic_index 建议主题

- 上游系统需求
- 当前项目系统架构
- 软件功能行为
- 软件接口
- 时序/性能
- 资源/平台约束
- 诊断/故障处理
- 安全相关软件约束
- 追溯 ID

## Checklist

- [ ] 每份 source 有 L1/L2/L3 toc
- [ ] L3 含 `location`
- [ ] 每个主题至少命中一个本项目 source，或显式 gap
- [ ] 当前项目 `SystemArchitecture` 中与软件相关章节可精确导航
- [ ] 历史项目 `SystemArchitecture` 仅建 toc，不进事实 topic
- [ ] 接口主题能定位到方向、对端、触发/周期信息所在位置

## From-Scratch

- [ ] 若当前项目架构未成文，则以现有接口规范/系统需求建立最低索引
- [ ] 无法定位的软件运行模式、故障处理逻辑登记 gap

## With-SystemArchitecture-Reference

- [ ] 历史架构和本项目架构 topic 完全分离
- [ ] 历史架构不可作为 `provenance.file_id`
- [ ] 差异类主题单独登记，供后续 `SEC-DIFF` 使用

## Review 要点

| 检查点 | 通过条件 |
|---|---|
| 导航性 | 每类 critical claim 都能追到 source 段落 |
| 区分度 | 当前项目架构与历史参考架构不混 |
| 接口可检索性 | 方向、周期、超时、对端有定位或 gap |
| 追溯前置条件 | 上游需求 ID 可定位 |

## 常见 P0

- 历史项目架构被编入事实 topic
- L3 无 `location`
- 接口主题不可导航却继续写接口需求

## A1 / A2 / B

**A1**：索引可导航、topic 清晰、参考边界正确。  
**A2**：补 toc、补 location、拆分事实与参考 topic。  
**B**：Step 6 的 EVD 必须只从本步可导航的 source 中取证。
