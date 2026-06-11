# Contributing

感谢你考虑参与 AI 专业文档写作 Claude Code 插件项目。

本项目当前定位是 technical preview：一套 deterministic Python writing workflow，加 Claude Code command / Skill guideline / 文档类型规则。贡献时请优先保持可运行、可审查、可测试和证据边界清晰。

## 开发准备

从仓库根目录安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

本地检查：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
claude plugin validate .
```

`claude plugin validate .` 需要本机已安装 Claude Code CLI。CI 使用 pytest 覆盖插件 manifest 和 command 结构，不强依赖 Claude Code CLI。

## 贡献边界

请保持以下项目边界：

- 一个插件，一套 pipeline。
- 不为每种文档复制一套 pipeline。
- 不引入 RAG、LangChain、vector DB 或复杂 agent framework。
- 不把 `sample` 或 expected output 当作项目事实来源。
- 不把 `reference` 当作 project-specific fact support。
- critical claim 必须有 `source` 或 HITL，否则保持 pending / `NEEDS_USER_CONFIRMATION`。
- `final_report.md`、eval passed、promotion report 和 candidate update 都不是专业批准。
- candidate update / candidate patch 默认 proposed / inactive，不能自动覆盖 stable profile 或 Skill。
- TSC / Technical Safety Concept 当前 deferred；不要新增 official TSC type、profile、Skill、fixture 或测试目标。

## 文档类型

当前 official built-in profiles：

- `hara`
- `technical_solution`
- `test_report`
- `fsr`

`generic_document` 是通用模式，不是 official built-in profile。`custom_technical_note` 是 external `document_profile.yaml` demo，不是 official built-in profile。

新增 official built-in document type 需要单独 active phase/spec、fixture、tests、Skill guideline 和维护者 review；不要在普通 PR 中顺手添加。

## Git hygiene

运行输出写入：

```text
runs/<run_id>/
```

不要提交 runtime outputs、local archive、缓存或本地参考材料。提交前建议检查：

```bash
git status --short
git status --short -- runs/
git ls-files runs/
```

## Pull request 建议

PR 请尽量小而清楚：

- 说明变更目标和用户影响。
- 列出测试命令和结果。
- 明确是否修改 artifact contract、document type rules 或 command behavior。
- 如果变更 public docs，确认没有引入 professional approval、automatic compliance、TSC implemented 等误导表述。
