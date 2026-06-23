# User Guide

这份指南面向想用本插件基于自己材料生成专业文档的用户。

## 基本 workflow

插件运行一套确定性的 Python workflow：

```text
input materials -> material inventory -> source index -> template outline -> evidence map -> citation plan -> section tasks -> conservative draft -> review -> verification -> revision -> final report -> run summary -> candidate profile update
```

所有支持的文档类型和模式都使用同一套 pipeline 和 artifact tree。文档差异来自内置 `DocumentTypeRules` 或通过校验的 external `document_profile.yaml`。

## Input material roles

在 `task.yaml` 里，每个输入都要声明 role。

| Role | 用途 | 事实来源边界 |
| --- | --- | --- |
| `source` | 项目事实、需求、结果、约束或已确认输入 | 在可解析且相关时，可以支持项目事实 |
| `template` | 必须遵循的结构、标题、格式或表格布局 | 不证明项目事实 |
| `checklist` | review criteria、quality gates 或 completeness checks | 不证明项目事实 |
| `sample` | 示例风格、形态、章节颗粒度或表格组织 | `sample` is not fact source |
| `reference` | 方法、背景、术语或一般 review guidance | `reference` 不能证明项目事实 |

`sample` 和 `reference` 很有用，但不能替代项目 `source`。

## 准备项目目录

一个普通专业文档任务可以先这样组织：

```text
my_doc_task/
  task.yaml
  inputs/
    source.md
    template.md
    checklist.md
    sample.md
    reference.md
```

中文项目也建议先保持路径清晰：

```text
my_doc_task/
  task.yaml
  inputs/
    source.md      # 项目事实、需求、结果或约束
    template.md    # 目标结构或表格形态
    checklist.md   # 审查标准
    sample.md      # 风格示例，不是事实来源
    reference.md   # 通用背景或方法，不证明项目事实
```

`task.yaml` 中的 `inputs[*].path` 相对于 `task.yaml` 所在目录解析。也就是说，`my_doc_task/task.yaml` 里的 `inputs/source.md` 会解析为 `my_doc_task/inputs/source.md`。

## 准备 task.yaml

`task.yaml` 声明文档类型、目标读者、输出格式、需要人工确认的事项和输入文件。

普通专业文档可以先用 `generic_document`：

```yaml
task_type: generic_document
task_title: Generate a project document
target_audience: Reviewers
output_format: markdown
allow_inference: false
requires_human_confirmation:
  - final recommendation
inputs:
  - path: inputs/source.md
    role: source
    notes: Project source material.
  - path: inputs/template.md
    role: template
    notes: Structure only.
  - path: inputs/checklist.md
    role: checklist
    notes: Review criteria only.
  - path: inputs/reference.md
    role: reference
    notes: General methodology only, not project evidence.
  - path: inputs/sample.md
    role: sample
    notes: Style only, not project evidence.
```

路径相对于 `task.yaml` 所在目录解析。

## 选择 document type

`generic_document` 可以作为普通专业文档起点，适合先跑通材料、证据边界和输出目录。official L3 built-ins 是增强场景：它们带有内置规则、fixture、测试和 Skill guideline。

如果任务明确匹配以下类型，优先使用 official L3 built-in：

- `hara`
- `technical_solution`
- `test_report`
- `fsr`

此外，以下 document-type skill 层类型也带有内置规则与逐步子 skill（PascalCase 路径），按需选择：

- `ItemDefinitionDocument`（Item 定义，Clause 5）
- `FunctionalSafetyRequirement`（功能安全需求，Clause 7）
- `TechnicalSafetyConcept`（技术安全概念，Clause 8）

如果你有 `source`、`template`、`checklist`，但没有合适的 document type，继续使用 `generic_document`。

如果你有反复使用的自定义文档类型，并希望用结构化规则描述它，可以使用 external `document_profile.yaml`，而不是新增 built-in。

## official L3 built-ins

### hara

使用：

```yaml
task_type: hara
```

用于 HARA hazard analysis report 辅助写作。

HARA critical claims 包括 hazard identification、hazardous events、S/E/C ratings、ASIL、safety goals 和 final acceptability。这些内容需要 `source` evidence 或 HITL。

### technical_solution

使用：

```yaml
task_type: technical_solution
```

用于架构方案、实现方案或技术方案文档。

Critical claims 包括 architecture decisions、performance targets、security boundaries、cost estimates 和 rollout risk acceptance。

### test_report

使用：

```yaml
task_type: test_report
```

用于测试报告包。

Critical claims 包括 test results、pass/fail status、defect status、coverage sufficiency、final test conclusions 和 release-readiness statements。

### fsr

使用：

```yaml
task_type: fsr
```

用于 Functional Safety Requirements package。

FSR safety requirements、Safety Goal linkage、ASIL inheritance、verification method adequacy、completeness 和 final FSR conclusions 都是 critical claims，不能自动确认。

HARA 输出不能自动转成 FSR 事实来源。用户提供的 HARA summary 只能支持其中明确包含的 trace。

### TechnicalSafetyConcept

使用：

```yaml
task_type: TechnicalSafetyConcept
```

用于 Technical Safety Concept（技术安全概念，ISO 26262-4 Clause 8）package，在已确认的 FSR/SG 与系统架构之上派生技术安全需求（TSR）、安全机制、故障检测与处理、接口安全需求与追溯矩阵。

TSR wording、FSR/SG linkage、architecture allocation、safety mechanism concept、fault handling strategy、FTTI、ASIL inheritance/decomposition、verification method 与 final TSC conclusions 都是 critical claims，不能自动确认。

上游 FSR source 只能支持其明确包含的 FSR-xx 与 SG 链接，不能变成 blanket TSR approval；HARA summary 只能支持显式的 FTTI 与安全状态。TSC 不写 HSC/SSC（硬件/软件安全概念）终稿或详细实现，也不做 TSC 批准或合规结论。demo fixture：`examples/technical_safety_concept_demo_fixture/`。

## generic_document mode

使用：

```yaml
task_type: generic_document
```

`generic_document` 是 generic mode，不是 official L3。适合以下情况：

- 文档仍然由 `source`、`template`、`checklist` 驱动；
- 该领域不需要 built-in rule package；
- unresolved critical claims 可以保持 pending；
- 你希望使用共享 artifact tree 和 review 边界。

它不承诺完整的领域专业判断。

## external profile demo

仓库包含一个 external profile demo：

```text
profiles/document_types/customer_demo/custom_technical_note.yaml
examples/custom_technical_note_profile_demo_fixture/task.yaml
```

对应 `task.yaml` 使用：

```yaml
task_type: custom_technical_note
document_profile_path: profiles/document_types/customer_demo/custom_technical_note.yaml
```

`custom_technical_note` 是 external profile demo，不是 official L3。

## 运行 workflow

在 Claude Code 中加载本地插件后，使用：

```text
/ai-writing-plugin:write "Run the writing workflow with my_doc_task/task.yaml"
```

不用 Claude Code 时，可以使用 Python CLI 备用路径：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task path/to/task.yaml
```

命令会打印运行目录：

```text
runs/<run_id>/
```

## Resume interrupted runs and optional stage review gates

- Interrupted resumable runs can continue with `resume-run --run runs/<run_id>`.
- Stage review packages can be prepared and validated with `prepare-stage-review` and `validate-stage-review`.
- `review_units.json` supports unit-level review coverage for structured issues.
- Users can record `accepted`, `skipped`, `needs_revision`, or `blocked` stage review decisions.
- `--require-stage-review-gates` is opt-in for stricter workflows; the default workflow remains non-gated.
- Gate decisions are `stage_review_gate_only` and are not professional approval.

Detailed operational commands and recovery cases are covered in [Runbook](RUNBOOK.md).

## 读取生成的 artifact

先按这个顺序阅读：

```text
runs/<run_id>/final/final_report.md
runs/<run_id>/final/delivery_summary.md
runs/<run_id>/review/final_review.md
runs/<run_id>/verify/verify_report.json
runs/<run_id>/plans/claim_support_matrix.json
runs/<run_id>/learning/candidate_profile_update.yaml
```

完整说明见 [Reading Outputs](READING_OUTPUTS.md)。

如果需要排查 evidence、provenance、review 和 verification，可以继续查看：

```text
inputs/input_inventory.json
knowledge/source_index.json
knowledge/provenance_index.json
plans/evidence_map.json
plans/citation_plan.json
plans/claim_support_matrix.json
review/review_report.json
verify/verify_report.json
trace/hitl_decisions.jsonl
learning/candidate_profile_update.yaml
learning/candidate_skill_patch.md
learning/promotion_report.md
```

## open items 和 NEEDS_USER_CONFIRMATION

`NEEDS_USER_CONFIRMATION`、pending claim status、open confirmations 或 blocked verification 都可能是正确结果。

它们表示插件没有找到足够的项目 `source` 或已记录 HITL 来支持某个 critical claim。不要手工删除这些标记；应通过真实项目材料或 workflow 记录人工决定。

## 理解 final report

`final_report.md` 是 review-ready package。它不是专业批准文件，不是合规批准，也不是 release decision。

你可以用它检查：

- 已确认的 source facts；
- open confirmations；
- provenance summaries；
- unsupported 或 pending claims；
- review 和 verification findings；
- limitations。

## 运行后做什么

1. 阅读 `final/final_report.md` 和 `final/delivery_summary.md`。
2. 检查 `verify/verify_report.json` 中的 blocked 或 warning checks。
3. 查看 `plans/claim_support_matrix.json` 中 critical claim 的支撑情况。
4. 使用项目 `source` 或已记录 HITL 解决 open confirmations。
5. 将 `learning/candidate_profile_update.yaml` 和 `learning/candidate_skill_patch.md` 视为 proposal。

## candidate updates

Candidate updates 默认 proposed/inactive。

它们不能自动覆盖：

- stable external profiles；
- stable Skill.md files；
- built-in document type rules。

correction harvesting 可以生成 candidate patch，但 stable profile 变更需要 explicit review、eval evidence、promotion gate checks 和 rollback metadata。

## 常见错误

- 把 `sample` 当成项目事实；
- 把 `reference` 当成项目决策证据；
- 没有记录 HITL 就删除 `NEEDS_USER_CONFIRMATION`；
- 把 `generic_document` 叫做 official L3；
- 把 `custom_technical_note` 叫做 official L3；
- 把 eval passed 当成专业批准；
- 把 `final report` 当成专业批准；
- 期待 correction harvesting 自动修改 stable profile；
- 期待 FSR 输出生成 TSC 输出；
- 为每类文档复制一套 pipeline。
