from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THIN_CONTROLLER_PROMPTS = [
    ROOT / "commands/write.md",
    ROOT / "skills/workflow-orchestrator/SKILL.md",
]
CANONICAL_STEP_PROMPTS = sorted((ROOT / "skills/workflow-steps").glob("*/SKILL.md"))
DOCUMENT_TYPE_OVERLAYS = sorted((ROOT / "skills/document-types").glob("*/steps/*.md"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_command_and_orchestrator_do_not_assign_artifact_production_to_main_agent():
    forbidden_phrases = [
        "主执行上下文产出",
        "各 step 的 artifacts 由当前主执行上下文",
        "各 step 的产出由主执行上下文",
        "驱动本 stage 产出（主执行上下文）",
        "当前主执行上下文按该 step skill 产出符合 artifact 契约的 artifacts",
    ]

    matches = []
    for path in THIN_CONTROLLER_PROMPTS:
        text = read(path)
        for phrase in forbidden_phrases:
            if phrase in text:
                matches.append((path.relative_to(ROOT).as_posix(), phrase))

    assert not matches, f"top-level prompts still make the main agent produce artifacts: {matches}"


def test_canonical_steps_use_one_step_worker_and_one_stage_review_worker():
    assert len(CANONICAL_STEP_PROMPTS) == 13
    forbidden_phrases = [
        "subagent",
        "子代理",
        "主执行上下文",
        "review_state",
        "revision_state",
        "state.json",
    ]
    matches = []
    missing = []

    for path in CANONICAL_STEP_PROMPTS:
        text = read(path)
        for phrase in forbidden_phrases:
            if phrase in text:
                matches.append((path.relative_to(ROOT).as_posix(), phrase))
        for phrase in ["当前 step worker", "StepResult", "Stage review worker"]:
            if phrase not in text:
                missing.append((path.relative_to(ROOT).as_posix(), phrase))

    assert not matches, f"canonical steps still contain legacy nested-worker state: {matches}"
    assert not missing, f"canonical steps do not declare the current worker boundary: {missing}"


def test_canonical_steps_make_review_read_only_and_redispatch_a2_to_step_worker():
    forbidden = [
        "Stage review worker可按当前document-type guidance的A2规则局部修订受影响artifact",
        "必须写入 `stage_reviews/<stage>/issues_index.json`",
    ]
    required = [
        "Stage review worker只记录问题，不修改专业artifact或StepResult",
        "A2由重新派发的原step worker执行",
        "A2 worker不得自行派发其他step",
        "controller按自动依赖协议重跑被失效的后续step",
        "stage_reviews/<stage>/issues.json",
        "build-stage-review-issues",
        "validate-stage-review-issues",
    ]
    matches = []
    missing = []

    for path in CANONICAL_STEP_PROMPTS:
        text = read(path)
        for phrase in forbidden:
            if phrase in text:
                matches.append((path.relative_to(ROOT).as_posix(), phrase))
        for phrase in required:
            if phrase not in text:
                missing.append((path.relative_to(ROOT).as_posix(), phrase))

    assert not matches, f"stage review worker still edits professional artifacts: {matches}"
    assert not missing, f"canonical revision handoff is incomplete: {missing}"


def test_canonical_steps_treat_document_type_guidance_as_optional_lazy_refs():
    required = [
        "wrapper 与本 canonical workflow Skill 是必需引用",
        "document-type root Skill 与 per-step overlay 都按文件存在性懒加载",
        "root Skill 存在但 per-step overlay 缺失是合法的 root-only 模式",
        "所有实际出现在 `instruction_refs[]` 中的引用都必须通过 path/hash 校验",
        "可选 document-type root Skill 或 overlay 未出现不得判为 `metadata_invalid`",
        "已包含的引用缺失或 hash 无效时返回 `metadata_invalid`",
    ]
    missing = []

    assert len(CANONICAL_STEP_PROMPTS) == 13
    for path in CANONICAL_STEP_PROMPTS:
        text = read(path)
        for phrase in required:
            if phrase not in text:
                missing.append((path.relative_to(ROOT).as_posix(), phrase))

    assert not missing, f"canonical document-type lazy-ref contract is incomplete: {missing}"


def test_document_type_overlays_do_not_reintroduce_nested_worker_state():
    forbidden_phrases = [
        "subagent",
        "子代理",
        "review_state",
        "revision_state",
        "state.json",
    ]
    matches = []

    for path in DOCUMENT_TYPE_OVERLAYS:
        text = read(path)
        for phrase in forbidden_phrases:
            if phrase in text:
                matches.append((path.relative_to(ROOT).as_posix(), phrase))

    assert not matches, f"document-type overlays still contain nested-worker state: {matches}"


def test_step_one_worker_consumes_controller_owned_scaffold():
    step_one = read(ROOT / "skills/workflow-steps/step-input-materials/SKILL.md")
    controller_text = "\n".join(read(path) for path in THIN_CONTROLLER_PROMPTS)

    assert "python -m ai_writing_plugin init-run --task <task.yaml>" not in step_one
    for phrase in [
        "Controller-owned Phase 0 precondition",
        "Step 1 worker 不得调用 `init-run`",
        "只读核对 `input_refs.json`、`manifest.json` 与 `task_brief.json`",
        "StepResult 引用三个 scaffold files 的最终 path/hash",
    ]:
        assert phrase in step_one
    assert "init-run → init-progress-ledger → prepare-step-worker-dispatch" in controller_text


def test_command_and_orchestrator_define_thin_controller_contract():
    combined = "\n".join(read(path) for path in THIN_CONTROLLER_PROMPTS)

    required_phrases = [
        "薄编排器",
        "thin controller",
        "step execution context",
        "短摘要",
        "路径/hash",
        "artifact_paths",
        "artifact_hashes",
        "review_package_paths",
        "blocking_issues_count",
        "next_gate_status",
        "StepResult",
        "ReviewResult",
        "runs/<run_id>/orchestration/step_results/<step>.json",
        "runs/<run_id>/orchestration/review_results/<stage>/<step>.json",
        "StepContextPackage",
        "runs/<run_id>/orchestration/context_packages/<stage>/<step>.json",
        "ProgressLedger",
        "runs/<run_id>/orchestration/progress_ledger.json",
        "StepWorkerDispatch",
        "runs/<run_id>/orchestration/worker_dispatches/<stage>/<step>.json",
        "全 13 step worker handoff",
        "ReviewContextPackage",
        "runs/<run_id>/orchestration/review_context_packages/<stage>.json",
        "StageGateResult",
        "runs/<run_id>/orchestration/stage_gate_results/<stage>.json",
        "不回放 issues.json",
        "不回放 review_units.json",
        "不读取 artifact 正文",
        "不得粘贴 artifact 正文",
        "不得批量读取 step canonical",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in combined]

    assert not missing, f"thin controller prompt contract is incomplete: {missing}"


def test_thin_controller_prompts_do_not_keep_worker_pilot_escape_hatch():
    forbidden_pilot_phrases = [
        "ingest worker pilot",
        "非 `ingest` stage 暂不宣称",
        "非 `ingest` step 不扩大 worker pilot 范围",
        "非 ingest 不扩大 worker pilot 范围",
    ]

    matches = []
    for path in THIN_CONTROLLER_PROMPTS:
        text = read(path)
        for phrase in forbidden_pilot_phrases:
            if phrase in text:
                matches.append((path.relative_to(ROOT).as_posix(), phrase))

    assert not matches, f"thin controller prompts still contain worker pilot escape hatch: {matches}"


def test_thin_controller_requires_real_task_tool_worker_handoff():
    combined = "\n".join(read(path) for path in THIN_CONTROLLER_PROMPTS)

    required_phrases = [
        "Task tool",
        "Agent tool",
        "Task tool / Agent tool",
        "worker_unavailable",
        "fail closed",
        "不得 fallback 到主上下文执行 step 或 review",
        "Step worker 只接收 StepWorkerDispatch 路径和 StepContextPackage 路径",
        "Review worker 只接收 ReviewContextPackage 路径",
        "不得把 artifact 正文、canonical 正文或 review 明细正文传给 worker",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in combined]

    assert not missing, f"real worker handoff contract is incomplete: {missing}"


def test_thin_controller_requires_document_type_lazy_loading():
    combined = "\n".join(read(path) for path in THIN_CONTROLLER_PROMPTS)

    required_phrases = [
        "DocumentTypeLazyLoad",
        "不得批量读取 `skills/document-types/**`",
        "只把当前 `task_type` 下实际存在的 document-type path/hash 放进 StepContextPackage",
        "wrapper 与 canonical workflow Skill 是必需引用",
        "root-only 模式合法",
        "缺少可选 overlay 不是 `metadata_invalid`",
        "必须验证所有已包含引用的 path/hash",
        "worker 只能通过 StepContextPackage 中的 path/hash 读取当前 `task_type` 的 document type 文件",
        "不得读取 sibling document types",
        "task_type=hara",
        "SoftwareArchitecture",
        "SystemRequirement",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in combined]

    assert not missing, f"document-type lazy routing contract is incomplete: {missing}"


def test_thin_controller_requires_python_metadata_builders_and_validators():
    combined = "\n".join(read(path) for path in THIN_CONTROLLER_PROMPTS)

    required_phrases = [
        "python -m ai_writing_plugin init-progress-ledger --run-dir <run_dir>",
        "python -m ai_writing_plugin prepare-step-worker-dispatch",
        "python -m ai_writing_plugin validate-step-context-package",
        "python -m ai_writing_plugin validate-step-worker-dispatch",
        "python -m ai_writing_plugin validate-progress-ledger",
        "python -m ai_writing_plugin validate-step-result",
        "python -m ai_writing_plugin validate-review-result",
        "python -m ai_writing_plugin complete-step-worker-dispatch",
        "python -m ai_writing_plugin build-review-context-package",
        "python -m ai_writing_plugin validate-review-context-package",
        "python -m ai_writing_plugin build-stage-gate-result",
        "python -m ai_writing_plugin validate-stage-gate-result",
        "metadata_invalid",
        "不得手写 orchestration JSON",
        "不得手动 patch ledger",
        "主 Agent 不得写 StepResult",
        "主 Agent 不得写 ReviewResult",
        "主 Agent 不得写 step artifacts",
        "不得使用 Write/Edit 手写 runtime metadata",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in combined]

    assert not missing, f"validated runtime metadata contract is incomplete: {missing}"


def test_thin_controller_requires_final_result_hash_binding_order():
    combined = "\n".join(read(path) for path in THIN_CONTROLLER_PROMPTS)

    required_phrases = [
        "不得在 complete-step-worker-dispatch 后修改 StepResult",
        "修改 StepResult 后必须重新运行 validate-step-result 和 complete-step-worker-dispatch",
        "ProgressLedger 中的 step_result_ref 必须绑定最终 StepResult sha256",
        "ProgressLedger 中的 review_result_ref 必须绑定最终 ReviewResult sha256",
        "不得手动修改 progress_ledger.json",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in combined]

    assert not missing, f"final result hash binding contract is incomplete: {missing}"


def test_thin_controller_requires_per_step_review_result_fanout_and_rebinding():
    combined = "\n".join(read(path) for path in THIN_CONTROLLER_PROMPTS)

    required_phrases = [
        "ReviewContextPackage.steps[] 中每个 step 必须恰好对应一个 ReviewResult",
        "禁止返回单个 stage 聚合 ReviewResult",
        "按 ReviewContextPackage.steps[] 顺序",
        "complete-step-worker-dispatch --step-result <step_result_path> --review-result <review_result_path>",
        "全部 review_result_ref 绑定并通过 validate-progress-ledger 后，才允许 build-stage-gate-result",
        "缺失、重复或额外 step 的 ReviewResult 必须 metadata_invalid fail closed",
        "build-stage-gate-result 必须按相同顺序重复传入全部 --review-result",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in combined]

    assert not missing, f"per-step review result closure is incomplete: {missing}"


def test_thin_controller_requires_full_stage_rereview_after_step_redispatch():
    combined = "\n".join(read(path) for path in THIN_CONTROLLER_PROMPTS)
    required_phrases = [
        "Stage review worker不得修改专业artifact或StepResult",
        "prepare-step-worker-dispatch --overwrite-package --overwrite-dispatch",
        "stage_reviews/<stage>/issues_index.json",
        "build-review-context-package --overwrite",
        "重新审核整个stage",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in combined]
    assert not missing, f"stage revision cycle is incomplete: {missing}"


def test_command_and_orchestrator_define_closed_runtime_handoff_protocol():
    required_phrases = [
        "`prepare-step-worker-dispatch` 自动传播已验证的前序 StepResult `artifact_paths`",
        "默认refs → 自动上游refs → 原package额外refs → 新显式 `--input-ref`",
        "按路径稳定去重",
        "只传播 path/hash，不读取 artifact 正文",
        "`issues.json` → `build-stage-review-issues` → `validate-stage-review-issues` → per-step ReviewResult",
        "A2完成 → `build-review-context-package --overwrite` 事务重置并解除旧 stage-review refs → 覆盖 issue set → 全stage复审",
        "`--overwrite-dispatch` 重新派发较早 step 时",
        "删除这些后续 step 的旧 ContextPackage、StepWorkerDispatch 和 ProgressLedger entry",
        "按固定 13-step 顺序重新执行这些下游 step",
        "`issues_index.json` 的 `blocking_issues_count=0`",
        "`decision_scope=stage_review_gate_only`",
        "`professional_approval=false`",
        "`complete-step-worker-dispatch --status` 只是一致性断言",
        "不得覆盖 StepResult 或 ReviewResult 的 status",
    ]
    missing = []

    for path in THIN_CONTROLLER_PROMPTS:
        text = read(path)
        for phrase in required_phrases:
            if phrase not in text:
                missing.append((path.relative_to(ROOT).as_posix(), phrase))

    assert not missing, f"runtime handoff protocol is incomplete: {missing}"


def test_thin_controller_requires_worker_prompt_result_schema():
    combined = "\n".join(read(path) for path in THIN_CONTROLLER_PROMPTS)

    required_phrases = [
        "Step worker prompt 必须包含完整 StepResult 字段列表",
        "kind=step_result",
        "schema_version=1",
        "artifact_hashes",
        "不允许 task_type",
        "不允许 knowledge_gaps_count",
        "不允许 completed_at",
        "Step worker 返回前必须自行运行 validate-step-result",
        "同一个 step worker 修正后重跑 validate-step-result",
        "Review worker prompt 必须包含完整 ReviewResult 字段列表",
        "kind=review_result",
        "review_package_hashes",
        "Review worker 返回前必须自行运行 validate-review-result",
        "同一个 review worker 修正后重跑 validate-review-result",
        "--run-dir <run_dir> --path <result_path>",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in combined]

    assert not missing, f"worker result schema prompt contract is incomplete: {missing}"


def test_thin_controller_requires_immutable_run_refs_and_fail_closed_order():
    combined = "\n".join(read(path) for path in THIN_CONTROLLER_PROMPTS)

    required_phrases = [
        "engine-owned immutable files",
        "StepContextPackage.run_refs[]",
        "不得 Write/Edit/MultiEdit task_brief.json",
        "不得 Write/Edit/MultiEdit manifest.json",
        "Step 1 worker 不得扩展 task_brief.json",
        "validate-step-context-package → validate-step-worker-dispatch → validate-step-result → complete-step-worker-dispatch --step-result <result_path> → validate-progress-ledger",
        "任一命令失败立即 metadata_invalid fail closed",
        "不得开修复 worker 反复修 metadata",
        "worker 只能读取当前用户选择的 task file 以及该 task 声明的 inputs",
        "不得读取 sibling demo",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in combined]

    assert not missing, f"immutable run refs and fail-closed contract is incomplete: {missing}"


def test_thin_controller_does_not_allow_manual_metadata_json_workarounds():
    forbidden_manual_metadata_phrases = [
        "允许手写 orchestration JSON",
        "可以手写 orchestration JSON",
        "手写 StepContextPackage 后继续执行",
        "手写 StepWorkerDispatch 后继续执行",
        "手写 ProgressLedger 后继续执行",
        "手动 patch ledger 后继续执行",
        "validator 失败也可以继续",
        "metadata_invalid 后继续执行",
    ]

    matches = []
    for path in THIN_CONTROLLER_PROMPTS:
        text = read(path)
        for phrase in forbidden_manual_metadata_phrases:
            if phrase in text:
                matches.append((path.relative_to(ROOT).as_posix(), phrase))

    assert not matches, f"thin controller allows manual metadata workarounds: {matches}"


def test_thin_controller_does_not_allow_main_agent_worker_fallback():
    forbidden_fallback_phrases = [
        "允许 fallback 到主上下文",
        "可 fallback 到主上下文",
        "Task tool 不可用时由主 Agent 执行",
        "Task tool 不可用时主 Agent 执行",
        "主 Agent 可自行读取 canonical step 正文",
        "主 Agent 可以自行产出 step artifacts",
    ]

    matches = []
    for path in THIN_CONTROLLER_PROMPTS:
        text = read(path)
        for phrase in forbidden_fallback_phrases:
            if phrase in text:
                matches.append((path.relative_to(ROOT).as_posix(), phrase))

    assert not matches, f"thin controller prompts allow main-agent fallback: {matches}"


def test_thin_controller_prompts_do_not_expand_runtime_context_scope():
    forbidden_context_expansions = [
        "docs/maintainers",
        "examples/**",
        "runs/**",
    ]

    matches = []
    for path in THIN_CONTROLLER_PROMPTS:
        text = read(path)
        for phrase in forbidden_context_expansions:
            if phrase in text:
                matches.append((path.relative_to(ROOT).as_posix(), phrase))

    assert not matches, f"thin controller prompts expand default runtime context: {matches}"
