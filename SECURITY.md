# Security Policy

## Supported Versions

当前仓库处于 technical preview 阶段。安全修复优先面向 `main` 分支。

## Reporting a Vulnerability

请不要在公开 issue 中披露漏洞细节。

如果你发现安全问题，请优先使用 GitHub 的 private vulnerability reporting / repository security advisory 入口提交。报告中建议包含：

- 受影响的文件、命令或 workflow；
- 可复现步骤；
- 预期影响；
- 你已经尝试过的缓解方式。

维护者会在确认问题后评估修复范围，并在不泄露漏洞细节的前提下更新公开 issue、PR 或 changelog。

## Scope

本项目是本地运行的 Claude Code 插件和 deterministic Python writing engine。安全报告优先关注：

- 可能导致本地文件被意外读取或写入的问题；
- 依赖、CI 或 packaging 风险；
- 让 `sample` / `reference` 被错误提升为项目事实来源的缺陷；
- 绕过 HITL、candidate inactive 或 professional-approval 边界的缺陷；
- 插件 command / task input 处理中的 unsafe behavior。

本项目不会把 generated final report、eval passed 或 promotion report 视为专业批准或合规批准。
