# AI 专业文档写作插件泛化下一阶段指导方案 v1.0

> 适用对象：新的 GPT 讨论窗口、Codex 执行窗口、后续技术协作者、GitHub self-service users、developers、maintainers。  
> 当前定位：在已完成 Generalization Phase 0–6 的基础上，继续推进插件从“支持少数内置文档类型”走向“几乎所有有模板、事实来源和审查标准的专业文档都可辅助写作”。

---

## 0. 当前基线

当前项目已经完成 Generalization Phase 0–6，从 HARA 单点 MVP 演进为：

```text
一个 Claude Code 专业文档写作插件
+ 一套通用 Python deterministic writing engine
+ 四个 official L3 document type rules
+ 四类 official L3 demo fixture
+ 四类 official L3 回归测试
+ Skill / guideline 层
+ 产品化文档
```

当前正式支持四类 official L3 文档：

```text
1. hara
   HARA 危害分析报告

2. technical_solution
   技术方案文档

3. test_report
   测试报告

4. fsr
   FSR 功能安全需求文档
```

`generic_document` 仍是 L1 通用模式；`custom_technical_note` 仍是外部 `document_profile.yaml` demo，不是 official L3。
N8 已实现 FSR 作为第四个 official L3 类型；TSC 仍 deferred。

当前准确定位：

```text
可扩展的多专业文档写作 Claude Code 插件技术预览版
```

不能描述为：

```text
任意专业文档自动生成平台
生产级自动合规批准工具
完全无人值守专业结论生成系统
FSR/TSC 自动批准或完整功能安全生命周期平台
```

这是后续所有方案的边界。

---

## 1. 后续总目标

后续目标不是继续无限新增内置文档类型，而是把插件从：

```text
支持少数内置 document type
```

推进到：

```text
支持一种通用专业文档写作方法：
template + source + checklist + evidence + review + HITL + trace + profile learning
```

最终产品形态应是：

```text
一个插件
+ 一套稳定通用 Python writing engine
+ 一个 generic_document 通用模式
+ 可外部配置的 document_profile
+ 少量高价值 Skill / guideline
+ source-of-truth / provenance 机制
+ eval / correction harvesting
+ 高价值官方 document type 增强包
```

内置 document type 不再是产品能力边界，而是高价值增强包。

---

## 2. 不可动摇的架构原则

### 2.1 一个插件，一套 pipeline

不同文档类型只能通过 rules / profile 注入差异，不能变成多套 pipeline。

禁止方向：

```text
hara_pipeline.py
fsr_pipeline.py
tsc_pipeline.py
prd_pipeline.py
```

正确方向：

```text
generic pipeline
+ hara rules
+ technical_solution rules
+ test_report rules
+ fsr rules
+ future tsc / external profiles
```

### 2.2 Python deterministic engine 是可信执行骨架

Python engine 继续负责：

```text
artifact 生成
schema 校验
source policy
citation / evidence trace
review
verify
final status
HITL trace
candidate update 状态控制
```

不能退化成 prompt-only 写作助手。

### 2.3 Markdown spec 是说明层，不是唯一机器规则

Markdown spec 可以做人类可读 / Claude Code 可读说明。

但真正供 engine 执行的规则必须结构化：

```text
Python dataclass
dict
YAML / JSON document_profile
Pydantic model
```

推荐关系：

```text
Markdown Spec = 人类可读 / Claude Code 可读 / 领域专家可编辑
Document Profile / Rules = 机器可读 / 测试可验证 / engine 可执行
```

### 2.4 Skill.md 是 guideline，不是执行层

Skill.md 可以说明：

```text
流程
边界
调用方式
参考文档
gotchas
review focus
```

Skill.md 不能替代：

```text
schema 校验
artifact 生成
source_index
evidence trace
review / verify
HITL trace
candidate update 状态控制
```

### 2.5 全局安全边界不能动

必须持续保护：

```text
1. sample 永远不是事实来源。
2. reference 不能证明项目事实。
3. critical claim 必须有 source 或 HITL。
4. final report 不是专业批准文件。
5. candidate update 不能自动覆盖 stable skill。
6. 不为每类文档复制一套 pipeline。
7. 不一上来做大 RAG / LangChain / agent framework。
```

---

## 3. 只吸收外部思路中价值最高的部分

### 3.1 吸收：Markdown Spec 作为上游说明层

保留并强化：

```text
docs/document_types/<task_type>_SPEC.md
```

它用于让人类、领域专家、AI coding 工具理解某类文档。

每个 Markdown Spec 应包含：

```text
1. 文档目标
2. 目标读者
3. 典型输入材料
4. source / template / checklist / sample / reference 角色说明
5. 默认章节
6. required sections
7. critical claims
8. requires_human_confirmation
9. forbidden final claims
10. review focus
11. verification focus
12. sample / reference policy
13. final status policy
14. 常见错误 / gotchas
15. 推荐 demo fixture 结构
```

它不是运行时唯一依据。它的作用是生成或维护结构化 profile / rules / tests / Skill。

### 3.2 吸收：两类 Skill，而不是每一步都拆成 Skill

Skill 最终分两类即可：

```text
writing-process skill
document-domain skill
```

`writing-process skill` 说明通用写作流程：

```text
clarify
ingest
source index
template outline
evidence map
citation plan
draft
review
verify
finalize
trace
learning
```

`document-domain skill` 说明具体领域边界：

```text
HARA
FSR
TSC
test_report
technical_solution
customer_domain
generic_document
```

暂不建议把每一步都拆成独立 skill。只有当 Claude Code 确实需要更细粒度上下文时，再拆。

### 3.3 吸收：高质量 reference docs / gotchas

可以把客户或领域的最佳实践、guideline、checklist、常见错误做成 LLM 友好的 reference docs。

建议结构：

```text
docs/domain_references/<domain>/
  terminology.md
  gotchas.md
  review_guideline.md
  evidence_policy.md
  common_patterns.md
```

但这些 reference docs 仍然只能支持方法论、流程和审查标准，不能证明项目事实。

### 3.4 吸收：provenance footer / source support

每个章节或关键 claim 应带 source support：

```text
Claim status: supported / weak / unsupported / needs confirmation
Source tier: project source / checklist / reference / sample-style-only / HITL
Source id: SRC-xxx
Evidence id: EVD-xxx
Human confirmation: HITL-xxx / pending
Profile version: <profile>@<version>
```

这是提升客户信任的关键能力。

### 3.5 吸收：eval + correction harvesting

不要做：

```text
历史文档 RAG 直接写新文档
```

要做：

```text
历史文档 / 用户纠错
→ candidate profile
→ review rule
→ eval case
→ human approval
→ active profile
```

---

## 4. 明确不吸收的内容

以下内容不进入最终方案：

```text
1. 不做“输入 Markdown spec 自动生成新插件平台”。
2. 不让 Skill.md 变成执行层。
3. 不为每类文档生成一套新 pipeline。
4. 不一上来引入 RAG / LangChain / agent framework / 多 agent 平台。
5. 不把历史样例文档直接当事实来源。
6. 不为了追求“泛化”降低 HARA、FSR、TSC、测试报告等高风险文档的专业判断边界。
```

---

## 5. 目标架构

最终应形成八层结构：

```text
1. Claude Code Command Layer
   /ai-writing-plugin:write

2. Generic Python Engine
   run / ingest / outline / evidence / draft / review / verify / final / trace / learning

3. Artifact Contract Layer
   所有文档类型共享同一套 artifact tree

4. Document Profile Layer
   内置 rules + 外部 YAML/JSON profile + generic_document 临时 profile

5. Markdown Spec Layer
   人类可读、领域专家可编辑、AI coding 可理解的上游说明

6. Skill / Guideline Layer
   writing-process skill + document-domain skill

7. Eval / Fixture Layer
   full run、sample policy、critical claim、final status、leakage、candidate update 测试

8. Learning / Promotion Layer
   correction → candidate patch → eval → human approval → active profile
```

其中：

```text
2、3、4、7 是可信执行与验证核心。
5、6 是可理解、可维护、可协作层。
```

---

## 6. 文档支持等级

以后不要只用“是否内置支持”衡量全部能力。建议定义四档。

```text
L0：未知文档
没有 profile，不能承诺效果。

L1：Generic Document Mode
用户提供 source / template / checklist / sample / reference，插件基于通用流程辅助写作。
目标：几乎所有有模板和事实来源的专业文档都能跑。

L2：Customer / Project Document Profile
针对客户常用文档沉淀 profile、术语、模板、checklist、critical claims、forbidden claims。
目标：客户内部可复用。

L3：Official Built-in Document Type
内置 rules、fixture、tests、Skill、回归测试。
目标：高价值、高风险、高频文档。
```

当前：

```text
hara = L3
technical_solution = L3
test_report = L3
fsr = L3
```

未来：

```text
TSC = 适合 L3
大多数客户内部文档 = 先做 L1 / L2
```

---

## 7. 后续推进路线

### Phase N0：冻结当前泛化基线

目标：确认 Phase 0–6 真实闭环，避免在不确定基线上继续开发。

执行：

```bash
git status --short
git log --oneline -10
.venv/bin/python -m pytest -q
claude plugin validate .
.venv/bin/python -m ai_writing_plugin write-run --task examples/hara_demo_fixture/task.yaml
.venv/bin/python -m ai_writing_plugin write-run --task examples/technical_solution_demo_fixture/task.yaml
.venv/bin/python -m ai_writing_plugin write-run --task examples/test_report_demo_fixture/task.yaml
```

验收：

```text
1. N0 当时的 hara / technical_solution / test_report demo 完整跑通；Post-N8 当前还应覆盖 fsr；
2. official L3 文档共享同一 artifact tree；
3. sample/reference 未被当事实来源；
4. critical claims 保留确认项；
5. candidate update proposed/inactive；
6. final report 不是 approval；
7. runs/ 不进入 git。
```

这一步必须先做。

---

### Phase N1：实现 `generic_document` 通用模式

目标：没有内置 document type 时，也能基于 template/checklist/source 跑完整专业文档辅助写作流程。

新增：

```text
ai_writing_plugin/document_types/generic_document.py
examples/generic_document_demo_fixture/
tests/test_generic_document_demo.py
```

能力：

```text
1. 从 task.yaml 读取 display_name；
2. 从 template 提取章节；
3. 从 checklist 推断 review_focus；
4. 从用户声明或默认规则生成 critical_claims；
5. 默认 final_status = ready_for_human_review；
6. 所有无证据关键判断标记 NEEDS_USER_CONFIRMATION；
7. sample/reference policy 与现有文档类型一致。
```

验收：

```text
1. generic_document demo 完整跑通；
2. 输出完整 artifact tree；
3. sample 不进入 fact evidence；
4. reference 不证明项目事实；
5. unsupported critical claims 进入 unresolved/review/verify/final；
6. candidate update proposed/inactive；
7. hara/technical_solution/test_report 不回归。
```

这是从“支持少数文档类型”走向“几乎所有专业文档可辅助”的核心第一步。

---

### Phase N2：引入外部 `document_profile.yaml`

目标：把新增文档类型从“写 Python rules”推进到“结构化配置接入”。

新增：

```text
schemas/document_profile.schema.json 或 Pydantic model
profiles/document_types/
  generic_document.yaml
  customer_demo/
    custom_technical_note.yaml
```

profile 字段应基本对齐现有 DocumentTypeRules：

```yaml
task_type:
display_name:
description:
default_sections:
required_sections:
optional_sections:
critical_claims:
requires_human_confirmation:
forbidden_final_claims:
confirmation_marker:
fact_source_roles:
non_fact_source_roles:
reference_policy:
sample_policy:
default_final_status:
allowed_final_statuses:
review_focus:
verification_focus:
candidate_learning_policy:
terminology:
output_labels:
```

验收：

```text
1. 外部 profile 可加载；
2. profile 有 schema 校验；
3. profile 非法时写入 failures.md / verify_report.json；
4. run artifact 记录 profile_id / profile_version；
5. 内置 rules 仍可用；
6. 现有 official L3 文档不回归。
```

注意：此阶段只是外部配置化，不是让 Markdown 自然语言直接驱动 engine。

---

### Phase N3：建立 Markdown Spec → Document Profile 的生成/维护流程

目标：吸收自然语言 spec 的优势，但不让它替代结构化规则。

新增：

```text
docs/DOCUMENT_PROFILE_SPEC_TEMPLATE.md
docs/document_types/generic_document_SPEC.md
scripts/profile_from_spec.py 或 ai_writing_plugin profile-from-spec 命令
tests/test_profile_from_spec.py
```

流程：

```text
Markdown Spec
→ 生成 candidate document_profile.yaml
→ schema 校验
→ 生成 fixture skeleton
→ 生成 eval skeleton
→ 人工审查
→ 才可用于正式 run
```

验收：

```text
1. Spec 中的信息可映射到 profile 字段；
2. 生成结果必须是 candidate；
3. 不自动覆盖 active profile；
4. 不自动生成新 pipeline；
5. 不修改 stable skills；
6. 缺失 critical_claims / sample_policy / final_status_policy 时阻塞 promote。
```

---

### Phase N4：强化 Source-of-Truth 与 Provenance

目标：让客户能看懂每个结论的可信度。

新增或增强 artifact 字段：

```text
source_tier
claim_status
evidence_status
human_confirmation_status
profile_version
source_freshness / source_date 可选
owner / confirmer 可选
```

建议 source tier：

```text
T0：HITL / human confirmation
T1：project source
T2：template / checklist
T3：reference methodology
T4：sample style only
T5：AI summary / inference
```

规则：

```text
T1 可证明项目事实；
T2 约束结构和审查；
T3 只能支持方法论；
T4 只能支持风格和结构；
T5 不能支撑 critical claim。
```

验收：

```text
1. final_report 增加 provenance summary；
2. draft/revised/final 中关键 claim 有 source support；
3. sample style only 不得被显示为 fact support；
4. verify 检查 critical claim 的 source_tier；
5. final delivery 明确 open confirmations。
```

---

### Phase N5：重整 Skill 层，只保留高价值 Skill

目标：形成清晰的两类 Skill，不把 Skill 做成碎片化执行器。

建议结构：

```text
skills/
  writing-core/
    SKILL.md

  document-types/
    hara/SKILL.md
    technical_solution/SKILL.md
    test_report/SKILL.md
    generic_document/SKILL.md
    fsr/SKILL.md        # 当前 N8 已完成
    tsc/SKILL.md        # deferred，需未来单独 active phase
```

`writing-core/SKILL.md` 包含：

```text
1. 插件目标；
2. 通用 workflow；
3. artifact contract；
4. source/template/checklist/sample/reference 角色；
5. sample 不是事实来源；
6. reference 不能证明项目事实；
7. critical claim 规则；
8. HITL 规则；
9. provenance 规则；
10. candidate update 不自动激活；
11. Python entrypoints；
12. 常见错误处理。
```

`document-domain/SKILL.md` 包含：

```text
1. 文档类型目标；
2. 典型输入；
3. 默认章节；
4. critical claims；
5. forbidden final claims；
6. 人工确认项；
7. sample/reference policy；
8. review focus；
9. gotchas；
10. final report 边界。
```

验收：

```text
1. Skill.md 指向 Python command 和 artifact；
2. Skill.md 不承担核心执行；
3. 没有大量空壳 step-level skill；
4. Claude Code 使用说明更清楚；
5. pytest 和 plugin validate 通过。
```

---

### Phase N6：建立用户自定义 profile Eval Harness

目标：泛化效果由 eval 证明，不靠肉眼判断。

新增：

```text
tests/evals/
  generic_document/
  external_profile/
  fsr/
  tsc/

ai_writing_plugin/eval/
  runner.py
  metrics.py
  report.py
```

最小 eval 类别：

```text
1. material classification eval
2. source tier eval
3. template extraction eval
4. evidence mapping eval
5. sample misuse eval
6. reference misuse eval
7. critical claim eval
8. forbidden final claim eval
9. final status eval
10. candidate update inactive eval
11. cross-document leakage eval
```

验收：

```text
1. 每个 L3 document type 有 eval set；
2. 每个 external profile 至少有 smoke eval；
3. profile 变更必须跑相关 eval；
4. eval_report 写入 run 或独立 reports/；
5. 不通过 eval 的 profile 不能 promote。
```

---

### Phase N7：Correction Harvesting 与 Candidate Promotion

目标：让用户显式纠错变成系统进步的来源，但仍然人工可控。

新增：

```text
trace/correction_events.jsonl
learning/candidate_profile_patch.yaml
learning/candidate_eval_case.json
learning/profile_promotion_report.md
```

流程：

```text
用户纠错
→ correction_events.jsonl
→ candidate_profile_patch.yaml
→ candidate_eval_case.json
→ 跑 eval
→ 人工 approve
→ profile version bump
→ active profile
→ 支持 rollback
```

验收：

```text
1. 用户纠错不会直接修改 stable profile；
2. candidate patch 默认 inactive；
3. promotion 必须有 eval result；
4. rollback metadata 存在；
5. candidate skill patch 不自动覆盖 stable skill。
```

这一步把原有 candidate update 机制升级为用户自定义 profile 的持续维护机制。

---

### Phase N8：高价值 L3 文档类型增强：FSR 已完成，TSC deferred

目标：在 generic_document + profile + eval 基础上，再做高价值官方支持类型。

建议顺序：

```text
1. fsr
2. tsc
3. safety_case 或 verification_plan
```

不要写死 FSR/TSC pipeline。FSR 已按标准流程完成；TSC 仍需未来单独 active phase，且必须继续沿用一套 pipeline：

```text
docs/document_types/fsr_SPEC.md
profiles/document_types/fsr.yaml 或 ai_writing_plugin/document_types/fsr.py
examples/fsr_demo_fixture/
tests/test_fsr_demo.py
skills/document-types/fsr/SKILL.md
evals/fsr/
```

FSR 与未来 TSC 的核心价值是打通功能安全链路：

```text
Item Definition
→ HARA
→ Safety Goals
→ FSR
→ TSC
→ Verification / Test Report
```

验收：

```text
1. HARA 不回归；
2. FSR critical claims 被控制；
3. TSC 保持 deferred，不能被描述为已实现；
4. safety requirement 不被编造；未来 TSC 的 technical safety requirement 也必须 source/HITL 控制；
5. sample/reference policy 不变；
6. final status 不伪装成 approval。
```

---

## 8. 后续 Codex 执行总约束

每个后续 Phase Prompt 都必须包含：

```text
1. 只做当前 Phase，不提前做后续 Phase；
2. 不新增多套 pipeline；
3. 不把 Markdown spec 当运行时唯一规则；
4. 不让 Skill.md 替代 Python engine；
5. 不自动生成插件平台；
6. 不引入 LangChain / RAG / agent framework；
7. 不放宽 sample/reference policy；
8. 不自动确认 critical claims；
9. 不自动激活 candidate update；
10. 不改变 artifact tree，除非 Phase 明确要求；
11. 所有新增行为必须有测试；
12. HARA / technical_solution / test_report / fsr 必须回归；
13. pytest 必须通过；
14. claude plugin validate 必须通过。
```

---

## 9. 最终技术路线图

可以把路线压缩成一句话：

```text
当前 L3 四类文档基线（hara / technical_solution / test_report / fsr）
→ generic_document 通用模式
→ 外部 document_profile
→ Markdown Spec 生成 profile
→ provenance / source tier
→ eval harness
→ correction harvesting
→ external profile
→ TSC 等后续高价值 L3 类型（deferred）
```

更短的产品表达：

```text
不是“内置所有文档类型”；
而是“任意有 source/template/checklist 的专业文档，都能先用 generic_document 辅助；
高频用户文档沉淀为 external profile；
高风险高价值文档沉淀为官方 document type”。
```

---

## 10. 最终判断

这份方案吸收了 Markdown spec / Skill 思路中真正有价值的部分：

```text
1. Markdown spec 更适合人类和领域专家编辑；
2. Skill 适合承载流程和领域 guideline；
3. reference docs / gotchas 能增强泛化质量；
4. provenance 能提升用户信任；
5. eval 和 correction harvesting 能让系统持续进化。
```

但明确拒绝这些会污染原方案的做法：

```text
1. 让 AI coding 工具成为运行时泛化核心；
2. 每个文档类型自动生成一套代码；
3. Skill.md 替代 Python engine；
4. Markdown spec 直接替代结构化 rules；
5. 历史样例 RAG 直接生成新项目事实；
6. 为追求泛化牺牲 evidence / HITL / critical claim 边界。
```

最终指导原则：

```text
自然语言 spec 提供可编辑性；
结构化 profile 提供可执行性；
Python engine 提供稳定性；
Skill.md 提供流程指导；
eval/tests 提供可信验证；
HITL/provenance 提供专业边界。
```

这就是后续从“支持几类文档”走向“几乎所有专业文档可辅助写作”的主路线。
