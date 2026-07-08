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
        "不读取 artifact 正文",
        "不得粘贴 artifact 正文",
        "不得批量读取 step canonical",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in combined]

    assert not missing, f"thin controller prompt contract is incomplete: {missing}"


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
