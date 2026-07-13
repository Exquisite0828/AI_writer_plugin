# Examples

`examples/`保存opt-in task fixtures。它们用于演示输入角色、domain guidance和runtime路由，不是默认上下文，也不是事实来源。

当前Python测试不会把这些fixtures跑成完整专业文档。Python可以对其task执行`init-run`；完整artifact需要Claude Code独立workers实际运行。

## 两种使用方式

### Claude Code agent协议

```text
/ai-writing-plugin:write "Run the writing workflow with examples/<fixture>/task.yaml"
```

该路径需要Task/Agent worker和用户stage gate。

### Python Phase 0检查

```bash
.venv/bin/python -m ai_writing_plugin init-run \
  --task examples/<fixture>/task.yaml
```

该路径只生成`input_refs.json`、`manifest.json`和`task_brief.json`。

## Official L3 domain fixtures

| Label | Fixture | 用途 |
| --- | --- | --- |
| `hara` | `examples/hara_demo_fixture/task.yaml` | HARA边界、source/sample分离和人工确认guidance |
| `technical_solution` | `examples/technical_solution_zh_demo_fixture/task.yaml` | 中文技术方案材料角色和领域guidance |
| `technical_solution` | `examples/technical_solution_demo_fixture/task.yaml` | 英文技术方案输入形态 |
| `test_report` | `examples/test_report_demo_fixture/task.yaml` | 测试结果、缺陷、覆盖和release claim边界 |
| `fsr` | `examples/fsr_demo_fixture/task.yaml` | FSR、SG/ASIL trace和TSC边界 |

这些标签有Skill/fixture资产，但当前没有Python document-type registry或端到端内容engine test。

示例：

```text
/ai-writing-plugin:write "Run the writing workflow with examples/technical_solution_zh_demo_fixture/task.yaml"
```

## Generic and external-profile fixtures

| Asset | Fixture | Current status |
| --- | --- | --- |
| `generic_document` | `examples/generic_document_demo_fixture/task.yaml` | generic Skill/task/profile设计资产；Python不执行generic内容策略 |
| `custom_technical_note` | `examples/custom_technical_note_profile_demo_fixture/task.yaml` | external profile demo；Python没有profile loader |

这些fixture可以验证Phase 0输入引用，但profile字段当前不会改变Python行为。

## Nonofficial skill-layer fixtures

仓库还包含多个非official document-type Skill/fixture资产。它们用于runtime guidance开发，不构成公共支持或兼容性承诺。

`examples/technical_safety_concept_demo_fixture/`对应`TechnicalSafetyConcept`非official prototype：Skill、step overlays和fixture存在；Python rules、registry、端到端内容CLI和专门engine test不存在。Official L3 TSC与HSC/SSC均deferred。

## Fixture边界

- fixture source只对该fixture声明的项目事实有效；
- sample只能指导结构和风格；
- reference只能支持方法和背景；
- expected output不是fact source；
- 不得把一个fixture的内容迁移成另一个真实项目的事实；
- 未运行的worker artifact不能被描述为已生成；
- metadata validation不是专业批准。

## 预期检查

执行`init-run`后可以检查：

```text
manifest.status = initialized
manifest.phase = phase_0
task_brief.task_type = task声明值
input_refs.constraints.sample_is_not_fact_source = true
input_refs.input_materials[*].path/role/sha256
```

若使用Claude Code agent路径，还应确认：

- 出现真实独立worker handoff；
- StepResult/ReviewResult通过validator；
- ProgressLedger绑定最终result hash；
- stage gate等待明确用户决定；
- unsupported claims没有被自动批准。

## 不应期待

不要从fixture或`init-run`推断以下能力已经由Python实现：

- 自动完整写作；
- 断点续写；
- external profile loading；
- document-type Python rules；
- eval或promotion；
- 专业结论批准。
