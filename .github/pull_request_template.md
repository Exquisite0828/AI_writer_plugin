# Pull Request

## Summary

请简要说明本 PR 改了什么，以及为什么需要改。

## Change Type

- [ ] Docs / repository packaging
- [ ] Tests / fixtures
- [ ] Python engine
- [ ] Claude Code command / Skill guideline
- [ ] Document type rules
- [ ] Other:

## Boundary Check

- [ ] 没有把 `sample` 或 expected output 当作项目事实来源。
- [ ] 没有把 `reference` 当作 project-specific fact support。
- [ ] 没有把 `final_report.md`、eval passed、promotion report 或 candidate update 写成专业批准。
- [ ] 没有让 candidate update / candidate patch 自动覆盖 stable profile 或 Skill。
- [ ] 没有新增 TSC official type、profile、Skill、fixture 或测试目标，除非有单独 active phase/spec。
- [ ] 没有为每类文档复制一套 pipeline。
- [ ] 没有提交 `runs/` runtime outputs。

## Tests

请贴出已运行的命令和结果：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
claude plugin validate .
```

如果没有运行某项检查，请说明原因。
