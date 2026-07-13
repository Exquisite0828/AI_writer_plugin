# Reading Outputs

当前仓库有两类输出：Python强制生成/校验的metadata，以及Claude Code worker在真实执行后可能生成的专业artifact。不要把两者混为一谈。

## 1. Python Phase 0输出

`init-run`只创建：

```text
runs/<run_id>/input_refs.json
runs/<run_id>/manifest.json
runs/<run_id>/task_brief.json
```

推荐顺序：

1. `manifest.json`：确认`status=initialized`、`phase=phase_0`和task路径。
2. `task_brief.json`：确认task type、标题、受众和人工确认要求。
3. `input_refs.json`：确认每个输入的path、hash、role、read policy和fact-source permission。

Phase 0之后没有final report可读，因为Python没有执行内容阶段。

## 2. Orchestration metadata

当agent workflow开始调度worker后，重点查看：

```text
orchestration/progress_ledger.json
orchestration/context_packages/<stage>/<step>.json
orchestration/worker_dispatches/<stage>/<step>.json
orchestration/step_results/<step>.json
orchestration/review_context_packages/<stage>.json
orchestration/review_results/<stage>/<step>.json
orchestration/stage_gate_results/<stage>.json
stage_reviews/<stage>/issues.json
stage_reviews/<stage>/issues_index.json
stage_reviews/<stage>/issues/<issue_id>.json
```

推荐顺序：

1. ProgressLedger：当前step状态及result refs。
2. StepResult：worker报告的artifact paths/hashes和blocking count。
3. Stage-review issues：`issues.json`是review worker的严格source；`issues_index.json`是紧凑索引，逐issue detail保存有界的定位、理由和建议。先运行builder/validator，再使用这些输出。
4. Per-step ReviewResults：同一个stage review worker为该stage每个step报告package refs和blocking count；逐项确认ledger中的`review_result_ref`已绑定最终hash。
5. StageGateResult：是否可以继续、需要修订、blocked或等待用户确认。

Metadata只能证明shape、path、hash和状态关系。它不证明专业内容正确。

## 3. Worker professional artifacts

只有对应worker确实完成并在StepResult中报告后，才读取下列目录：

```text
inputs/
knowledge/
plans/
draft/
review/
verify/
revised/
final/
trace/
learning/
```

常见阅读路线：

```text
source/provenance
-> evidence and claim support
-> citation/section tasks
-> draft
-> review and verification
-> revision
-> review-ready final
```

具体路径由当前step Skill和`contracts/CURRENT_ARTIFACT_CONTRACTS.md`的worker ownership说明决定。Python当前不创建或语义校验这些内容。

## 4. Pending和open状态

以下状态可能是正确结果：

- `NEEDS_USER_CONFIRMATION`；
- pending/open claim；
- missing evidence；
- blocked verification；
- `pending_user_confirmation` stage gate；
- proposed/inactive candidate material。

它们表示系统没有足够项目证据或人工决定。不要通过手工删除标记把问题伪装成已解决。

## 5. Approval boundary

- hash match不是事实认证；
- StepResult done不是专业批准；
- ReviewResult done不是专业批准；
- StageGateResult accepted只允许编排继续；
- verification没有发现机械错误，不代表结论正确；
- `final_report.md`只能是review-ready文档；
- candidate material不会被当前Python自动激活。

## 6. Source boundary检查

在worker artifact中追溯claim时，至少确认：

1. citation指向存在的evidence；
2. evidence指向明确source/provenance位置；
3. source role允许事实支持；
4. sample/reference没有被升级为项目事实；
5. evidence内容真正支持claim，而不只是关键词相似；
6. critical claim缺少T0/T1时仍保持open。

## 7. Missing output

不存在某个专业目录时，先检查：

- 对应step是否真的被独立worker调度；
- StepResult是否存在且通过validator；
- ProgressLedger是否绑定该result；
- stage是否blocked或等待用户确认；
- 当前环境是否报告`worker_unavailable`。

不要依据旧Phase 0-8文档假设所有目录都应由`init-run`预创建。
