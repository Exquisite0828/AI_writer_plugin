# Technical Solution Document Type Spec

## 1. Purpose

Technical solution documents support backend, architecture, and technical review workflows. They organize project background, goals, requirements, architecture, interfaces, implementation plan, risks, rollout plan, and open issues.

## 2. Target Audience

Backend engineers, architecture reviewers, technical leads, and project maintainers.

## 3. Typical Inputs

- source: `system_context.md`, `requirements.md`
- template: `solution_template.md`
- checklist: `checklist.md`
- reference: `architecture_reference.md`
- sample: `sample_solution.md`

## 4. Default Sections

- 背景
- 目标和非目标
- 需求
- 架构概览
- 数据流和接口
- 实施计划
- 风险和权衡
- 上线计划
- 开放问题

## 5. Critical Claims

- architecture decision
- performance target
- security boundary
- deployment risk
- cost estimate
- compatibility constraint
- rollout risk acceptance

## 6. Requires Human Confirmation

- final architecture decision
- performance target
- security boundary
- cost estimate
- rollout risk acceptance

## 7. Forbidden Final Claims

- architecture is approved
- no security risk exists
- performance target is guaranteed
- cost is final
- rollout is risk-free
- production ready

## 8. Source Policy

`source` inputs may support project facts. `reference` inputs may support general technical rationale or methodology, but must not prove project-specific requirements, constraints, decisions, performance targets, costs, or risk acceptance. `sample` inputs may guide structure and style, but must not be used as fact sources.

## 9. Review Focus

- template completeness
- requirements coverage
- unsupported architecture decisions
- unsupported performance or cost claims
- unsupported security boundary claims
- sample misuse
- reference misuse as project fact
- unresolved risks and trade-offs

## 10. Verification Focus

- required artifacts
- citation integrity
- sample not fact source
- reference not project fact source
- critical claims confirmation
- document type terminology isolation
- candidate update inactive
