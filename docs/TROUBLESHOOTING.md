# Troubleshooting

本页只覆盖当前真实CLI和Claude Code agent-runtime协议。

## 插件校验通过但命令不显示

`claude plugin validate .`只校验manifest。请从仓库根目录启动新会话：

```bash
claude --plugin-dir .
```

然后检查`/ai-writing-plugin:write`。

## Python提示unknown command

先查看当前命令：

```bash
.venv/bin/python -m ai_writing_plugin --help
```

当前CLI没有一键写作、resume、profile、eval或promotion命令。旧文档中的这些命令不适用于当前分支。

## `init-run`找不到task

错误通常类似：

```text
task file not found
```

确认命令从预期目录运行，并使用存在的task路径：

```bash
.venv/bin/python -m ai_writing_plugin init-run --task path/to/task.yaml
```

## task YAML解析失败

当前parser只支持受限YAML子集。常见原因：

- 顶层不是简单mapping；
- 使用嵌套mapping或复杂inline collection；
- list缩进不符合当前task格式；
- bracket不平衡；
- bool写成非`true/false`形式。

按README中的task示例简化。解析失败不会被静默忽略。

## 输入文件不存在

`inputs[*].path`相对于task文件目录解析。路径必须指向普通文件，不能使用glob。修正路径后创建一个新run；不要手工修改已经生成的`input_refs.json`。

## sample被强制降级

如果路径看起来属于sample/example/expected output，系统会强制：

```text
fact_source_allowed = false
```

即使task请求把sample作为事实来源，也只会产生warning或validation failure。这是安全边界，不是bug。

## run目录已存在

同一`--run-id`不能覆盖已有目录。使用新的安全run id，或省略`--run-id`让工具生成时间戳id。不要删除或覆盖一个仍需审计的run。

## `worker_unavailable`

`/write`要求真实Task/Agent worker handoff。如果宿主环境没有该能力，主agent必须停止。处理方式：

1. 确认当前Claude Code版本/环境支持独立worker；
2. 确认插件是在新会话中加载；
3. 不要要求主agent在同一长期上下文代执行step；
4. 仅需验证Python层时，改用`init-run`和metadata命令。

## `metadata_invalid`

不要手工修JSON。按固定顺序重新检查：

```text
validate-step-context-package
validate-step-worker-dispatch
validate-step-result
complete-step-worker-dispatch
validate-progress-ledger
```

常见原因：

- missing或extra field；
- stage-step pair错误；
- status不在允许集合；
- path不是run-relative POSIX路径；
- referenced file缺失；
- SHA-256已变化；
- result path list与hash map key不一致。

## context package已经存在

Builder默认拒绝覆盖。只有在你明确知道旧package不再有效时才使用对应`--overwrite`或`--overwrite-package`参数。覆盖后必须重新生成依赖它的dispatch/result绑定。

## task brief或input ref hash mismatch

这些文件是scaffold-owned输入边界。原task/input变化后，旧hash引用应失效。创建新run通常比手工修补安全。

## ProgressLedger校验失败

检查：

- ledger的`run_id`是否等于run目录名；
- 同一stage/step是否重复；
- refs是否存在并匹配hash；
- result本身是否先通过validator；
- 是否在complete dispatch后又修改了result。

Ledger只能通过当前builder更新，不要手工patch。

## ReviewContextPackage构建失败

Builder要求列出的每个step已经有：

- 对应StepContextPackage；
- 对应且有效的StepResult。

`--step`顺序必须与当前stage实际steps一致。可选`stage_review_refs`只会引用已经存在的允许文件；builder不会创建review内容。

## StageGateResult等待确认

没有decision文件时，默认状态是：

```text
pending_user_confirmation
```

这是正确的fail-closed行为。不要伪造decision。即使status为`accepted`，也只表示编排可以继续，不是专业批准。

注意：当前builder允许`--status`覆盖且validator只做结构校验；它本身不能证明存在用户决定或review。Agent runtime不得把无真实decision的`accepted`覆盖值当作继续依据。

## context budget失败

```bash
.venv/bin/python -m ai_writing_plugin check-context-budget \
  --root . --task-type hara --step step-input-materials --json
```

该检查测量runtime Markdown surface的确定性估算，不测量真实provider prompt-cache hit rate，也不评估文档质量。

## pytest不可用

安装dev依赖：

```bash
.venv/bin/python -m pip install -e ".[dev]"
```

然后运行：

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider
```

## runtime output出现在Git状态中

```bash
git status --short -- runs/
git ls-files runs/
```

`runs/`应被ignore且没有tracked文件。不要提交runtime artifacts。

## TSC状态看起来冲突

统一口径是：`TechnicalSafetyConcept`的Skill、step overlays和fixture存在；它不是official L3，且没有Python rules/registry、端到端内容CLI或专门engine test。Official L3 TSC与HSC/SSC仍deferred。
