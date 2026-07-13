---
name: step-input-materials
description: 中文优先指导 workflow 第 1 步「输入材料」：核对 controller 已创建的 Phase 0 scaffold，保留 input role 与 source!=sample 边界，不直接写最终文档。
---

# Step 1 · 输入材料 (Input Materials)

工作流第 1 步。负责核对 controller 已创建的 Phase 0 scaffold。Python 只登记输入refs与task metadata，不做草稿、审查或专业判断。

## 何时使用

- 用户提供材料并希望开始一次专业文档写作 run。
- 需要确认 `task_type`、`target_audience`、`critical_claims`、`requires_human_confirmation` 等任务声明。

## 输入

- 用户的 task.yaml（声明 `task_type` 与 `inputs` 列表）。
- 每个输入声明的 `role` 与 `path`。

## 核对的 controller-owned scaffold refs

- `input_refs.json`
- `manifest.json`
- `task_brief.json`

## Controller-owned Phase 0 precondition

controller必须在派发任何step worker前完成 `init-run → init-progress-ledger → prepare-step-worker-dispatch`。只有 `init-run` 成功并生成三个Phase 0 scaffold files后，才允许准备Step 1 dispatch；初始化失败立即fail closed。

Step 1 worker接收已存在的run，Step 1 worker 不得调用 `init-run`，不得创建、修改或扩展scaffold。它只读核对 `input_refs.json`、`manifest.json` 与 `task_brief.json`，检查输入role、缺失/不支持材料、fact source与sample边界，并让StepResult 引用三个 scaffold files 的最终 path/hash。

## 边界与约束

材料 `role` 不可互换，且 `fact source != sample document`：

- `source`：项目事实来源。
- `template`：结构约束，不是事实支撑。
- `checklist`：审查/验证要求，不是事实支撑。
- `reference`：方法学/背景/术语，不能证明项目事实。
- `sample` / `expected_output_shape`：仅风格、表格形状、章节粒度。

绝不把 sample / reference / expected_output 当作事实证据；解析失败、缺失、不支持格式必须显式报告，不能静默跳过。

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

run 目录建立后，进入 **Step 2 · 材料清单**（产出 `inputs/input_inventory.json`）。
