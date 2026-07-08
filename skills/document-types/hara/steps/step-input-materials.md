# HARA 子 skill · Step 1 · 输入材料 (Input Materials)

本文件是通用骨架 `skills/workflow-steps/step-input-materials/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。它只补充 HARA 专属的目的要点、候选方案示例、典型子任务与审核检查项；通用流程、artifact 契约与角色边界以骨架为准。HARA 领域规则（critical claims、章节、forbidden final claims、source tier）以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 领域补充）

- 确认本步 run 元数据与 `task_type: hara` 边界，并加载 HARA `DocumentTypeRules` 与本子 skill；共享 run 起点与 manifest / task_brief ownership 由通用 Step 1 / deterministic engine 负责。
- 把 task.yaml 声明的每份输入登记为材料记录（分配 file_id、记录 path/title/format）。
- 判定每份材料的 `role`：item definition / operational situations / assumptions 多为 `source`；HARA 模板为 `template`；safety/review checklist 为 `checklist`；functional safety 方法学为 `reference`；既有 HARA 报告样例为 `sample`（仅风格/表格形状）。
- 确认 HARA critical claims（hazard、hazardous event、S/E/C、ASIL、safety goal、final acceptability）已声明为 `requires_human_confirmation`，等待 T0/T1 证据或 HITL。
- 对缺失/不支持/解析失败的材料显式记录，不静默跳过。
- **底线**：不得把 sample HARA 报告或 reference 方法学当作 hazard/rating/ASIL/safety goal 的事实来源。

## HARA 报告过程总览（本步定位）

HARA（ISO 26262-3）经 **13 个** workflow step skill 产出 hazard 分析报告（逻辑 Step 1–6、9–15）。本步是流程入口，对应「输入材料准备」阶段。

**HARA 输入材料类别与事实来源边界**：

- ✅ 事实来源（T1 项目源）：item 定义文件、运行工况清单、系统架构说明
- ❌ 结构约束（T2，非事实来源）：HARA 模板
- ❌ 方法框架（T3，非事实来源）：ISO 26262-3 标准文本
- ❌ 严格禁止作为事实依据（T4）：sample HARA 报告——其 hazard、评级、ASIL、安全目标不得照搬

**本步定位**：登记并分类全部输入，确认 source / template / checklist / reference / sample 的 role 与事实来源边界，**不做任何 HARA 专业判断**。


## 本步将被审查的关键点（Review / Verification 自检清单）

本步输出（`manifest.yaml`、material role 声明）将在 Step 10/11 被以下检查点定位。subagent 交付前应自检：

| 关联检查 | 检查项 | 自检方法 |
|---|---|---|
| VC-1-01 | manifest 存在且 role / tier / is_fact_source 字段完整 | 遍历所有 file_id，确认三字段非空 |
| VC-2-04 | 每条 source 记录含 provenance | 检查 path、format、file_id 齐全 |
| VC-5-04 | 无静默解析失败 | 每个 file_id 含 `parse_status`（即使 `pending`）|
| RD-2 | 无 sample 被升格为 source | sample HARA 报告必须 role=`sample`，is_fact_source=false |
| RD-6 | knowledge gap 已显式登记 | 缺失材料登记到 `knowledge_gaps`，不静默跳过 |

**自检底线**：sample HARA 报告与 reference 方法学的 role 是否被正确隔离；如有任何关键字段缺失，登记 knowledge_gap 而不是推断填值。



## ISO 26262-3 标准 Checklist 与 Review 要点（Clause 对照）

本步对应 ISO 26262-3:2018 **Clause 5（Item Definition）** 输入登记，以及文档治理层（Scope & References）。
登记输入时必须为后续 Clause 5/6 工作奠定可追溯基础。

### A1 · Item Definition 输入完备性（ISO 26262-3 §5）

- [ ] Item 功能清单（F-xx）来源已登记（item_definition / SyRS / SRS）
- [ ] Item 非功能性需求（性能、可用性、可维护性）来源已登记
- [ ] 系统边界（In-scope / Out-of-scope）来源已登记
- [ ] 外部接口（传感器 / 执行器 / CAN / 机械 / 用户）来源已登记，含信号方向描述材料
- [ ] 假设与依赖（Assumptions & Constraints）来源已显式登记
- [ ] 操作环境（速度范围、温度、车型）来源已登记
- [ ] **合理可预见的误用**（reasonably foreseeable misuse，ISO 26262-3 §5.4.4 b）来源已登记
- [ ] Legacy item 信息（若有）来源已登记
- [ ] 缺失项登记到 `knowledge_gaps`，**不静默跳过**

### A2 · 文档范围与参考（Scope & References）

- [ ] 适用标准声明（ISO 26262-3:2018）记入 manifest 元数据
- [ ] 项目输入文件**含版本号与日期**
- [ ] 参考文档清单**含版本号**

### Review 要点（按 Clause 映射）

| 失效 | 级别 |
|---|---|
| Item 边界材料缺失且无 gap 登记 | **P0** |
| 接口信号方向材料缺失 | **P1** |
| 误用材料未登记（§5.4.4 b） | **P0** |
| 假设隐式而非显式 | **P1** |
| 引用文档无版本号 | **P1** |
| 适用标准版本声明缺失或版本错配 | **P0** |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主要风险 | 输入不全、推断填值 | 误用既有项目的边界 / 接口定义 |
| 本步动作 | 缺失项标 `[PENDING]`、登记 knowledge gap | 既有 HARA 报告 role 必须 `sample`；项目独立 source 单独登记；为 Step 9/13 的 **Δ-Analysis** 预留 file_id |


## ISO 26262 HARA 方法论（本步专属执行指引）

### HARA 典型输入材料与 role 判定指引

| 材料类型 | 典型文件名/格式 | role | is_fact_source | 用途 |
|---|---|---|---|---|
| Item 定义文档 | item_definition.docx / SyRS / SRS | source | true | item 功能描述、系统边界、接口、运行约束 |
| 运行工况清单 | operational_situations.xlsx / ODD | source | true | 运行场景、暴露环境描述 |
| 系统架构说明 | sys_arch.pdf / block_diagram | source | true | 系统功能拆解、接口信号 |
| 失效模式参考 / FMEA | fmea.xlsx / failure_modes.pdf | source | true | 可能危害类型的初始输入（若由项目组提供）|
| HARA 模板 | hara_template.docx | template | false | 报告结构、表格格式、强制章节 |
| Safety / review checklist | fs_checklist.xlsx / review_criteria | checklist | false | ISO 26262-3 检查条目 |
| 功能安全方法学 | ISO_26262_3.pdf / functional_safety_guide | reference | false | S/E/C/ASIL 评定方法（T3，仅方法框架）|
| 既有 HARA 报告样例 | sample_hara.pdf / example_report | sample | false | 仅供格式/表格形状/措辞风格参考（T4）|

### HARA Source 材料应包含的关键信息

若收到 item definition source，应确认其包含：
1. **item 名称与版本号**
2. **主要功能列表**（≥3 条，每条功能有具体描述）
3. **系统边界**（包含的子系统 / 明确不包含的子系统）
4. **关键外部接口**（传感器/执行器/CAN信号/机械接口，信号名称与方向）
5. **运行约束**（速度范围、环境温度、应用车型限制、使用场景）

若以上任一项缺失，登记为 `知识缺口（knowledge_gap）`，在 manifest 中显式标注并向用户确认，**不得用 sample 替代**。

## A1 审核任务（HARA）

### 候选方案（示例）
- 方案A 按检查维度逐项核对（task_type=hara/inputs/role 声明）。
- 方案B 按 artifact（manifest/task_brief）逐项核对。
- 方案C 先扫高风险约束（HARA 样例报告是否被误标为 source、critical claims 是否声明 requires_human_confirmation）再补其余。

### 典型审核子任务
1. 核对 `task_type` 是否为 `hara`，inputs/role 声明是否正确。
2. 核对 HARA sample 报告被标为 `sample`（非 `source`），方法学被标为 `reference`。
3. 核对 hazard/S-E-C/ASIL/safety goal 等 critical claims 是否声明为 `requires_human_confirmation`。
4. 核对缺失/不支持材料是否显式标记，manifest/task_brief 是否符合 artifact 契约。

## A2 修订任务（HARA）

### 候选方案（示例）
- 方案A 一次性批量登记全部输入后统一校验 role 与 source≠sample。
- 方案B 按 role 分组分批登记（source / template / checklist / reference / sample）。
- 方案C 逐份材料登记并即时校验 path 可达性、format 支持与 source≠sample。

### 典型修订子任务
1. 确认 Phase 0 run 起点 artifacts 已由 deterministic engine 生成。
2. 确认 `task_type: hara` 并加载 HARA 规则与本子 skill。
3. 逐份登记输入材料（分配 file_id、记录 path/title/format/role）。
4. 校验 HARA source≠sample 边界与缺失/不支持材料的显式标记。

## state.json 示例（HARA）

```json
{
  "step": "input-materials",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对 task_type=hara/inputs/role 声明", "status": "done"},
      {"id": "rv-2", "desc": "核对 HARA sample 报告未被标为 source", "status": "running"},
      {"id": "rv-3", "desc": "核对 HARA critical claims 声明 requires_human_confirmation", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "确认 Phase 0 run 起点 artifacts 已由 engine 生成", "status": "done"},
      {"id": "rt-2", "desc": "确认 task_type=hara 并加载 HARA 规则", "status": "running"},
      {"id": "rt-3", "desc": "逐份登记输入材料并标注 role", "status": "not_run"},
      {"id": "rt-4", "desc": "校验 source≠sample 边界与缺失/不支持标记", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：`task_type: hara` 与 `inputs` / `role` 声明是否正确；HARA sample 报告与方法学 reference 是否未被升格为事实来源（source≠sample）；HARA critical claims 是否声明 `requires_human_confirmation`；缺失/不支持材料是否已显式标记。
