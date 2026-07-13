---
name: step-revision
description: 中文优先指导 workflow 第 10 步「修订」：由独立 step worker 生成 revision_plan.json 与 revised/full_draft.md、change_log.md，按审查与验证结果受控修订草稿。
---

# Step 10 · 修订 (Revision)

工作流第 10 步。基于审查报告与验证失败项，生成受控修订计划并产出修订后草稿与变更日志。

## 何时使用

- 已完成 Step 8/9（审查与验证）。
- 需要把审查/验证发现转化为可追溯的修订。

## 输入

- `review/review_report.json`、`review/final_review.md`
- `verify/verify_report.json`、`verify/failures.md`
- `draft/full_draft.md`、`plans/*`、`knowledge/*`

## 产出 artifacts

- `revision_plan.json`
- `revised/full_draft.md`
- `revised/change_log.md`

## 边界与约束

- 修订是确定性的，依据审查/验证结果，不引入未支撑的新结论。
- 无法解决的开放项继续带入最终交付的 open items，保持 pending。
- 修订不得破坏 `EVD-xxx` → L1/L2/L3 + `location` 溯源链；补证据须 **L1→L2→L3→读原文**，禁止旧版 chunk/SRC 或直接打开输入文件摘录。

## 当前 worker 与 document-type guidance

当前 step worker 只能通过 StepContextPackage.instruction_refs[] 中的 path/hash 读取已纳入 package 的 instructions。wrapper 与本 canonical workflow Skill 是必需引用；document-type root Skill 与 per-step overlay 都按文件存在性懒加载，未出现时不加入 package。root Skill 存在但 per-step overlay 缺失是合法的 root-only 模式；可选 document-type root Skill 或 overlay 未出现不得判为 `metadata_invalid`。所有实际出现在 `instruction_refs[]` 中的引用都必须通过 path/hash 校验；已包含的引用缺失或 hash 无效时返回 `metadata_invalid` 并停止。不得由 controller 直接加载这些正文，不得读取 sibling document types。

## StepResult 与 stage review交接

当前 step worker 读取允许的refs，生成本步声明的专业artifacts，写入并自行校验StepResult，然后返回并结束。它不得继续派发其他worker，也不得创建独立审核状态或stage gate。

Stage review worker 在本stage所有StepResult完成后由controller统一调度，只接收ReviewContextPackage路径。它按 `steps[]` 顺序沿 `context_package_refs[]` 读取本canonical与当前document-type guidance；overlay存在时叠加其领域检查。

### A1/B 通用审核检查

- 本步声明的必需artifact均存在，StepResult path/hash与最终文件一致。
- 产出满足本canonical的输入、输出、顺序和边界约束。
- sample/reference未被当作项目事实，critical claim缺T0/T1时仍为pending或 `NEEDS_USER_CONFIRMATION`。
- 未生成批准、合规、风险接受或生产就绪结论。
- 当前document-type guidance存在时，其A1/B领域检查全部执行。

### A2 局部修订

Stage review worker只记录问题，不修改专业artifact或StepResult。它必须先汇总写入 `stage_reviews/<stage>/issues.json`，再对该stage一次性调用 `build-stage-review-issues` 与 `validate-stage-review-issues`，由builder原子生成并校验固定路径的index/details。本step存在P0/P1或明确返工项时，其ReviewResult返回 `needs_revision`；P2/P3只进入review/open items。A2由重新派发的原step worker执行，并绑定 `issue_id`、`target_artifact`、`changed_paths`；A2 worker不得自行派发其他step。若目标不是最后一步，controller按自动依赖协议重跑被失效的后续step。

Stage review worker为本step写入并校验一个ReviewResult，不创建第二套持久化编排状态。

## 交接到下一步

进入 **Step 11 · 最终报告**（`final/final_report.md` + `final/delivery_summary.md`）。
