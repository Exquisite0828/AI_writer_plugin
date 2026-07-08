from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THIN_CONTROLLER_PROMPTS = [
    ROOT / "commands/write.md",
    ROOT / "skills/workflow-orchestrator/SKILL.md",
]


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
        "只把当前 `task_type` 的 document-type path/hash 放进 StepContextPackage",
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
