# AI 专业文档写作 Claude Code 插件泛化方案设计文档

版本：v1.0  
状态：维护者架构文档 / Generalization Phase 0-6 已完成后的当前设计依据  
适用对象：中文开发者、维护者、后续 Codex 执行窗口  
适用阶段：HARA MVP 之后的泛化开发与后续 document type 扩展  
目标仓库路径：`docs/maintainers/ARCHITECTURE.md`  

---

## 0. 文档定位

本文档用于指导 **AI 专业文档写作 Claude Code 插件** 从 HARA MVP 泛化到更多专业文档类型。

它不是早期产品 PRD，也不是某一个 Phase 的 Codex 执行提示词，而是泛化工作的总设计依据。后续新增 active Phase 的执行文档、验收文档、Codex Prompt 都应以本文档为上游约束。

当前文档关系如下：

```text
早期 PRD / HARA 交接文档 / 本轮方案讨论
        ↓
docs/maintainers/ARCHITECTURE.md
        ↓
未来 active phase/spec 文档（如有）
        ↓
Codex 分阶段实施
```

如本文档与早期 PRD 或历史交接材料冲突，以当前泛化目标为准；如本文档与当前代码状态描述冲突，应先核查仓库当前实现，再修订本文档或 active phase 文档。

当前实现状态：

```text
Generalization Phase 0-6 已完成。
Phase N8 已新增 fsr 作为第四个 official L3 built-in document type。
当前 official L3 built-ins 为 hara、technical_solution、test_report、fsr。
generic_document 仍是通用模式；custom_technical_note 仍是外部 document_profile demo，不是 official L3。
TSC 仍 deferred。
历史 phase / process / handoff 材料不再作为 tracked public docs 保留；如本地存在 archive 目录，只作历史参考，不是当前 active phase docs。
```

---

## 1. 当前项目背景

本项目是一个运行在 Claude Code 中的 **AI 专业文档写作插件**。它不是普通聊天式写作助手，也不是一次性自由生成文档的工具，而是面向有固定模板、固定输入材料、固定 checklist、固定审查标准的专业文档生产流程。

首个 MVP 场景是 **HARA 危害分析报告**。HARA MVP 已经完成 Phase 0–8，并已通过实际插件流程跑通，当前已被认可为技术人员内测版 / mentor technical preview。

当前已验证的核心闭环包括：

```text
/write 或 /ai-writing-plugin:write
→ 创建 runs/<run_id>/
→ 读取并分类输入材料
→ 区分 source/template/checklist/sample/reference
→ 构建 source_index
→ 解析模板与大纲
→ 生成 research_questions / evidence_map
→ 生成 citation_plan / section_tasks / writing_plan
→ 生成 conservative draft
→ 自动 review
→ 脚本化 verify
→ revision / final delivery
→ HITL trace
→ learning / candidate_profile_update / candidate_skill_patch
```

当前 HARA MVP 的价值不在于已经能生产正式合规批准文档，而在于它验证了以下产品机制：

```text
1. Claude Code 插件入口可用；
2. 专业文档写作流程可以被拆成可审查阶段；
3. 每个阶段可以生成可追踪 artifact；
4. 证据不足可以被显式标记；
5. 关键专业判断可以通过 HITL 控制；
6. 自动 review 和 verify 可以阻断错误交付；
7. 候选学习可以生成，但不会自动覆盖 stable skill。
```

泛化工作的目标是把这个已经验证过的闭环，从 HARA 扩展到更多专业文档类型。

---

## 2. 泛化目标

本轮泛化的目标是：

```text
将当前 hardcoded HARA pipeline
演进为
一个通用专业文档写作 pipeline + 多个 document_type rules。
```

更具体地说，目标架构应是：

```text
一个 Claude Code 写作插件
+ 一套通用 Python deterministic engine
+ 多个 document_type rules
+ 每个文档类型独立的 fixture / checklist / guideline / tests
+ 少量 Skill.md 辅助 Claude Code 理解流程和边界
```

不是：

```text
每个文档类型重新生成一个插件；
每个文档类型复制一套 pipeline；
让 AI coding 工具自动生成插件平台；
把核心执行逻辑全部放进 prompt；
让 LLM 自由写最终专业结论。
```

泛化后的插件应满足：

```text
1. 用户仍然通过统一入口启动写作任务；
2. 不同文档类型共享同一套核心 workflow；
3. 文档类型差异由 document_type rules 表达；
4. HARA 被保留为一个 document_type，而不是被删除；
5. 新文档类型通过 rules + fixture + tests 接入；
6. sample 永远不能成为事实来源；
7. critical claim 永远需要 evidence 或 HITL；
8. final report 必须保留未确认项和限制说明；
9. candidate update 永远不能自动覆盖 stable skill。
```

---

## 3. 明确非目标

本轮泛化不做以下事项。

### 3.1 不做自动生成插件平台

本项目要泛化的是 **同一个 Claude Code 写作插件对多类文档的支持能力**，不是建设一个“输入 Markdown spec 后自动生成新插件”的平台。

AI coding 工具可以辅助实现新 rules、fixture、tests，但不能成为产品运行时的核心泛化机制。

### 3.2 不做每个文档类型一套代码

不能变成：

```text
hara_pipeline.py
technical_solution_pipeline.py
prd_pipeline.py
test_report_pipeline.py
```

正确方向是：

```text
generic pipeline
+ hara rules
+ technical_solution rules
+ test_report rules
```

### 3.3 不引入大而全 workflow engine

当前阶段不引入复杂 workflow engine、LangChain、RAG 平台、多 agent 框架、后台异步任务系统或复杂知识图谱。

当前优先级是：

```text
可运行
可审查
可测试
可回归
边界稳定
```

不是：

```text
框架宏大
自动规划复杂
智能程度最高
```

### 3.4 不让 Skill.md 替代 Python engine

Skill.md 可以提供自然语言说明、阶段目标、guideline、checklist、调用说明，但不能替代：

```text
schema 校验
artifact 生成
source_index 构建
evidence trace
review/verify 规则
HITL trace
candidate update 状态控制
```

这些仍然必须由 Python deterministic engine 和测试保障。

### 3.5 不弱化 HARA 安全边界

HARA 中以下内容仍不能由 AI 自动最终确认：

```text
hazard identification
hazardous event
severity rating
exposure rating
controllability rating
ASIL / risk level
safety goal
final acceptability conclusion
```

泛化不能以删除这些边界为代价。正确做法是把它们作为 HARA document_type rules 的 critical claims。

### 3.6 不让 sample 成为事实来源

sample 文档在任何文档类型中都只能用于：

```text
结构参考
表达风格参考
表格组织参考
质量粒度参考
```

不能用于：

```text
事实迁移
参数迁移
结论迁移
风险项迁移
评级迁移
项目背景迁移
```

### 3.7 不自动覆盖 stable skill

一次 run 结束后可以生成：

```text
candidate_profile_update.yaml
candidate_skill_patch.md
promotion_report.md
```

但默认必须保持 proposed / inactive。任何候选更新不得自动覆盖 stable skill。

---

## 4. 核心术语

### 4.1 Generic Engine

通用执行引擎，主要由 Python 模块实现。它负责稳定执行写作闭环，包括 run 创建、artifact 读写、输入材料处理、证据映射、起草、review、verify、finalize、trace、learning 等。

Generic engine 不应直接写死 HARA、ASIL、S/E/C、技术方案、PRD 等业务语义。

### 4.2 Document Type

一种专业文档类型，例如：

```text
hara
technical_solution
test_report
prd
fsr
tsc
```

每个 document type 有自己的默认章节、关键 claim、人工确认规则、review 规则、final status policy、fixture 和 guideline。

### 4.3 Document Type Rules

机器可读的文档类型规则。它描述某类文档和通用 engine 的接口。

例如：

```text
task_type
display_name
default_sections
critical_claims
requires_human_confirmation
forbidden_final_claims
final_status_default
review_rules
verify_rules
```

### 4.4 Skill.md

给 Claude Code / AI coding 工具看的自然语言指导文档。它可以说明某个 workflow 阶段或 document type 的目标、边界、调用命令、参考材料和常见错误。

Skill.md 是指导层，不是核心执行层。

### 4.5 Fixture

用于测试和 demo 的最小输入包。每个正式支持的 document type 都应至少有一个 demo fixture。

典型结构：

```text
examples/<doc_type>_demo_fixture/
  task.yaml
  inputs/
    source.md
    template.md
    checklist.md
    reference.md
    sample.md
```

### 4.6 Critical Claim

对最终文档质量、专业判断或交付风险有关键影响的 claim。critical claim 必须有正式 source 支撑，或绑定明确 HITL 决策；否则必须标记为 `NEEDS_USER_CONFIRMATION` 或类似状态。

不同文档类型的 critical claim 不同。

例如 HARA：

```text
ASIL
S/E/C rating
safety goal
hazardous event
```

例如技术方案：

```text
architecture decision
performance target
security boundary
cost estimate
rollout risk acceptance
```

---

## 5. 总体架构设计

泛化后的系统建议分为六层。

### 5.1 Claude Code Command 层

用户入口保持统一：

```text
/ai-writing-plugin:write "基于 examples/<fixture>/task.yaml 生成某类文档"
```

未来可继续优化为：

```text
/write "生成技术方案"
```

但不建议为每个文档类型新增独立命令，例如：

```text
/write-hara
/write-tech-solution
/write-test-report
```

命令层只负责解释用户意图、定位 task.yaml、调用 Python engine，不承载文档类型业务逻辑。

### 5.2 Generic Workflow Engine 层

继续保留当前 Python deterministic backbone。通用 workflow 包括：

```text
init run
→ ingest
→ source index
→ template outline
→ research questions
→ evidence map
→ citation plan
→ section tasks
→ draft
→ review
→ verify
→ revise
→ finalize
→ trace
→ learning
```

该层应只关心通用专业文档写作概念：

```text
input material
fact source
template
checklist
sample
reference
section
claim
evidence
citation
review item
verification check
HITL decision
final status
candidate update
```

不应直接写死具体文档语义。

### 5.3 Document Type Registry / Rules 层

所有文档类型通过 registry 注册。

建议第一版使用 Python dataclass / dict，降低引入配置加载器的复杂度。后续再考虑 YAML。

建议结构：

```text
ai_writing_plugin/document_types/
  __init__.py
  base.py
  hara.py
  technical_solution.py
```

`base.py` 定义规则模型。`hara.py` 定义 HARA 规则。`technical_solution.py` 在 Phase 3 新增。

### 5.4 Artifact Contract / Schema 层

artifact contract 应尽量稳定，不因文档类型变化而改变目录结构。

所有文档类型都应继续输出：

```text
manifest.json
task_brief.json
inputs/input_inventory.json
knowledge/source_index.json
knowledge/knowledge_gaps.md
plans/template_structure.json
plans/outline_l1.md
plans/research_questions.json
plans/evidence_map.json
plans/unresolved_questions.md
plans/citation_plan.json
plans/outline_final.md
plans/section_tasks.json
plans/writing_plan.md
draft/full_draft.md
review/review_report.json
review/final_review.md
verify/verify_report.json
verify/failures.md
revision_plan.json
revised/full_draft.md
revised/change_log.md
final/final_report.md
final/delivery_summary.md
trace/session_trace.jsonl
trace/hitl_decisions.jsonl
learning/run_summary.md
learning/reusable_patterns.md
learning/candidate_profile_update.yaml
learning/candidate_skill_patch.md
learning/promotion_report.md
```

允许在 artifact 内容里增加字段，例如：

```text
task_type
document_type_display_name
critical_claim_categories
final_status_policy
source_policy
```

但不要为不同文档类型创建完全不同 artifact 契约。

### 5.5 Skill / Guideline 层

Skill / guideline 层用于增强 Claude Code 使用体验和后续人类协作理解。

建议最小结构：

```text
skills/writing-core/SKILL.md
skills/document-types/hara/SKILL.md
skills/document-types/technical_solution/SKILL.md
```

暂不建议一开始拆成大量空壳：

```text
skills/writing-core/ingest/SKILL.md
skills/writing-core/evidence/SKILL.md
skills/writing-core/review/SKILL.md
...
```

只有当 Claude Code 使用中确实需要更细粒度上下文时，再逐步拆分。

### 5.6 Fixture / Tests 层

每支持一个 document type，必须配 fixture 和测试。泛化是否成功由测试证明，不由肉眼判断。

至少需要以下测试类别：

```text
1. full demo run test
2. sample_not_fact_source test
3. critical_claim_requires_evidence_or_hitl test
4. no_cross_document_type_leakage test
5. final_status_policy test
6. candidate_update_inactive test
7. HARA regression test
```

---

## 6. 核心设计决策

### 6.1 一个插件，而不是多个插件

本轮泛化后，仍然只有一个 AI writing plugin。不同文档类型通过 `task_type` 和 rules 分发。

### 6.2 一个 pipeline，而不是多套 pipeline

HARA、技术方案、测试报告等文档共享同一套 pipeline。差异通过 rules 注入。

### 6.3 HARA 不是被删除，而是被迁移

HARA 仍然是重要文档类型。泛化第一步不是删除 HARA 词，而是把 HARA 规则集中到 `document_types/hara.py`。

### 6.4 Markdown spec 可用于说明，但不能作为唯一机器规则

可以为每个文档类型维护 Markdown spec，用于描述文档意图、输入类型、章节结构、关键 claim、review 规则和人工确认规则。

但真正供 engine 执行的规则必须结构化，例如 Python dataclass / dict / YAML。

推荐：

```text
Markdown Spec = 人类可读 / Claude Code 可读
DocumentTypeRules = 机器可读 / 测试可验证
```

### 6.5 Python deterministic engine 继续作为可信执行骨架

泛化不能把系统退化成 prompt-only 写作助手。Python 继续负责：

```text
artifact 创建
schema 校验
source/sample/reference policy
citation id 追踪
review item 结构化
verify check
final status
HITL trace
candidate update 状态
```

### 6.6 Critical claim 机制从 HARA 泛化

HARA 中的 ASIL、S/E/C、安全目标，本质是某类专业文档里的 critical claims。

泛化后，每个 document type 都需要定义自己的 critical claims。

### 6.7 Final report 不是正式批准文件

`final/final_report.md` 是插件输出的最终文档包 artifact，不等于专业审批通过文件。

对不同文档类型，应使用类似状态：

```text
ready_for_human_review
finalized_with_open_items
blocked_pending_confirmation
```

禁止无条件输出：

```text
approved
validated
compliant
risk accepted
production ready
```

除非有明确 source 或 HITL 决策支持，并且 document type rules 允许。

---

## 7. DocumentTypeRules v0.1 设计

### 7.1 推荐字段

第一版规则模型建议如下：

```python
@dataclass(frozen=True)
class DocumentTypeRules:
    task_type: str
    display_name: str
    description: str

    default_sections: list[str]
    required_sections: list[str]
    optional_sections: list[str]

    critical_claims: list[str]
    requires_human_confirmation: list[str]
    forbidden_final_claims: list[str]
    confirmation_marker: str

    fact_source_roles: list[str]
    non_fact_source_roles: list[str]
    reference_policy: str
    sample_policy: str

    default_final_status: str
    allowed_final_statuses: list[str]

    review_focus: list[str]
    verification_focus: list[str]
    candidate_learning_policy: str

    terminology: dict[str, str]
    output_labels: dict[str, str]
```

### 7.2 字段语义

`task_type`：机器识别名，例如 `hara`、`technical_solution`。  
`display_name`：用户可见名称，例如 `HARA 危害分析报告`、`技术方案文档`。  
`default_sections`：模板缺失时的 fallback 章节。  
`required_sections`：必须检查的章节类别。  
`critical_claims`：该文档类型中必须有证据或 HITL 的关键 claim。  
`requires_human_confirmation`：即使有候选推理，也默认要求人工确认的判断。  
`forbidden_final_claims`：没有证据或确认时禁止出现在 final 中的确定性表达。  
`confirmation_marker`：默认 `NEEDS_USER_CONFIRMATION`。  
`fact_source_roles`：通常为 `source`。  
`non_fact_source_roles`：通常包括 `sample`、`template`、部分 `reference`。  
`reference_policy`：说明 reference 能否作为方法论依据，不能作为项目事实。  
`sample_policy`：说明 sample 只能作为结构/风格参考。  
`default_final_status`：默认交付状态。  
`allowed_final_statuses`：允许输出的 final 状态枚举。  
`review_focus`：自动 review 的重点。  
`verification_focus`：脚本化 verify 的重点。  
`candidate_learning_policy`：候选学习是否允许、默认状态、是否可激活。  
`terminology`：文档类型术语表。  
`output_labels`：final report / review report 中的文案标签。

### 7.3 HARA rules 示例

```python
HARA_RULES = DocumentTypeRules(
    task_type="hara",
    display_name="HARA 危害分析报告",
    description="面向功能安全分析的 HARA 报告写作任务。",
    default_sections=[
        "文档目的和范围",
        "输入材料和假设",
        "Item definition 摘要",
        "运行场景和模式",
        "危害识别",
        "危险事件分析",
        "S/E/C 评级表",
        "ASIL 候选",
        "安全目标候选",
        "开放问题和必需确认",
        "审查摘要",
    ],
    required_sections=[
        "scope",
        "input materials",
        "item definition",
        "hazard identification",
        "hazardous event analysis",
        "rating table",
        "open issues",
    ],
    critical_claims=[
        "hazard identification",
        "hazardous event",
        "severity rating",
        "exposure rating",
        "controllability rating",
        "ASIL or risk level",
        "safety goal",
        "final acceptability conclusion",
    ],
    requires_human_confirmation=[
        "hazard identification",
        "hazardous event",
        "severity rating",
        "exposure rating",
        "controllability rating",
        "ASIL or risk level",
        "safety goal",
        "final acceptability conclusion",
    ],
    forbidden_final_claims=[
        "final ASIL is approved",
        "risk is acceptable",
        "safety goal is approved",
    ],
    confirmation_marker="NEEDS_USER_CONFIRMATION",
    fact_source_roles=["source"],
    non_fact_source_roles=["sample", "template"],
    reference_policy="Reference materials may support methodology but must not prove project-specific facts.",
    sample_policy="Sample documents may guide style and structure but must not be used as fact sources.",
    default_final_status="finalized_with_open_items",
    allowed_final_statuses=[
        "finalized_with_open_items",
        "blocked_pending_confirmation",
        "ready_for_human_review",
    ],
    review_focus=[
        "template completeness",
        "checklist coverage",
        "unsupported critical claims",
        "sample misuse",
        "unconfirmed HARA professional judgments",
    ],
    verification_focus=[
        "required artifacts",
        "citation integrity",
        "sample not fact source",
        "critical claims confirmation",
        "candidate update inactive",
    ],
    candidate_learning_policy="Generate candidate updates only; keep proposed/inactive unless explicitly approved.",
    terminology={},
    output_labels={},
)
```

### 7.4 Technical Solution rules 示例

`technical_solution` 是建议的第二文档类型，用于验证泛化能力。

```python
TECHNICAL_SOLUTION_RULES = DocumentTypeRules(
    task_type="technical_solution",
    display_name="技术方案文档",
    description="面向后端、架构或技术评审场景的技术方案写作任务。",
    default_sections=[
        "背景",
        "目标和非目标",
        "需求",
        "架构概览",
        "数据流和接口",
        "实施计划",
        "风险和权衡",
        "上线计划",
        "开放问题",
    ],
    required_sections=[
        "background",
        "goals",
        "requirements",
        "architecture",
        "risks",
        "open issues",
    ],
    critical_claims=[
        "architecture decision",
        "performance target",
        "security boundary",
        "deployment risk",
        "cost estimate",
        "compatibility constraint",
        "rollout risk acceptance",
    ],
    requires_human_confirmation=[
        "final architecture decision",
        "performance target",
        "security boundary",
        "cost estimate",
        "rollout risk acceptance",
    ],
    forbidden_final_claims=[
        "architecture is approved",
        "no security risk exists",
        "performance target is guaranteed",
        "cost is final",
        "rollout is risk-free",
    ],
    confirmation_marker="NEEDS_USER_CONFIRMATION",
    fact_source_roles=["source"],
    non_fact_source_roles=["sample", "template"],
    reference_policy="Reference materials may support general technical rationale but must not prove project-specific requirements or constraints.",
    sample_policy="Sample solution documents may guide structure and style but must not supply project facts.",
    default_final_status="ready_for_human_review",
    allowed_final_statuses=[
        "ready_for_human_review",
        "finalized_with_open_items",
        "blocked_pending_confirmation",
    ],
    review_focus=[
        "template completeness",
        "requirements coverage",
        "unsupported architecture decisions",
        "unsupported performance or cost claims",
        "sample misuse",
        "unresolved risks and trade-offs",
    ],
    verification_focus=[
        "required artifacts",
        "citation integrity",
        "sample not fact source",
        "critical claims confirmation",
        "no HARA terminology leakage",
        "candidate update inactive",
    ],
    candidate_learning_policy="Generate candidate updates only; keep proposed/inactive unless explicitly approved.",
    terminology={},
    output_labels={},
)
```

---

## 8. 通用 Pipeline 与文档类型注入点

### 8.1 Init Run

通用职责：

```text
创建 run_id
创建 runs/<run_id>/
写 manifest.json
写 task_brief.json
加载 task_type
解析 document_type rules
```

文档类型注入点：

```text
display_name
default_final_status
requires_human_confirmation
```

### 8.2 Ingest

通用职责：

```text
扫描输入文件
识别 source/template/checklist/sample/reference
生成 input_inventory.json
生成 source_index.json
生成 knowledge_gaps.md
```

文档类型注入点：

```text
fact_source_roles
non_fact_source_roles
sample_policy
reference_policy
```

必须保持的通用规则：

```text
sample 默认 is_fact_source=false
reference 不能自动成为项目事实来源
unsupported/missing materials 必须进入 gaps
不能静默跳过解析失败
```

### 8.3 Outline

通用职责：

```text
解析 template_structure
生成 outline_l1
生成 outline_final
```

文档类型注入点：

```text
default_sections
required_sections
output_labels
```

规则：

```text
有用户模板时优先用户模板；
没有模板或模板解析失败时才使用 default_sections；
模板缺口必须记录。
```

### 8.4 Evidence Planning

通用职责：

```text
生成 research_questions
从 source_index 中匹配 evidence candidates
生成 evidence_map
标记 supported / weak / unsupported
生成 unresolved_questions
```

文档类型注入点：

```text
critical_claims
requires_human_confirmation
reference_policy
```

规则：

```text
source 可证明项目事实；
reference 可支持方法论或背景，但不能证明项目事实；
sample 不得进入 fact evidence；
critical claim 无证据时必须进入 unresolved。
```

### 8.5 Citation Plan / Section Tasks

通用职责：

```text
为章节绑定 allowed_evidence
生成 citation_plan
生成 section_tasks
生成 writing_plan
```

文档类型注入点：

```text
critical_claims
forbidden_final_claims
confirmation_marker
required_sections
```

规则：

```text
section task 必须明确 forbidden_sources=["sample"]；
关键 claim 章节必须保留 confirmation policy；
unsupported claim 不能被写成确定结论。
```

### 8.6 Draft

通用职责：

```text
按 section_tasks 生成 conservative draft
合并 draft/full_draft.md
保留 source support
标记 NEEDS_USER_CONFIRMATION
```

文档类型注入点：

```text
confirmation_marker
critical_claims
forbidden_final_claims
display_name
```

规则：

```text
没有证据的 critical claim 不得写成最终结论；
sample 不能作为 source support；
reference 不能作为项目事实 support；
允许保守、机械，但不允许伪造确定性专业判断。
```

### 8.7 Review

通用职责：

```text
执行 template review
执行 checklist review
执行 evidence review
执行 final review
生成 review_report.json
生成 final_review.md
```

文档类型注入点：

```text
review_focus
critical_claims
sample_policy
reference_policy
forbidden_final_claims
```

规则：

```text
unsupported critical claim = P0 或 P1；
sample 被当事实来源 = P0；
未确认专业判断必须进入 review；
review item 必须可转成 revision task。
```

### 8.8 Verify

通用职责：

```text
执行脚本化检查
生成 verify_report.json
生成 failures.md
```

文档类型注入点：

```text
verification_focus
allowed_final_statuses
critical_claims
forbidden_final_claims
```

必须脚本化的检查：

```text
required artifacts exist
citation ids exist in source_index
sample not fact source
critical claims have evidence or HITL or confirmation marker
candidate updates are proposed/inactive
no document type leakage
final report includes unresolved items
```

### 8.9 Finalize

通用职责：

```text
生成 revised/full_draft.md
生成 change_log.md
生成 final/final_report.md
生成 final/delivery_summary.md
```

文档类型注入点：

```text
display_name
default_final_status
allowed_final_statuses
critical_claims
output_labels
```

规则：

```text
final report 必须说明输入、输出、限制、未解决事项、人工确认状态；
不得把未确认 critical claim 写成已批准结论；
状态应默认 ready_for_human_review / finalized_with_open_items / blocked_pending_confirmation。
```

### 8.10 Trace / Learning

通用职责：

```text
记录 session_trace.jsonl
记录 hitl_decisions.jsonl
生成 run_summary.md
生成 reusable_patterns.md
生成 candidate_profile_update.yaml
生成 candidate_skill_patch.md
生成 promotion_report.md
```

文档类型注入点：

```text
candidate_learning_policy
review_focus
critical_claims
```

规则：

```text
candidate update 默认 proposed；
不得自动激活；
不得覆盖 stable skill；
应支持 approve/reject/rollback 的未来扩展。
```

---

## 9. Skill / Guideline 层设计

### 9.1 定位

Skill.md 是 Claude Code 的自然语言协作层。它的作用是让 AI coding 工具和 Claude Code 更好理解插件阶段、边界和调用方式。

它不承担核心执行逻辑。

### 9.2 第一版建议结构

泛化初期只建议新增或整理少量 skill：

```text
skills/writing-core/SKILL.md
skills/document-types/hara/SKILL.md
skills/document-types/technical_solution/SKILL.md
```

### 9.3 writing-core/SKILL.md 应包含

```text
1. 插件目标；
2. 通用 workflow；
3. artifact contract；
4. source/template/checklist/sample/reference 角色；
5. sample 不是事实来源；
6. critical claim 规则；
7. HITL 规则；
8. candidate update 不自动激活；
9. 应调用的 Python entrypoints；
10. 常见错误处理。
```

### 9.4 document-types/hara/SKILL.md 应包含

```text
1. HARA 文档目标；
2. HARA 默认章节；
3. HARA critical claims；
4. HARA 必须人工确认内容；
5. HARA forbidden final claims；
6. HARA 表格策略；
7. HARA final report 边界说明。
```

### 9.5 document-types/technical_solution/SKILL.md 应包含

```text
1. 技术方案文档目标；
2. 推荐输入材料；
3. 默认章节结构；
4. 技术方案 critical claims；
5. 架构决策、性能指标、安全边界、成本估算的确认规则；
6. sample/reference 使用边界；
7. review 重点。
```

### 9.6 禁止写法

Skill.md 不应写成：

```text
你是专业写作专家，请自由生成完整文档。
```

而应写成：

```text
你必须通过插件 workflow 运行；
你必须尊重 artifact contract；
你必须调用对应 Python command；
你不能把 sample 当事实来源；
你不能自动确认 critical claims。
```

---

## 10. 第二文档类型选择：technical_solution

### 10.1 为什么不先选 PRD

PRD 太容易变成自由写作任务，容易掩盖以下问题：

```text
1. evidence map 是否仍然有效；
2. critical claim 是否仍被控制；
3. sample 是否仍被禁止作为事实来源；
4. final report 是否仍保留未确认项；
5. HARA hardcode 是否真的清除。
```

### 10.2 为什么选 technical_solution

技术方案文档适合作为第二文档类型，因为它同时具备：

```text
固定模板
明确输入材料
架构决策
约束与风险
性能/成本/安全等关键 claim
review checklist
人类评审场景
```

它足够不同于 HARA，但仍然属于专业文档写作，适合验证通用 engine。

### 10.3 technical_solution demo fixture 建议

```text
examples/technical_solution_demo_fixture/
  task.yaml
  inputs/
    system_context.md
    requirements.md
    solution_template.md
    checklist.md
    architecture_reference.md
    sample_solution.md
```

`task.yaml` 示例：

```yaml
task_type: technical_solution
task_title: 生成技术方案文档
target_audience: 后端/架构评审人员
output_format: markdown
strict_template: true
allow_inference: false
requires_human_confirmation:
  - architecture decision
  - performance target
  - security boundary
  - deployment risk
  - cost estimate
```

### 10.4 technical_solution 验收重点

```text
1. demo run 完整跑通；
2. final_report 不出现 HARA / ASIL / S/E/C / safety goal / hazardous event；
3. sample 不进入 source_index 的 fact source；
4. sample 不进入 citation_plan 的 allowed evidence；
5. architecture decision 无证据时标记 NEEDS_USER_CONFIRMATION；
6. performance target 无证据时标记 NEEDS_USER_CONFIRMATION；
7. final status 不是 approved，而是 ready_for_human_review 或 finalized_with_open_items；
8. candidate update 保持 proposed/inactive；
9. HARA demo fixture 不回归。
```

---

## 11. 测试与验收策略

### 11.1 测试原则

泛化不能靠肉眼判断。每个 Phase 都必须有测试。每新增一个 document type，都必须有 demo fixture 和对应测试。

### 11.2 通用测试类别

```text
test_document_type_registry.py
test_document_type_rules_schema.py
test_hara_demo_regression.py
test_sample_not_fact_source.py
test_reference_not_project_fact_source.py
test_critical_claim_policy.py
test_final_status_policy.py
test_candidate_update_inactive.py
test_no_document_type_leakage.py
```

### 11.3 HARA 回归测试

必须保证：

```text
1. hara_demo_fixture 仍能完整跑通；
2. HARA critical claims 仍要求人工确认；
3. HARA final report 仍保留 open items；
4. sample/reference policy 不变；
5. candidate update 不自动激活。
```

### 11.4 Cross-document leakage 测试

新增 technical_solution 后，必须检查 technical_solution 输出中不出现：

```text
HARA
ASIL
S/E/C
hazardous event
safety goal
HARA professional judgment
```

反过来，也不能让 HARA 输出丢失必要 HARA 术语。

### 11.5 Critical claim 测试

对每个 document type，应至少构造一个无证据 critical claim，验证其不会被写成确定结论。

### 11.6 Candidate learning 测试

所有文档类型都必须验证：

```text
candidate_profile_update.yaml exists
candidate_skill_patch.md exists
status = proposed / inactive
stable skill not modified
rollback_supported = true 或 equivalent metadata exists
```

---

## 12. 泛化 Phase 路线

本轮泛化建议分为 7 个 Phase：

```text
Phase 0：冻结 HARA 基线
Phase 1：抽出 document_type rules
Phase 2：通用化 engine 文案和判断逻辑
Phase 3：新增第二文档类型 technical_solution
Phase 4：补 Skill / guideline 层
Phase 5：扩展第三文档类型并修正抽象
Phase 6：泛化验收与产品化整理
```

严格说 Phase 0 是保护性前置阶段，不是功能开发阶段。但建议纳入统一 Phase 管理。

---

## 13. Phase 0：冻结 HARA 基线

### 13.1 目标

保护已经被认可的 HARA MVP，确保后续泛化不会破坏基线。

### 13.2 范围

```text
1. 确认当前 git 状态；
2. 跑全量测试；
3. 跑 Claude plugin validate；
4. 跑 hara_demo_fixture；
5. 保存 HARA demo 输出摘要或 golden baseline；
6. 明确 HARA 不可回归行为。
```

### 13.3 不做

```text
不抽象 rules；
不新增 document_types；
不修改 engine 行为；
不新增 technical_solution；
不做大重构。
```

### 13.4 验收标准

```text
1. pytest 全量通过；
2. claude plugin validate 通过；
3. hara_demo_fixture 完整 run 通过；
4. HARA 输出基线被记录；
5. 工作区变更仅限文档、基线记录、必要测试脚手架。
```

---

## 14. Phase 1：抽出 document_type rules

### 14.1 目标

把 HARA hardcode 集中到 document type rules 中，但不改变 HARA 行为。

### 14.2 范围

新增：

```text
ai_writing_plugin/document_types/
  __init__.py
  base.py
  hara.py
```

实现：

```text
DocumentTypeRules
get_document_type_rules(task_type)
HARA_RULES
```

把散落的 HARA 规则迁移到 HARA_RULES。

### 14.3 不做

```text
不新增 technical_solution；
不改变 artifact contract；
不改变 HARA 输出含义；
不引入 YAML loader；
不生成大量 Skill.md。
```

### 14.4 验收标准

```text
1. HARA rules 集中在 document_types/hara.py；
2. 关键模块通过 rules 读取 HARA critical claims；
3. HARA demo 不回归；
4. pytest 全过；
5. 代码中 HARA-specific string 明显减少；
6. 仍允许 HARA 术语出现在 hara.py、HARA fixture、HARA tests、HARA docs 中。
```

---

## 15. Phase 2：通用化 engine 文案和判断逻辑

### 15.1 目标

让 generic engine 不再写死 HARA 文案、HARA final title、HARA judgment note 和 HARA-specific verification 文案。

### 15.2 范围

重点模块：

```text
draft.py
review.py
verify.py
finalize.py
learning.py
planning.py
evidence.py
```

改造方向：

```text
HARA 危害分析报告最终交付包
→ {rules.display_name} 最终交付包

HARA professional judgments remain pending
→ Critical judgments remain pending where marked

HARA-specific critical claims
→ rules.critical_claims
```

### 15.3 不做

```text
不新增第二文档类型；
不改变 fixture；
不追求输出文案大幅美化；
不引入 LLM 自由起草；
不删除 HARA rules。
```

### 15.4 验收标准

```text
1. HARA demo 仍通过；
2. engine 大部分文案来自 rules；
3. critical claim review 来自 rules；
4. forbidden final claims 来自 rules；
5. sample/reference policy 仍生效；
6. pytest 全过。
```

---

## 16. Phase 3：新增第二文档类型 technical_solution

### 16.1 目标

用技术方案文档验证 engine 是否真正从 HARA 泛化。

### 16.2 范围

新增：

```text
ai_writing_plugin/document_types/technical_solution.py
examples/technical_solution_demo_fixture/
tests/test_technical_solution_demo.py
```

technical_solution fixture 至少包含：

```text
task.yaml
inputs/system_context.md
inputs/requirements.md
inputs/solution_template.md
inputs/checklist.md
inputs/architecture_reference.md
inputs/sample_solution.md
```

### 16.3 不做

```text
不追求生成非常漂亮的技术方案正文；
不引入第三文档类型；
不大改 pipeline；
不让 reference 证明项目事实；
不让 sample 进入 citation_plan。
```

### 16.4 验收标准

```text
1. technical_solution demo 完整跑通；
2. 输出完整 artifact；
3. final_report 不出现 HARA / ASIL / S/E/C / safety goal 等残留；
4. technical_solution critical claims 无证据时被标记；
5. sample 不作为事实来源；
6. candidate update proposed/inactive；
7. HARA demo 不回归；
8. pytest 全过。
```

---

## 17. Phase 4：补 Skill / guideline 层

### 17.1 目标

补齐 Claude Code 使用层的自然语言说明，让插件泛化能力更容易被人和 AI coding 工具理解。

### 17.2 范围

建议新增：

```text
skills/writing-core/SKILL.md
skills/document-types/hara/SKILL.md
skills/document-types/technical_solution/SKILL.md
```

或在当前已有 skill 结构上做最小调整。

### 17.3 不做

```text
不生成大量空壳 skill；
不把核心执行逻辑迁入 prompt；
不修改 artifact contract；
不新增第三文档类型。
```

### 17.4 验收标准

```text
1. Skill.md 明确插件 workflow；
2. Skill.md 明确 sample/reference/critical claim/HITL 边界；
3. Skill.md 指向 Python command 和 artifact；
4. HARA 与 technical_solution demo 仍通过；
5. pytest 全过。
```

---

## 18. Phase 5：扩展第三文档类型并修正抽象

### 18.1 目标

用 test_report 验证抽象是否过拟合 HARA 和 technical_solution。

### 18.2 推荐第三文档类型

建议选择：

```text
test_report / 测试报告
```

原因：

```text
technical_solution 是决策类文档；
test_report 是结果类文档；
二者差异能暴露 pipeline 泛化不足。
```

### 18.3 范围

新增：

```text
ai_writing_plugin/document_types/test_report.py
examples/test_report_demo_fixture/
tests/test_test_report_demo.py
```

重点验证：

```text
1. 测试结果不能编造；
2. pass/fail 必须有数据或人工确认；
3. 表格型输入能被记录或标记缺口；
4. final conclusion 需要 evidence 或 HITL；
5. sample 仍不能作为事实来源。
```

### 18.4 验收标准

```text
1. test_report demo 跑通；
2. hara / technical_solution 不回归；
3. Phase 5 当时的 hara / technical_solution / test_report 共享同一 pipeline；
4. document_type rules 能表达这些文档类型差异；
5. pytest 全过。
```

---

## 19. Phase 6：泛化验收与产品化整理

### 19.1 目标

把泛化能力整理成可演示、可维护、可继续扩展的产品状态。

### 19.2 范围

更新：

```text
README.md
docs/RUNBOOK.md
docs/CURRENT_ARTIFACT_CONTRACTS.md
docs/DOCUMENT_TYPE_DEVELOPMENT_GUIDE.md
docs/archive/generalization_phase0_6/GENERALIZATION_SUMMARY.md
current demo documentation
```

历史 HARA MVP demo 说明不再作为 public docs 保留；当前 demo 说明以 `docs/EXAMPLES.md` 为准。

明确：

```text
1. 当前支持哪些 document type；
2. 每个 document type 的 demo 命令；
3. 如何新增新文档类型；
4. artifact contract 是否稳定；
5. 当前限制；
6. 不支持事项；
7. 回归测试方式。
```

### 19.3 验收标准

```text
1. Phase 0-6 当时至少支持 hara、technical_solution、test_report；Post-N8 当前已扩展到 hara、technical_solution、test_report、fsr；
2. official L3 文档共享同一 pipeline；
3. 每类文档都有 rules、fixture、tests；
4. HARA 安全边界未丢失；
5. sample policy 全局生效；
6. critical claim policy 全局生效；
7. candidate update policy 全局生效；
8. 文档足够支撑下一位技术人员新增第四文档类型。
```

---

## 20. 新增文档类型的标准流程

当需要新增一个 document type 时，必须按以下流程执行。

### 20.1 先写文档类型说明

创建：

```text
docs/document_types/<task_type>_SPEC.md
```

说明：

```text
1. 文档目标；
2. 目标读者；
3. 典型输入材料；
4. 默认章节；
5. critical claims；
6. 需要人工确认的内容；
7. forbidden final claims；
8. review focus；
9. verification focus；
10. sample/reference policy。
```

### 20.2 再写 machine-readable rules

新增：

```text
ai_writing_plugin/document_types/<task_type>.py
```

并注册到 registry。

### 20.3 再做 demo fixture

新增：

```text
examples/<task_type>_demo_fixture/
```

必须包含：

```text
task.yaml
source material
template
checklist
reference
sample
```

### 20.4 再写测试

至少包含：

```text
full run
sample not fact source
critical claim control
final status
candidate update inactive
no irrelevant document type leakage
```

### 20.5 最后再考虑 Skill.md

如果该文档类型需要额外自然语言说明，再新增：

```text
skills/document-types/<task_type>/SKILL.md
```

---

## 21. Codex 执行约束

后续每个 Phase 的 Codex Prompt 必须包含以下约束。

```text
1. 只执行当前 Phase，不提前做后续 Phase；
2. 不引入 LangChain / RAG / agent framework；
3. 不做自动生成插件平台；
4. 不删除 HARA 功能；
5. 不弱化 sample not fact source；
6. 不让 reference 自动证明项目事实；
7. 不自动确认 critical claims；
8. 不自动激活 candidate updates；
9. 不改变 artifact contract，除非 Phase 明确要求；
10. 所有新增行为必须有测试；
11. 所有失败必须显式写入 artifact；
12. pytest 必须通过；
13. HARA demo fixture 必须持续回归通过。
```

---

## 22. 风险与缓解策略

### 22.1 风险：泛化变成大重构

缓解：每个 Phase 限定范围，Phase 1 只迁移 HARA rules，不新增第二文档类型。

### 22.2 风险：HARA 边界丢失

缓解：HARA demo regression test 必须贯穿所有 Phase。

### 22.3 风险：sample 被误用为事实来源

缓解：sample_not_fact_source 测试必须成为全局回归测试。

### 22.4 风险：technical_solution 输出残留 HARA 文案

缓解：增加 no_hara_leakage 测试。

### 22.5 风险：Skill.md 变成 prompt-only 执行

缓解：Skill.md 必须只描述调用、边界、guideline，不替代 Python engine。

### 22.6 风险：每个文档类型复制一套代码

缓解：新增 document type 时只能新增 rules、fixture、tests；除非必要，不新增 pipeline 模块。

### 22.7 风险：candidate learning 污染 stable skill

缓解：所有 document type 都必须测试 candidate update proposed/inactive。

---

## 23. Phase 0-6 后的决策状态

以下问题在 Phase 0-6 中已经形成当前默认决策：

```text
1. DocumentTypeRules 使用 Python dataclass；
2. docs/document_types/*.md 与 Python rules 双轨维护；
3. Skill 层保持 writing-core + document-types 的少量 guideline；
4. 第三文档类型采用 test_report；
5. 回归测试以结构化 artifact 和语义断言为主，不使用完整 golden 文本快照；
6. 暂不引入 live LLM semantic layer、RAG、LangChain 或 agent framework。
```

Phase 0-6 后仍开放、但不阻塞当前基线的问题：

```text
1. 是否新增第四文档类型；
2. 何时引入更强文本质量层；
3. 如何优化 HITL 交互体验；
4. 是否实现 candidate update approve/reject/rollback 的实际启用机制；
5. 是否支持更多输入文件格式。
```

---

## 24. 总体验收标准

本轮泛化完成后，应满足：

```text
1. 同一个 Claude Code 插件支持至少四类 official L3 文档：
   - hara
   - technical_solution
   - test_report
   - fsr

2. official L3 文档共享同一套 generic pipeline；

3. 每类文档通过 document_type rules 表达差异；

4. 每类文档都有 demo fixture 和测试；

5. HARA critical claims 仍需人工确认；

6. technical_solution critical claims 仍需 evidence 或 HITL；

7. test_report 的测试结果和结论不能被编造；

8. sample 在所有文档类型中都不能作为事实来源；

9. reference 不能自动证明项目事实；

10. final report 不会伪装成专业批准文件；

11. candidate update 不自动覆盖 stable skill；

12. 新增第四文档类型有清晰流程和文档指导。
```

---

## 25. 最终结论

本轮泛化的核心不是“让 AI 自动生成更多插件”，也不是“把 HARA 字样删掉”。

正确方向是：

```text
保留已经验证过的 Python deterministic writing engine；
保留 artifact / evidence / review / verify / HITL / learning 闭环；
把 HARA-specific 语义迁移为 document_type rules；
用 technical_solution 验证第二文档类型；
再用 test_report 验证第三文档类型；
通过 fixture 和 tests 保证泛化不破坏边界。
```

一句话总结：

```text
泛化方案 = 一个插件 + 一个通用写作闭环 + 多个可测试的 document_type rules。
```
