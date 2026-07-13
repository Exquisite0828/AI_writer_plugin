# Documentation

文档按当前实现、运行时协议、设计资产和历史记录分层。

## 用户文档

- [Quickstart](QUICKSTART.md)：安装、加载插件，以及Python Phase 0与Claude Code worker路径的区别。
- [User Guide](USER_GUIDE.md)：task、材料角色、运行阶段和能力边界。
- [Examples](EXAMPLES.md)：可显式选择的fixture及其当前用途。
- [Reading Outputs](READING_OUTPUTS.md)：Python-enforced metadata与worker artifact的阅读方式。
- [Troubleshooting](TROUBLESHOOTING.md)：当前真实命令和agent-runtime故障排查。

## 维护者文档

- [Runbook](RUNBOOK.md)：当前CLI、metadata协议和维护检查。
- [Current Artifact Contracts](../contracts/CURRENT_ARTIFACT_CONTRACTS.md)：当前Python-enforced schema及worker ownership边界。
- [Project Context](maintainers/PROJECT_CONTEXT.md)：最短当前状态说明。
- [Architecture](maintainers/ARCHITECTURE.md)：当前架构与未来目标的明确分离。
- [Roadmap](maintainers/ROADMAP.md)：从当前scaffold/metadata基线出发的未来顺序；不是active phase。
- [Technical Decisions](TECHNICAL_DECISIONS.md)：当前代码实际采用的技术决策。
- [Runtime Context Boundary](maintainers/RUNTIME_CONTEXT_BOUNDARY.md)：运行期上下文规则。

## 设计和指导资产

- [Document Profiles](DOCUMENT_PROFILES.md)：尚未被当前Python加载的profile设计资产。
- [Document Type Development Guide](DOCUMENT_TYPE_DEVELOPMENT_GUIDE.md)：未来active phase开发类型时的完成门槛。
- [Document Profile Spec Template](DOCUMENT_PROFILE_SPEC_TEMPLATE.md)：候选profile上游说明模板。
- [Generic Document Spec](document_types/generic_document_SPEC.md)
- [Technical Solution Spec](document_types/technical_solution_SPEC.md)
- [Test Report Spec](document_types/test_report_SPEC.md)
- [FSR Spec](document_types/fsr_SPEC.md)

这些Spec和profile文件不等于当前Python engine支持。

## 历史记录

- [Baselines](baselines/README.md)：带明确历史状态的结构快照。

历史phase/process计划由Git历史保留，不属于当前自助执行文档。任何未来实现必须先创建明确的active phase/spec。
