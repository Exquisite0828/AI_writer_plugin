# System Architecture 子 skill · Step 12 · 运行总结

骨架：`skills/workflow-steps/step-run-summary/SKILL.md`。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点

- 生成 `run_summary.md`、`session_trace.jsonl`、`hitl_decisions.jsonl`、`reusable_patterns.md`。
- 中性叙事；可复用模式**不含**具体元素/接口/分配/资源事实。

## System Architecture 方法论（本步定位）

本步对应 **追溯与学习**；对本次架构 run 做中性总结。

## 本步 Review / Checklist 要点

### run_summary 强制字段 Checklist

- [ ] run_id、task_type、document_status、start/end timestamp
- [ ] 输入概览：source/template/checklist/reference/sample 计数
- [ ] 阶段映射：13 step 状态与 artifact 链接
- [ ] 关键统计：元素数、接口数、分配矩阵行数、open 数、HITL 数
- [ ] gap 分类：按 SEC-* 分类统计
- [ ] P0 / P1 关闭情况
- [ ] 流程信号：参考架构误用风险、Direction 缺失、分配 open 密集度等
- [ ] 与架构边界一致性声明：非批准、非合规

### gap 分类 Checklist

| 分类 | 典型 gap |
|---|---|
| SEC-REQTRACE | 上游 SyRS 不全 |
| SEC-LARCH | 逻辑架构分解依据不足 |
| SEC-PARCH | 物理/平台信息缺失 |
| SEC-IF | 接口方向/对端缺失 |
| SEC-ALLOC | 分配理由无 source |
| SEC-DIAG | 诊断/降级链路缺失 |
| SEC-RES | 资源约束无 source |
| SEC-SAFE-ARCH | FSR/TSC 架构约束缺失 |

### From-Scratch 专属 Checklist

- [ ] gap 计数较大属预期；流程信号注明“初版架构 gap 多为正常”

### With-Reference 专属 Checklist

- [ ] 必含“参考架构误用风险”段
- [ ] Δ 统计：Added / Removed / Modified / Scope-changed
- [ ] reusable_patterns 可写 Δ-Analysis 方法学，**不**写本次 Δ 具体内容

### 常见 P0

| 错误 | 后果 |
|---|---|
| run_summary 含批准/合规措辞 | 越权语义 |
| reusable_patterns 含具体元素/接口/资源事实 | 项目事实泄漏 |

## A1 / A2 / B

**A1**：无批准语义；gap 已分类；artifact 链接齐全。  
**A2**：补 trace / HITL / 流程信号。  
**B**：summary 与架构边界一致；reusable_patterns 无项目事实。
