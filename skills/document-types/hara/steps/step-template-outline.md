# HARA 子 skill · Step 4 · 模板大纲 (Template Outline)

本文件是通用骨架 `skills/workflow-steps/step-template-outline/SKILL.md` 在 `task_type: hara` 下加载的任务专属子 skill。通用两阶段流程（**先 L1、后 L2**）与输入文档 L1→L2→L3 访问协议以骨架与 `writing-core` 为准；HARA 领域规则以根 skill `skills/document-types/hara/SKILL.md` 为准。

## 本步目的要点（HARA 领域补充）

### 阶段 A · 定 L1（文档结构与一级大纲）

- 从 `task_brief` 读取 HARA 写作任务：`critical_claims`、是否 `strict_template`、目标读者、With-Reference / From-Scratch 情景。
- 经 Step 3 三级目录 **L1→L2→L3** 阅读 `role=template` 的 HARA 模板（T2），提取强制章节与顺序。
- 经三级目录阅读 `role=sample` 或用户提供的**同类型 HARA 参考报告**（T4），提取**章节划分与表格形状**（不提取 hazard/S-E-C/ASIL/SG 事实）。
- 合并 HARA `DocumentTypeRules` 与 ISO 26262-3 期望的 12 个 L1 章（SEC-DOC … SEC-REVIEW），产出 `outline_l1.md` 与 `template_structure.json` 的 L1 节点。
- **底线**：sample 只借结构；L1 不写 hazard/评级结论。

### 阶段 B · 定 L2（二级大纲，L1 定稿后）

- **逐 L1 章**展开 L2，依据：模板在该章下的子节/表格列、sample 同章的小节粒度、任务对该章的 critical claim、`topic_index` 中 Item/工况/接口等材料是否可支撑。
- 例：SEC-ITEM 的 L2 可含「功能清单 F-xx」「系统边界表」「外部接口 IF-xx」「运行约束」；SEC-OPS 的 L2 可含「工况分类说明」「OS-xx 工况表」——**按模板与参考文档实际形状裁剪**，不机械硬套。
- 材料缺口时 L2 保留占位并标 `evidence: pending`；写入 `outline_l2.md` 与 `template_structure.json` 的 `level=2` 节点（`parent_id` 指向 L1）。
- **底线**：L2 只定义写作块与 intent，不填 S/E/C 数值或 ASIL 结论。

## HARA 报告过程总览（本步定位）

| 输入 | 角色 | 本步如何使用 |
|---|---|---|
| `task_brief` | 写作任务 | 定范围、强制章、确认要求 |
| template（HARA 模板） | T2 结构 | 定 L1 强制节、L2 子节与表格列 |
| sample / 同类型 HARA 参考 | T4 形状 | 对照章节粒度与表格形状，不借事实 |
| reference（ISO 26262-3 等） | T3 方法学 | 可选：标准章节/Table 引用位置，不借评级值 |
| `topic_index` | 材料导航 | 判断某 L2 是否有 T1 材料可写 |

**本步定位**：固化 HARA 交付报告的 L1 章 + L2 小节骨架；**不写正文**。

## HARA 标准 L1 章节（合并 template / 规则后的期望）

| 节序 | section_id | L1 标题 | 强制 |
|---|---|---|---|
| 1 | SEC-DOC | 文档信息与修订历史 |  |
| 2 | SEC-SCOPE | 文档目的与范围 |  |
| 3 | SEC-REF | 参考文件 |  |
| 4 | SEC-TERMS | 术语与缩略语 |  |
| 5 | SEC-ITEM | Item 定义摘要 | ★ |
| 6 | SEC-OPS | 运行工况与模式 | ★ |
| 7 | SEC-HAZ | 危害识别 | ★ |
| 8 | SEC-HE | 危害事件分析 | ★ |
| 9 | SEC-SEC | S/E/C 评级与 ASIL 候选 | ★ |
| 10 | SEC-SG | 安全目标候选 | ★ |
| 11 | SEC-OPEN | 开放问题与待确认项 |  |
| 12 | SEC-REVIEW | 审查总结 | ★ |

With-Reference 情景须在 L1 增加 **Differences from Reference HARA**（可并入 SEC-SCOPE 或独立 L1，须在 `warnings` 说明）。

## HARA 各 L1 下常见 L2 划分（阶段 B 参考，按 template/sample 实际情况取舍）

| L1 | 常见 L2 小节（示例） | 主要结构来源 |
|---|---|---|
| SEC-ITEM | 功能清单；系统边界；外部接口；运行约束 | template + item definition sample 形状 |
| SEC-OPS | 工况分类；OS-xx 工况表；模式说明 | template + operational situations 形状 |
| SEC-HAZ | 引导词说明；H-xx 危害表 | template HARA 表列 |
| SEC-HE | HE-xxx 危害事件表 | template |
| SEC-SEC | S 评级；E 评级；C 评级；ASIL 候选 | template + ISO Table 1–4 引用位 |
| SEC-SG | SG-xx 安全目标表（含 Safe State / FTTI 列） | template + §7.4.2.4 字段要求 |
| SEC-OPEN | 按类别汇总 open items | 任务 + checklist |
| SEC-REVIEW | 覆盖度摘要；Confirmation Review 占位 | template |

L2 的 `section_id` 建议：`{L1_id}-L2-{序号}` 或 `{L1_id}-{短名}`，与 `template_structure.nodes` 一致。

## 本步将被审查的关键点（自检）

| 检查项 | 自检方法 |
|---|---|
| L1 完整 | 12 个 SEC-* L1 齐全（+ With-Reference 差异节） |
| L2 在 L1 之后 | `outline_l2.md` 每个 L2 有明确 `parent` L1 |
| template 已读 | `template_source` 指向实际 template；经 document_tocs 读取 |
| sample 仅形状 | L2 intent 无 sample 中的具体 hazard/评级事实 |
| strict_template | mandatory L1 未删改 |
| 三 artifact 一致 | JSON nodes ↔ outline_l1 ↔ outline_l2 |

## A1 审核任务（HARA）

### 典型审核子任务

1. 核对 L1 覆盖 HARA 12 章 + 情景必备节。
2. 核对 L2 仅出现在 L1 定稿之后，且每 L1 下 L2 与 template/sample 形状一致或 gap 已说明。
3. 核对 sample/reference 未升格为事实。
4. 核对三份 artifact 字段一致。

## A2 修订任务（HARA）

### 典型修订子任务

1. 读 task_brief + template（L1→L2→L3）提取 L1 骨架。
2. 读 sample/同类型参考（L1→L2→L3）对照章节形状。
3. 写入 L1 → `outline_l1.md` + JSON L1 节点。
4. **L1 定稿后**逐章定 L2 → `outline_l2.md` + JSON L2 节点。
5. 标注 `needs_human_confirmation` 与 `evidence: pending`。

## state.json 示例（HARA）

```json
{
  "step": "template-outline",
  "revision_state": {
    "subtasks": [
      {"id": "rt-1", "desc": "读 task+template+sample 定 L1", "status": "done"},
      {"id": "rt-2", "desc": "写入 outline_l1 与 L1 节点", "status": "done"},
      {"id": "rt-3", "desc": "逐 L1 章定 L2 大纲", "status": "running"},
      {"id": "rt-4", "desc": "写入 outline_l2 与 L2 节点", "status": "not_run"}
    ]
  }
}
```

## B 审核检查项（HARA）

subagent 逐项核对：L1 是否综合任务+template+同类型参考且覆盖 HARA 强制章；L2 是否在 L1 定稿后按实际情况展开；template/sample 是否经三级目录读取；sample 是否仅借结构；`outline_l1` / `outline_l2` / `template_structure.json` 是否一致；是否未预设 hazard/rating/ASIL/SG 结论。
