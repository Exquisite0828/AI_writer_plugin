---
name: Bug report
about: Report a reproducible problem in the plugin, CLI, docs, or artifacts
title: "[Bug]: "
labels: bug
assignees: ""
---

## 问题描述

请简要说明发生了什么。

## 复现步骤

```bash
# paste commands here
```

## 预期行为

请说明你期望看到什么。

## 实际行为

请说明实际输出、错误信息或生成的 artifact 状态。

## 环境

- OS:
- Python version:
- Claude Code CLI version, if relevant:
- Commit hash:

## 相关文件

请列出相关 `task.yaml`、输入材料路径或 `runs/<run_id>/` artifact 路径。

不要上传敏感材料。`runs/` 输出可能包含项目材料摘要，请先脱敏。

## 边界检查

如果问题涉及文档内容，请说明是否涉及：

- `sample` 被当作事实来源；
- `reference` 被当作项目事实；
- missing HITL / `NEEDS_USER_CONFIRMATION`；
- final report / eval / promotion report 被误写成专业批准；
- TSC 被误写成已实现或已生成。
