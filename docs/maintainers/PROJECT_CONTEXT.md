# Project Context Brief

Status: Post-N8 current context brief.

本文档是当前项目状态的维护者索引。它不替代 `README.md`、`docs/RUNBOOK.md`、`docs/CURRENT_ARTIFACT_CONTRACTS.md` 或 `docs/maintainers/ARCHITECTURE.md`。

当前项目已经从 HARA 单点 MVP 泛化为一个 AI 专业文档写作 Claude Code 插件技术预览版，支持四类 official L3 built-in document types：

- `hara`
- `technical_solution`
- `test_report`
- `fsr`

`generic_document` 是 L1 generic mode，不是 official L3。`custom_technical_note` 是 external `document_profile.yaml` demo，不是 official L3。`TechnicalSafetyConcept` 为 document-type skill 层类型，已接入（task_type: TechnicalSafetyConcept）；其下游 HSC / SSC 仍 deferred。

## 当前入口

- 用户说明：`README.md`
- 文档导航：`docs/README.md`
- 泛化架构：`docs/maintainers/ARCHITECTURE.md`
- Roadmap：`docs/maintainers/ROADMAP.md`
- Runbook：`docs/RUNBOOK.md`
- Artifact contract：`docs/CURRENT_ARTIFACT_CONTRACTS.md`
- 新 document type 开发指南：`docs/DOCUMENT_TYPE_DEVELOPMENT_GUIDE.md`
- HARA baseline：`docs/baselines/HARA_MVP_BASELINE.md`

历史 phase / process / handoff 材料不再作为 tracked public docs 保留；如本地存在 `docs/archive/` 或 `local_archive/`，只作历史参考，不作为当前 Codex 执行指令。

未来新增能力应先创建新的 active phase/spec 文档。

## 项目目标

本项目开发一个运行在 Claude Code 中的 AI 专业文档写作插件。

系统目标是引导用户完成可追踪、可 review、证据边界明确的写作流程：

```text
input materials -> material inventory -> source index -> template outline -> evidence map -> citation plan -> section tasks -> conservative draft -> review -> verification -> revision -> final report -> run summary -> candidate profile update
```

当前实现由一套 deterministic Python engine 执行 artifact 生成、review、verify、final delivery、trace 和 proposed candidate learning。文档类型差异由 `DocumentTypeRules` 表达。

## 核心原则

- Template first：用户提供的 `template` 是目标文档结构约束；
- Source first：`source` 是项目事实基础；
- Sample is not fact source：`sample` 和 expected output 只能用于结构、风格、表格形态，不能支持事实或专业结论；
- Reference is not project fact source：`reference` 可支持方法论或背景，不能证明项目事实；
- Human-in-the-loop：critical claims 必须保留 HITL 边界；
- No automatic stable skill/profile replacement：candidate profile update / candidate patch 只能保持 proposed/inactive，不能自动应用。

## 当前支持范围

| `task_type` | 文档类型 | 默认交付状态 | 关键边界 |
| --- | --- | --- | --- |
| `hara` | HARA 危害分析报告 | `finalized_with_open_items` | HARA 专业判断不能自动确认 |
| `technical_solution` | 技术方案文档 | `ready_for_human_review` | 架构、性能、安全、成本、rollout 等判断需要 evidence/HITL |
| `test_report` | 测试报告 | `ready_for_human_review` | pass/fail、缺陷、覆盖率、release readiness 不能编造 |
| `fsr` | FSR 功能安全需求文档 | `ready_for_human_review` | FSR wording、safety goal linkage、ASIL inheritance、verification/compliance 结论需要 evidence/HITL；TSC 不自动生成 |

扩展支持：

- `generic_document`：L1 generic mode。
- validated external `document_profile.yaml`：L2 external profile mechanism，包括 `custom_technical_note` demo。

## Repository boundaries

本仓库应包含插件源码、deterministic fixtures、测试、Claude Code command、Skills/guidelines 和必要文档。

以下目录是可选本地参考资料，fresh clone 不依赖它们：

- `superpowers本体架构/`
- `HARA报告生成参考资料集_EPS/`

如果这些目录存在，只能作为只读参考，不应修改，也不应让插件、CLI 或测试依赖它们。

## 当前非目标

当前技术预览不是：

1. 自动合规批准系统；
2. 任意专业文档自动生成平台；
3. RAG / vector DB / LangChain 平台；
4. 自动 stable skill/profile 替换系统；
5. 无人值守专业结论生成系统；
6. TSC / Technical Safety Concept L3 implementation。
