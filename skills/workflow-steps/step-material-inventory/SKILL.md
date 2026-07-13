---
name: step-material-inventory
description: 中文优先指导 workflow 第 2 步「材料清单」：由独立 step worker 生成 input_inventory.json，登记每个文件的 role、parse_status 与 fact-source 标记。
---

# Step 2 · 材料清单 (Material Inventory)

工作流第 2 步。把声明的输入材料逐一登记为结构化清单，记录是否解析成功、角色和是否为事实来源。

## 何时使用

- 已完成 Step 1（输入材料声明）。
- 需要核对哪些文件被成功解析、哪些缺失或不支持、哪些是 fact source。

## 输入

- `manifest.json`、`task_brief.json`
- task.yaml 声明的输入文件

## 产出 artifacts

- `inputs/input_inventory.json`

每条文件记录含：`file_id`、`path`、`role`、`format`、`parse_status`、`is_fact_source`、`title`、`notes`、`error_message`。

`parse_status` 取值：`parsed` / `missing` / `unsupported` / `failed`。

## 路径解析与写入规则（必做）

- `task.yaml` 中的输入路径按 `task.yaml` 所在目录解析；不得按当前 shell cwd、`runs/<run_id>/`或worker cwd重新解释。
- 写入 `inputs/input_inventory.json` 时，`files[].path` 必须是已解析、已验证存在、后续步骤可直接读取的绝对路径。
- 禁止把 `../`、`../../`、`../../../inputdoc/...` 或其他依赖当前 cwd 的相对路径原样写入 `files[].path`。
- 若解析后的文件不存在或无法读取，必须把该材料记录为 `parse_status=missing` 或 `failed`，并在 `error_message` 中写明解析基准目录与解析后的绝对路径；不得留给 Step 3 或其他worker再猜路径。

## 边界与约束

- 清单只做"登记"，不做事实判断，也不把 sample/reference 提升为事实来源。
- `missing` / `unsupported` / `failed` 必须如实记录，禁止静默忽略。
- `summary` 字段提供 parsed/fact-source 计数，供后续步骤与人工审查参考。

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

清单建立后，进入 **Step 3 · 文档目录索引**（L1/L2/L3 三级目录 + `source_index.json` + `provenance_index.json` + `document_tocs/` + `knowledge_gaps.md`）。
