---
name: step-verification
description: 中文优先指导 workflow 第 9 步「验证」：由独立 verification step worker 生成 verify_report.json 与 failures.md，对草稿做机械校验并记录失败项。
---

# Step 9 · 验证 (Verification)

工作流第 9 步。对草稿与审查结果做机械验证检查，输出验证报告和失败清单。

## 何时使用

- 与 Step 8（审查）同属同一 review stage。
- 需要把"未通过的检查"显式列出，供修订处理。

## 输入

- `draft/full_draft.md`
- `review/review_report.json`
- `plans/*`、`knowledge/*`

## 产出 artifacts

- `verify/verify_report.json`
- `verify/failures.md`

## verify artifact 硬契约

`verify/verify_report.json` 不得只写 summary / verification_summary。它必须是结构化报告，至少包含：

- `run_id`
- `generated_at`
- `status`：只能取 `passed` / `passed_with_warnings` / `blocked` / `failed`
- `summary`
- `checks[]`：逐项检查结果；每项必须含 `check_id`、`name`、`status`、`severity`、`details`、`related_artifacts`
- `blocking_failures[]`
- `warnings[]`

每个任务专属子 skill 定义的 VC / CHECK-ID 都必须在 `checks[]` 中有明确 pass / warn / fail / blocked 结论。若只输出一段“全部通过”总结、缺少逐项检查，或未覆盖任务专属 VC，则本步自身为 P0 失败。

`verify/failures.md` 必须始终生成。即使没有 blocking failure，也必须写明 run id、摘要、阻塞失败项为空、非阻塞 warnings、人工确认阻塞项、阶段边界说明。任何 failed / blocked check 必须出现在 `failures.md`；不得静默通过。

Stage review worker 审核本步时必须先做 meta-contract 检查：`verify_report.json` 是否使用上述 top-level 字段与任务专属 `check_id`，`failures.md` 是否存在。若报告使用旧式字段（例如 `overall_status`、`verification_checks`）或泛化编号（例如 `VC-001`）替代任务专属 check id，应标为 P0并返回 `needs_revision`；重新派发的原step worker再按 A2 局部重写 `verify/verify_report.json` 与 `verify/failures.md`。不得把内容看起来“通过”的旧格式报告判为 pass。

## 边界与约束

- 验证是确定性检查，不替代专业判断或最终批准。
- 失败项必须如实写入 `failures.md`，不得静默通过。
- 验证须包含：L1/L2/L3 目录完整性、`EVD-xxx` 是否经三级路径可回溯原文（禁止 SRC/chunk 或直接全文读输入文件），见任务专属子 skill。

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

审查 + 验证结果一起进入 **Step 10 · 修订**（`revision_plan.json` + `revised/*`）。
