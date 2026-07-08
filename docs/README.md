# Documentation

本目录包含 AI 专业文档写作 Claude Code 插件的用户文档和维护者参考文档。

普通 GitHub 用户建议先阅读 Quickstart，再根据需要阅读 Troubleshooting、Reading Outputs、User Guide、Examples 和 Document Profiles。

## 用户文档

- [Quickstart](QUICKSTART.md)：clone 仓库后的本地安装、加载 Claude Code 插件和第一次运行。
- [Troubleshooting](TROUBLESHOOTING.md)：首次加载插件、Python 命令、`runs/` 输出和 pending confirmation 的常见排查。
- [Reading Outputs](READING_OUTPUTS.md)：生成输出的推荐阅读顺序、artifact 用途和 pending 状态解释。
- [User Guide](USER_GUIDE.md)：准备 `task.yaml`、选择 `task_type`、理解 material roles 和读取输出。
- [Examples](EXAMPLES.md)：已提交 demo 的运行命令、推荐顺序、artifact 检查和边界说明。
- [Document Profiles](DOCUMENT_PROFILES.md)：`generic_document`、external `document_profile.yaml`、candidate profile 和 promotion gate。

## 维护者文档

- [Runbook](RUNBOOK.md)：维护者运行检查和常用操作。
- [Artifact Contracts](../contracts/CURRENT_ARTIFACT_CONTRACTS.md)：当前 artifact tree 和 contract。
- [Document Type Development Guide](DOCUMENT_TYPE_DEVELOPMENT_GUIDE.md)：未来新增文档类型的开发指南。
- [Document Profile Spec Template](DOCUMENT_PROFILE_SPEC_TEMPLATE.md)：`Markdown Spec` 模板。
- [Technical Decisions](TECHNICAL_DECISIONS.md)：当前技术决策。
- [Runtime Context Boundary](maintainers/RUNTIME_CONTEXT_BOUNDARY.md)：运行期 prompt、维护者文档、contract、examples 和 runs 的上下文边界。

## 架构与路线

- [Architecture](maintainers/ARCHITECTURE.md)
- [Roadmap](maintainers/ROADMAP.md)
- [Project Context](maintainers/PROJECT_CONTEXT.md)

## document type specs

- [FSR Spec](document_types/fsr_SPEC.md)
- [Generic Document Spec](document_types/generic_document_SPEC.md)
- [Technical Solution Spec](document_types/technical_solution_SPEC.md)
- [Test Report Spec](document_types/test_report_SPEC.md)

历史 phase docs、handoff materials、prompt files 和 acceptance records 不属于当前 public self-service documentation。如果本地存在 archive 目录，它们只作为历史参考，不是当前执行指令。
