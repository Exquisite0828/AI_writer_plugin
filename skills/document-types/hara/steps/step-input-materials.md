# HARA 子 skill · Step 1 · 输入材料 (Input Materials)

通用骨架：`skills/workflow-steps/step-input-materials/SKILL.md`。HARA 根规则：`skills/document-types/hara/SKILL.md`。本 overlay 只补充 HARA 输入分类与审查边界；`init-run` 只创建 `input_refs.json`、`manifest.json` 和 `task_brief.json`，专业 artifact 由 agent worker 负责。

## Purpose

- 确认 `task_type: hara`，加载 HARA Skill/overlay guidance；当前 Python 不提供 HARA `DocumentTypeRules`。
- 按 task 声明登记每份输入材料：file_id、path、title、format、role、parse_status。
- 判定 role：item definition、operational situations、assumptions、system architecture 通常为 `source`；HARA template 为 `template`；safety/review checklist 为 `checklist`；ISO/methodology 为 `reference`；既有 HARA 报告样例为 `sample`。
- 声明 HARA critical claims（hazard、hazardous event、S/E/C、ASIL、safety goal、final acceptability）`requires_human_confirmation`。
- 对缺失、不支持、解析失败显式记录；不得静默跳过。

底线：sample HARA 报告或 reference 方法学不能作为 hazard、rating、ASIL、safety goal 的事实来源。

## HARA Input Checklist

- Item 功能清单、系统边界、外部接口、假设依赖、操作环境、合理可预见误用来源已登记；缺失则写 knowledge gap。
- 项目输入和参考文档有版本/日期；适用 ISO 26262-3 版本有声明或 open。
- source/template/checklist/reference/sample 的 role、tier、is_fact_source 清楚。
- sample HARA 必须 `role=sample`、`is_fact_source=false`。
- 方法学 reference 只能支持方法，不支持项目 hazard 或 rating。

## Typical Review Findings

P0：Item 边界材料缺失且无 gap；误用材料未登记；适用标准版本错配；sample 被升格为 source；HARA critical claim 未声明 human confirmation。

P1：接口信号方向材料缺失；假设隐式；引用文档缺版本号；parse_status 缺失。

## A1 / A2 / B

**A1**：核对 `task_type=hara`、inputs/role、sample/reference 隔离、critical claims confirmation 声明、缺失/不支持材料可见。
**A2**：只修正材料登记、role/tier/is_fact_source、gap 记录；不得生成 HARA 专业判断。
**B**：Stage review worker 核对 source≠sample、manifest/task_brief/input refs 边界、HARA claims pending 状态。
