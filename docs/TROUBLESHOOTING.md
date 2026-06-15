# Troubleshooting

这份文档覆盖普通 GitHub 用户首次本地运行时最常见的问题。

## `validate` 通过但插件命令不显示

症状：

```bash
claude plugin validate .
```

通过，但 Claude Code 里看不到 `/ai-writing-plugin:write`。

原因通常是：`validate` 只校验 manifest，不会把命令加载进当前 Claude Code 会话。

从仓库根目录启动新的会话：

```bash
claude --plugin-dir .
```

然后在新会话里运行：

```text
/ai-writing-plugin:write "Run the writing workflow with examples/technical_solution_demo_fixture/task.yaml"
```

## 当前目录不对

请确认你在仓库根目录。根目录应包含：

```text
.claude-plugin/plugin.json
commands/write.md
pyproject.toml
```

如果缺少这些文件，先 `cd` 到实际 clone 的 `AI_writer_plugin` 目录。

## Python 命令不可用

优先使用仓库内 virtual environment：

```bash
.venv/bin/python -m ai_writing_plugin write-run --task examples/technical_solution_demo_fixture/task.yaml
```

如果 `.venv/bin/python` 不存在，先创建并安装：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

如果已经激活 venv，也可以使用：

```bash
python -m ai_writing_plugin write-run --task examples/technical_solution_demo_fixture/task.yaml
```

## `runs/` 出现本地输出

这是正常 runtime output。每次运行会写入：

```text
runs/<run_id>/
```

不要提交这些输出。仓库 `.gitignore` 已忽略 `runs/`，提交前可以检查：

```bash
git status --short -- runs/
git ls-files runs/
```

`git ls-files runs/` 不应输出 tracked files。

## `resume-run` 提示不是 resumable run

症状：

```text
resume-run failed: ... is not a resumable run; run_state.json is missing
```

原因通常是该目录来自旧版本运行，或只执行了 `init-run`。`init-run` 保持非 resumable；可恢复运行从 `ingest-run` 或 `write-run` 开始。

处理方式：重新执行 `ingest-run` 或 `write-run` 创建新的 resumable run。

## `resume-run` 提示 task/profile hash mismatch

`run_state.json` 会记录原始 `task.yaml` 和 external `document_profile.yaml` 的 SHA-256。恢复时如果文件被修改、替换或删除，工具会拒绝继续，避免把不同任务混到同一个 run 里。

处理方式：

- 恢复原始 `task.yaml` / `document_profile.yaml` 后再运行 `resume-run`；
- 如果任务或 profile 确实已经改变，启动新的 `write-run`。

## `resume-run` 提示 lock 仍在运行

症状类似：

```text
run_state lock exists and pid <pid> is alive; another process may be running this run
```

这表示 `.run_state.lock` 中记录的 PID 仍存活。不要同时对同一个 `runs/<run_id>/` 执行两个 workflow。

如果进程已经崩溃且 PID 不存在，`resume-run` 会自动执行 stale lock recovery：替换 lock，把之前的 `running` stage 标记为 `interrupted`，然后继续。

如果 lock 文件内容损坏、缺少 PID 或不是 JSON，工具会失败并要求人工检查。不要静默覆盖无法判断来源的 lock。

## `resume-run` 提示 completed stage is dirty

症状：

```text
resume-run failed: completed stage evidence is dirty: plans/evidence_map.json missing. Start a new write-run or restore the artifact; automatic upstream rewind is not supported in v1.
```

这表示 `run_state.json` 记录某个 stage 已完成，但该 stage 的 required output 缺失、为空、JSON/JSONL 不可解析。V1 不会自动回滚 manifest、删除下游 artifacts 或重跑上游 stage。

处理方式：

- 恢复缺失或损坏的 artifact 后再继续；
- 或启动新的 `write-run`。

## `prepare-stage-review` 提示 unknown stage

`prepare-stage-review` 只接受当前 run lifecycle stage：

```text
ingest
outline
evidence
planning
draft
review
finalize
learning
```

例如 `tsc` 不是当前 stage，也不是已实现的 official L3 document type。遇到 unknown stage 时，不会创建对应 `stage_reviews/<stage>/` 输出。

## `prepare-stage-review` 提示 stage output missing

Stage review package 只能针对已完成 stage 准备。若 required output 缺失、为空、JSON/JSONL 不可解析，先恢复该 stage artifact，或重新创建 run。S1 不会重跑 stage，也不会自动修复原 artifact。

## `validate-stage-review` 提示 issues invalid

常见原因：

- `stage_reviews/<stage>/issues.json` 缺失或不是合法 JSON；
- `schema_version` 不是 `1`，或 `kind` 不是 `stage_review_issues`；
- `run_id` / `stage` 与当前 run 不匹配；
- `status` 使用了 `approved`、`validated`、`compliant`、`professionally_approved` 等批准式语义；
- 高风险 category 例如 `source_policy`、`critical_claim`、`hitl_required`、`citation_or_evidence`、`final_status_policy`、`candidate_update_policy` 设置了 `safe_auto_fix_eligible=true`；
- issue 文本声称 sample/reference 可以证明项目事实；
- issue 文本要求修改 stable profile / Skill，或直接删除 `NEEDS_USER_CONFIRMATION`。

校验失败时会写：

```text
runs/<run_id>/stage_reviews/<stage>/validation_report.json
```

根据 `errors` 修正 `issues.json` 后重新运行 `validate-stage-review`。

## `stage_reviews/` 是否需要提交

不需要。`stage_reviews/` 位于 `runs/<run_id>/` 下，是本地 runtime output。`runs/` 不进 git，提交前仍用：

```bash
git status --short -- runs/
git ls-files runs/
```

## 输出包含 `NEEDS_USER_CONFIRMATION`

`NEEDS_USER_CONFIRMATION`、pending claims、open confirmations 或 blocked verification 通常不是失败。

它们表示插件没有找到足够的项目 `source` 或已记录 HITL 来支持某个 critical claim。应补充真实项目材料，或在 workflow 中记录真实人工确认；不要把 `sample` 或 `reference` 当作项目事实来源。

## `claude plugin validate` 没有在 CI 跑

GitHub runner 未必安装 Claude Code CLI，所以 CI 不一定能运行：

```bash
claude plugin validate .
```

本地发布或交付前仍建议在安装了 Claude Code CLI 的环境中执行该检查。
