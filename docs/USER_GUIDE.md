# User Guide

这份指南说明当前插件协议如何组织专业文档任务，以及哪些能力由Python实际实现。

## 1. 两条执行路径

### Claude Code agent路径

```text
/ai-writing-plugin:write "Run the writing workflow with path/to/task.yaml"
```

该入口调度独立step/review worker。专业artifact由worker依据Skills生成；Python负责run scaffold和编排metadata。运行需要宿主环境提供Task/Agent能力，并在stage边界等待用户决定。

### Python工具路径

```bash
python -m ai_writing_plugin init-run --task path/to/task.yaml
```

这条路径只创建Phase 0的`input_refs.json`、`manifest.json`和`task_brief.json`。其他Python命令只构建或校验context、dispatch、progress、short result、review package、stage-review issue index/detail和stage-gate metadata。

当前没有一键专业内容CLI或resume lifecycle。

## 2. 准备任务

```text
my_doc_task/
  task.yaml
  inputs/
    source.md
    template.md
    checklist.md
    reference.md
    sample.md
```

```yaml
task_type: generic_document
task_title: Generate a project document
target_audience: Reviewers
output_format: markdown
strict_template: false
allow_inference: false
requires_human_confirmation:
  - final recommendation
inputs:
  - path: inputs/source.md
    role: source
  - path: inputs/template.md
    role: template
  - path: inputs/checklist.md
    role: checklist
  - path: inputs/reference.md
    role: reference
  - path: inputs/sample.md
    role: sample
```

路径相对于task文件所在目录解析。输入文件必须存在。当前Python parser支持简单mapping、scalar和list-of-scalar/object结构；复杂YAML特性不属于当前接口。

## 3. Material roles

| Role | Runtime用途 | Fact boundary |
| --- | --- | --- |
| `source` | 项目事实、需求、结果和约束 | 唯一可声明fact support的材料role |
| `template` | 目标结构、标题和表格形态 | 不证明事实 |
| `checklist` | review coverage和完成条件 | 不证明事实 |
| `reference` | 方法、背景和术语 | 不证明项目事实 |
| `sample` | 风格、颗粒度和输出形状 | 永远不是fact source |
| `expected_output_shape` | 期望形态 | 永远不是fact source |
| `other` | 未分类或受限输入 | 默认不能证明事实 |

`input_refs.json`只保存路径、hash、size、MIME type、role、read policy和fact-source permission，不复制输入正文。

## 4. Agent工作流

当前runtime协议使用以下顺序：

| Stage | Steps | 主要责任 |
| --- | --- | --- |
| `ingest` | input materials、material inventory、source index | 确认输入、导航和来源边界 |
| `outline` | template outline | 建立目标结构 |
| `evidence_planning` | research questions、evidence map | 规划证据、claim、citation和section task |
| `draft` | conservative draft | 不超出证据地起草 |
| `review` | review、verification | 独立审查与机械校验 |
| `finalize` | revision、final report | 受控修订和review-ready交付 |
| `learning` | run summary、candidate update | 中性总结和proposal |

每个step只写自己拥有的artifact，并通过StepResult返回path/hash。主agent不回放artifact正文。每个stage的review和gate是编排控制，不是专业批准。

## 5. Metadata控制链

```text
StepContextPackage
-> StepWorkerDispatch
-> independent worker
-> StepResult
-> ProgressLedger
-> ReviewContextPackage
-> one independent review worker for the stage
-> one ReviewResult per stage step
-> rebind each ProgressLedger entry
-> StageGateResult
```

这些metadata可以由Python构建或校验。Python校验shape、path、hash和状态，但不判断专业内容是否正确。

## 6. 文档类型

### Official L3产品/domain资产

- `hara`
- `technical_solution`
- `test_report`
- `fsr`

它们当前有维护的Skills和fixtures，但当前Python没有document-type registry、type-specific content rules或端到端内容测试。使用这些task type表示选择相应runtime guidance，不表示Python提供专业判断。

### Generic和external assets

`generic_document`有Skill、task和profile示例，但当前Python只把`task_type`记录进task brief，不加载profile或执行generic内容策略。

`custom_technical_note`是external profile demo。当前没有external profile loader，因此该YAML是设计资产，不是Python可执行配置。

### TSC

`TechnicalSafetyConcept`有非official Skill、step overlays和demo fixture。它没有Python rules、registry、end-to-end内容CLI或专门engine test。Official L3 TSC以及HSC/SSC仍deferred。

其他document-type目录同样只按资产层理解，不能仅凭目录存在宣称公共支持。

## 7. 证据和结论边界

Agent worker应维持以下tier：

```text
T0 = explicit HITL
T1 = project source
T2 = template/checklist
T3 = reference
T4 = sample
T5 = generated/unknown inference
```

Critical claim只有T0/T1支持时才可以关闭。否则保持pending、open或`NEEDS_USER_CONFIRMATION`。

特别注意：

- 找到文件不等于找到支持结论的证据；
- hash一致不等于内容真实；
- citation存在不等于citation充分支持claim；
- review或verification通过不等于专业批准；
- final report是review-ready package，不是合规、发布或安全批准。

## 8. 读取输出

Python `init-run`后先看：

```text
manifest.json
task_brief.json
input_refs.json
```

Agent step实际运行后，再按需看：

```text
orchestration/progress_ledger.json
orchestration/step_results/
orchestration/review_results/
orchestration/stage_gate_results/
```

只有对应worker确实完成后，才可能存在`knowledge/`、`plans/`、`draft/`、`review/`、`verify/`、`revised/`、`final/`、`trace/`或`learning/`。

详见[Reading Outputs](READING_OUTPUTS.md)。

## 9. Candidate material

Runtime Skills可能要求worker生成proposal形式的candidate material，但当前Python不生成、评估、应用或promote它。任何candidate都不能自动修改stable Skill或profile。

## 10. 失败行为

以下情况应显式停止：

- task或input文件不存在；
- task YAML结构不受支持；
- path不安全；
- metadata字段、stage-step pair或status无效；
- ref文件缺失或hash mismatch；
- Task/Agent worker不可用；
- short result校验失败；
- stage需要用户决定但尚未确认。

不要手工删除pending标记或伪造accepted gate来绕过失败。

## 11. 验证仓库能力

```bash
.venv/bin/python -m ai_writing_plugin --help
.venv/bin/python -m pytest -q -p no:cacheprovider
claude plugin validate .
```

这些检查证明当前代码和metadata协议状态，不证明专业文档内容质量。
