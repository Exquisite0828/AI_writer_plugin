# Examples

这份指南列出仓库内已提交的 example task files，并说明每个 demo 检查什么能力和边界。

安装依赖后，请从仓库根目录运行示例：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

每个命令都会把输出写到：

```text
runs/<run_id>/
```

demo 常见完成状态：

```text
Status: completed_with_candidate_updates_proposed
```

建议先打开：

```text
runs/<run_id>/final/final_report.md
runs/<run_id>/final/delivery_summary.md
```

如果只是第一次看输出，先读 [Reading Outputs](READING_OUTPUTS.md)，再按本页做 demo 边界检查。

## 推荐 demo 顺序

1. `hara_demo_fixture`：确认原 HARA baseline 仍可运行。
2. `technical_solution_zh_demo_fixture`：中文优先的技术方案 workflow，适合作为中文用户第一个 self-service example。
3. `technical_solution_demo_fixture`：英文材料取向的同类 technical solution regression demo。
4. `test_report_demo_fixture`：展示基于测试结果材料的 test report workflow。
5. `fsr_demo_fixture`：展示 Functional Safety Requirements 支持，同时保持「FSR 不写 TSC」的文档纯净边界。
6. `technical_safety_concept_demo_fixture`：展示 Technical Safety Concept（TSC）支持，在已确认 FSR/SG/架构之上派生 TSR、安全机制、故障处理与追溯。
7. `generic_document_demo_fixture`：展示没有 official L3 built-in 时的 generic mode。
8. `custom_technical_note_profile_demo_fixture`：展示通过校验的 external profile 运行。

## 每个 demo 检查什么

| Demo | 主要用途 | 关键边界 |
| --- | --- | --- |
| `examples/hara_demo_fixture/task.yaml` | HARA hazard analysis report workflow | Hazard、hazardous event、S/E/C、ASIL、safety goal 不能自动确认 |
| `examples/technical_solution_zh_demo_fixture/task.yaml` | 中文 technical solution first demo | Architecture、performance、security、cost、rollout claims 需要 evidence 或 HITL |
| `examples/technical_solution_demo_fixture/task.yaml` | English-oriented technical solution regression demo | Architecture、performance、security、cost、rollout claims 需要 evidence 或 HITL |
| `examples/test_report_demo_fixture/task.yaml` | Test report workflow | Pass/fail、defect、coverage、release-readiness 不能被编造 |
| `examples/fsr_demo_fixture/task.yaml` | Functional Safety Requirements workflow | FSR wording、Safety Goal linkage、ASIL inheritance、verification、completeness、compliance conclusions 需要 evidence 或 HITL；不生成 TSC |
| `examples/generic_document_demo_fixture/task.yaml` | Generic mode | 依赖用户提供的 `source`、`template`、`checklist` 和 profile 边界；不承诺完整领域判断 |
| `examples/custom_technical_note_profile_demo_fixture/task.yaml` | External profile demo | `custom_technical_note` 是 external `document_profile.yaml` demo，不是 official L3 |

## HARA demo

Task:

```text
examples/hara_demo_fixture/task.yaml
```

支持级别：official L3 built-in。

运行：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/hara_demo_fixture/task.yaml
```

展示：

- HARA `source` / `template` / `checklist` / `sample` / `reference` 处理；
- Hazard、hazardous event、S/E/C、ASIL 和 safety goal 边界；
- 没有 `source` 或 HITL 时，HARA critical claims 保持 pending。

边界：

- HARA `sample` 只能指导结构和风格；
- HARA 专业判断不会被自动 finalized。

## Chinese Technical Solution demo

Task:

```text
examples/technical_solution_zh_demo_fixture/task.yaml
```

支持级别：official L3 built-in。

运行：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/technical_solution_zh_demo_fixture/task.yaml
```

展示：

- 中文材料下的 technical solution 写作；
- 基于系统上下文和需求材料生成技术方案交付包；
- Architecture、performance、security、cost、rollout claim checks；
- sample / reference 不能作为项目事实来源。

边界：

- `reference` 只能提供通用灰度发布架构背景，不能证明项目特定需求或决策；
- `sample` 只能提供风格和章节形态；
- final architecture decisions 需要项目 `source` 或 HITL。

## Technical Solution demo

Task:

```text
examples/technical_solution_demo_fixture/task.yaml
```

支持级别：official L3 built-in。

运行：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/technical_solution_demo_fixture/task.yaml
```

展示：

- 基于英文材料取向的 system context 和 requirements 的 technical solution 写作；
- Architecture、performance、security、cost、rollout claim checks；
- HARA terminology leakage prevention。

边界：

- Architecture `reference` 不能证明项目特定需求或决策；
- final architecture decisions 需要项目 `source` 或 HITL。

## Test Report demo

Task:

```text
examples/test_report_demo_fixture/task.yaml
```

支持级别：official L3 built-in。

运行：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/test_report_demo_fixture/task.yaml
```

展示：

- 基于 test plan、result、defect 和 environment materials 生成 test report；
- Pass/fail、defect、coverage 和 final test conclusion 边界；
- 安全处理 sample report wording。

边界：

- Test results、defect state、coverage 和 release-readiness claims 不能被编造；
- sample test report 不是本项目测试结果的 evidence。

## Generic Document demo

Task:

```text
examples/generic_document_demo_fixture/task.yaml
```

支持级别：generic mode。

运行：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/generic_document_demo_fixture/task.yaml
```

展示：

- 没有 official L3 built-in 时仍可使用共享 writing workflow；
- 用户声明的 critical claims 和 required confirmations；
- generic document artifact tree 和 review flow。

边界：

- `generic_document` = generic mode，不是 official L3；
- 它不提供完整领域专业判断。

## Custom Technical Note external profile demo

Task:

```text
examples/custom_technical_note_profile_demo_fixture/task.yaml
```

支持级别：external `document_profile.yaml` demo。

Profile:

```text
profiles/document_types/customer_demo/custom_technical_note.yaml
```

运行：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/custom_technical_note_profile_demo_fixture/task.yaml
```

展示：

- External profile loading and validation；
- 自定义 critical claims 和 final-status policy；
- profile metadata 在 artifacts 中传播。

边界：

- `custom_technical_note` = external profile demo，不是 official L3；
- external profile guidance 不批准专业内容；
- candidate updates remain proposed/inactive。

## FSR demo

Task:

```text
examples/fsr_demo_fixture/task.yaml
```

支持级别：official L3 built-in。

运行：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/fsr_demo_fixture/task.yaml
```

展示：

- Functional Safety Requirements package generation；
- Safety Goal traceability、ASIL inheritance、verification method 和 requirement completeness 边界；
- FSR-specific TSC leakage prevention。

边界：

- `fsr` = official L3；
- FSR safety requirements 是 critical claims，不能自动确认；
- HARA summary 只能支持其中明确包含的 trace；
- FSR output 不能变成 TSC deliverable。

## 需要检查的 artifacts

每次运行后建议检查：

```text
runs/<run_id>/inputs/input_inventory.json
runs/<run_id>/knowledge/source_index.json
runs/<run_id>/knowledge/provenance_index.json
runs/<run_id>/plans/evidence_map.json
runs/<run_id>/plans/citation_plan.json
runs/<run_id>/plans/claim_support_matrix.json
runs/<run_id>/review/final_review.md
runs/<run_id>/review/review_report.json
runs/<run_id>/verify/verify_report.json
runs/<run_id>/final/final_report.md
runs/<run_id>/final/delivery_summary.md
runs/<run_id>/trace/hitl_decisions.jsonl
runs/<run_id>/learning/candidate_profile_update.yaml
runs/<run_id>/learning/candidate_skill_patch.md
runs/<run_id>/learning/promotion_report.md
```

重要审查路径：

```text
source_index -> provenance_index -> claim_support_matrix -> review_report -> verify_report -> final_report -> delivery_summary
```

## 预期 open items

非交互式 demo 中出现 open confirmations 是预期行为。即使 `final_report.md` 仍包含 `NEEDS_USER_CONFIRMATION`、open confirmations，或因为缺少 HITL confirmation 导致 verification status 为 `blocked`，demo 也可以正常完成。

candidate update proposed/inactive 也是预期行为：

```text
status: proposed
active: false
auto_applied: false
```

`final report` 是 review package，不是正式批准文件。

## 边界检查

对每个 demo：

- `sample` / `reference` materials 不能作为项目事实；
- `source_index.json` 不应包含 sample fact source entries；
- `citation_plan.json` 不应把 `sample` 当作 fact evidence；
- `plans/claim_support_matrix.json` 应让 unsupported critical claims 保持 pending 或 open；
- critical claims 必须由 `source` evidence 支持，否则保持 HITL open；
- candidate updates 不能自动 active；
- `final_report` 不是专业批准。

对 `test_report`，sample text 可能包含不安全示例结论。这些短语不能变成本项目的 test conclusion。

对 `fsr`，提供的 HARA summary 只能支持它明确包含的 trace，不能变成 blanket FSR approval；FSR 输出不得变成 TSC output（TSC 是独立下游文档类型）。

对 `TechnicalSafetyConcept`，提供的 FSR source 只能支持它明确包含的 FSR-xx 与 SG 链接，不能变成 blanket TSR approval；HARA summary 只能支持显式的 FTTI 与安全状态；sample/参考 TSC 不能支撑 TSR/机制/ASIL 事实。

## TSC 状态

TSC / Technical Safety Concept 由 document-type skill 层支持，通过 `task_type: TechnicalSafetyConcept` 加载。

仓库提供：

- `examples/technical_safety_concept_demo_fixture/`
- `skills/document-types/TechnicalSafetyConcept/SKILL.md` 与 13 个 `steps/step-*.md`

TSC 的下游 HSC / SSC（硬件/软件安全概念）仍 deferred。TSC 输出不得泄漏 HSC/SSC 终稿或详细实现。FSR negative eval fixtures 可以提到 TSC，用途是防止 FSR 阶段越权写入 TSC 内容。

## 预期输出状态

example runs 常见完成状态：

```text
completed_with_candidate_updates_proposed
```

非交互式 demo 中出现 open confirmations、pending critical claims，以及因缺少 HITL 导致的 blocked verification，是可以预期的。

## Cleanup 和 Git hygiene

Example outputs 是本地 runtime artifacts：

```text
runs/
```

不要提交它们。

如果不再需要本地 demo 输出，可以删除本地 runtime 目录：

```bash
rm -rf runs/
```

只在确认不需要本地 run artifacts 时执行。

## 常见问题

### 为什么 verify_report 是 blocked？

`blocked` 可能表示必需的 HITL confirmations 仍然 open。没有真实用户确认记录时，这是预期行为。

### final_report 是专业批准文件吗？

不是。它是包含 limitations 和 open confirmations 的可审查最终包，不是正式批准文件。

### sample 或 reference 能证明项目事实吗？

不能。`sample` / `reference` 不能作为 project-specific fact support。
