from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8").lower()


def assert_contains_all(text: str, terms: list[str]) -> None:
    missing = [term for term in terms if term.lower() not in text]
    assert not missing, f"Missing terms: {missing}"


def test_readme_describes_supported_document_types_and_demos() -> None:
    text = read_text("README.md")

    assert_contains_all(
        text,
        [
            "hara",
            "technical_solution",
            "test_report",
            "fsr",
            "专业文档",
            "examples/hara_demo_fixture/task.yaml",
            "examples/technical_solution_zh_demo_fixture/task.yaml",
            "examples/technical_solution_demo_fixture/task.yaml",
            "examples/test_report_demo_fixture/task.yaml",
            "examples/fsr_demo_fixture/task.yaml",
            "/ai-writing-plugin:write",
            "claude plugin validate .",
            "claude --plugin-dir .",
            "runs/<run_id>/",
            "`runs/` 是本地 runtime output",
            "`sample` is not fact source",
            "`reference` is not project-specific fact support",
            "critical claim 必须有 `source` 或 hitl",
            "`final report` 不是专业批准文件",
            "candidate updates remain proposed/inactive",
            "docs/document_type_development_guide.md",
            "docs/troubleshooting.md",
            "docs/reading_outputs.md",
            "docs/readme.md",
            "未实现 tsc",
        ],
    )
    assert "only supports hara" not in text
    assert "automatic professional approval" not in text


def test_quickstart_prioritizes_first_run_plugin_experience() -> None:
    text = read_text("docs/QUICKSTART.md")

    assert_contains_all(
        text,
        [
            "普通用户最短路径",
            "python -m pip install -e \".[dev]\"",
            "claude plugin validate .",
            "只校验 `.claude-plugin/plugin.json`",
            "不会把 `/ai-writing-plugin:write` 加载进当前",
            "claude --plugin-dir .",
            "/ai-writing-plugin:write",
            "examples/technical_solution_zh_demo_fixture/task.yaml",
            "examples/technical_solution_demo_fixture/task.yaml",
            "my_doc_task/task.yaml",
            "inputs/source.md",
            "generic_document",
            "python cli 备用路径",
            "git status --short -- runs/",
            "git ls-files runs/",
            "`runs/` 是本地 runtime output",
            "troubleshooting",
            "reading outputs",
            "`sample` is not fact source",
            "`reference` 不能证明项目事实",
            "tsc / technical safety concept 仍 deferred",
        ],
    )
    assert "普通用户每次写文档都必须运行" in text


def test_troubleshooting_covers_first_run_failures_without_overclaiming() -> None:
    text = read_text("docs/TROUBLESHOOTING.md")

    assert_contains_all(
        text,
        [
            "validate` 通过但插件命令不显示",
            "只校验 manifest",
            "不会把命令加载进当前 claude code 会话",
            "claude --plugin-dir .",
            ".claude-plugin/plugin.json",
            "commands/write.md",
            "pyproject.toml",
            ".venv/bin/python",
            "runs/<run_id>/",
            "git status --short -- runs/",
            "git ls-files runs/",
            "needs_user_confirmation",
            "pending claims",
            "`sample` 或 `reference`",
            "github runner 未必安装 claude code cli",
        ],
    )
    assert "production ready compliance" not in text
    assert "professional approval" not in text
    assert "sales" not in text


def test_demo_instructions_cover_post_n8_demos_and_boundaries() -> None:
    text = read_text("docs/EXAMPLES.md")

    assert_contains_all(
        text,
        [
            "examples/hara_demo_fixture/task.yaml",
            "examples/technical_solution_zh_demo_fixture/task.yaml",
            "examples/technical_solution_demo_fixture/task.yaml",
            "examples/test_report_demo_fixture/task.yaml",
            "examples/fsr_demo_fixture/task.yaml",
            "examples/generic_document_demo_fixture/task.yaml",
            "examples/custom_technical_note_profile_demo_fixture/task.yaml",
            "completed_with_candidate_updates_proposed",
            "open confirmations",
            "candidate update proposed/inactive",
            "reading outputs",
            "`sample` / `reference`",
            "final_report",
            "不是正式批准文件",
            "runs/<run_id>/",
            "tsc",
            "deferred",
        ],
    )


def test_reading_outputs_guide_explains_order_roles_and_boundaries() -> None:
    text = read_text("docs/READING_OUTPUTS.md")

    assert_contains_all(
        text,
        [
            "reading outputs",
            "runs/<run_id>/final/final_report.md",
            "runs/<run_id>/final/delivery_summary.md",
            "runs/<run_id>/review/final_review.md",
            "runs/<run_id>/verify/verify_report.json",
            "runs/<run_id>/plans/claim_support_matrix.json",
            "runs/<run_id>/learning/candidate_profile_update.yaml",
            "user-facing",
            "review and verification",
            "audit/debug",
            "learning proposal",
            "needs_user_confirmation",
            "pending claims",
            "open confirmations",
            "blocked verification",
            "正确输出",
            "proposed/inactive",
            "candidate skill patch",
            "`sample` is not fact source",
            "`reference` is not project-specific fact support",
        ],
    )
    assert "professional approval" not in text
    assert "compliance approval" not in text
    assert "risk acceptance approval" not in text
    assert "production readiness approval" not in text


def test_write_command_is_generic_not_hara_only() -> None:
    text = read_text("commands/write.md")

    assert_contains_all(
        text,
        [
            "/ai-writing-plugin:write",
            "task_type",
            "documenttyperules",
            "python engine",
            "examples/hara_demo_fixture/task.yaml",
            "examples/technical_solution_demo_fixture/task.yaml",
            "examples/test_report_demo_fixture/task.yaml",
            "examples/fsr_demo_fixture/task.yaml",
            "generic_document",
            "custom_technical_note",
            "sample is not fact source",
            "critical claims require evidence or hitl",
            "candidate updates remain proposed/inactive",
        ],
    )
    assert "/write-hara" not in text
    assert "confirm the task goal and hara document type" not in text


def test_runbook_contains_regression_commands_and_boundary_checks() -> None:
    text = read_text("docs/RUNBOOK.md")

    assert_contains_all(
        text,
        [
            ".venv/bin/python -m pytest -q",
            "claude plugin validate .",
            ".venv/bin/python -m ai_writing_plugin write-run --task examples/hara_demo_fixture/task.yaml",
            ".venv/bin/python -m ai_writing_plugin write-run --task examples/technical_solution_demo_fixture/task.yaml",
            ".venv/bin/python -m ai_writing_plugin write-run --task examples/test_report_demo_fixture/task.yaml",
            ".venv/bin/python -m ai_writing_plugin write-run --task examples/fsr_demo_fixture/task.yaml",
            "source_index",
            "citation_plan",
            "sample fact source",
            "candidate_profile_update",
            "active: false",
            "auto_applied: false",
            "runs/",
            "generalization_phase*_execution_package.md",
            "generalization_phase*_handoff.md",
        ],
    )


def test_artifact_contract_states_shared_contract_and_core_tree() -> None:
    text = read_text("docs/CURRENT_ARTIFACT_CONTRACTS.md")

    assert_contains_all(
        text,
        [
            "shared artifact contract",
            "hara",
            "technical_solution",
            "test_report",
            "fsr",
            "artifact contract does not fork by task_type",
            "task_type affects content",
            "inputs/input_inventory.json",
            "knowledge/source_index.json",
            "plans/evidence_map.json",
            "plans/citation_plan.json",
            "draft/full_draft.md",
            "review/review_report.json",
            "verify/verify_report.json",
            "final/final_report.md",
            "learning/candidate_profile_update.yaml",
            "sample is not fact source",
            "reference is not project-specific fact support",
            "critical claims require evidence or hitl",
            "candidate updates remain proposed/inactive",
        ],
    )


def test_document_type_development_guide_covers_extension_flow() -> None:
    text = read_text("docs/DOCUMENT_TYPE_DEVELOPMENT_GUIDE.md")

    assert_contains_all(
        text,
        [
            "docs/document_types/<task_type>_spec.md",
            "ai_writing_plugin/document_types/<task_type>.py",
            "registry",
            "examples/<task_type>_demo_fixture",
            "tests/test_<task_type>_demo.py",
            "skills/document-types/<task_type>/skill.md",
            "task_type",
            "critical_claims",
            "requires_human_confirmation",
            "forbidden_final_claims",
            "sample_policy",
            "reference_policy",
            "candidate_learning_policy",
            "leakage checks",
            "do not copy a pipeline",
            "do not use sample as fact source",
            "do not let reference prove project facts",
            "do not automatically confirm critical claims",
        ],
    )


def test_docs_readme_covers_public_navigation_and_archive_boundary() -> None:
    text = read_text("docs/README.md")

    assert_contains_all(
        text,
        [
            "documentation",
            "quickstart",
            "troubleshooting",
            "reading outputs",
            "user guide",
            "examples",
            "document profiles",
            "runbook",
            "artifact contracts",
            "technical decisions",
            "architecture",
            "roadmap",
            "project context",
            "document type specs",
            "历史 phase docs",
            "不是当前执行指令",
        ],
    )


def test_historical_execution_docs_are_not_tracked_public_docs() -> None:
    assert not (ROOT / "docs" / "archive" / "README.md").exists()
    assert not (ROOT / "docs" / "archive" / "generalization_next_n0_n8" / "README.md").exists()
    assert not (ROOT / "docs" / "archive" / "generalization_phase0_6" / "HANDOFF.md").exists()
    assert not (ROOT / "docs" / "POST_N8_ACCEPTANCE_REPORT.md").exists()


def test_test_report_skill_is_guideline_only_and_preserves_boundaries() -> None:
    text = read_text("skills/document-types/test_report/SKILL.md")

    assert_contains_all(
        text,
        [
            "test_report",
            "test report",
            "guideline",
            "python engine",
            "plugin workflow",
            "pass/fail",
            "defect",
            "coverage",
            "release readiness",
            "needs_user_confirmation",
            "sample not fact source",
            "reference is not project-specific fact support",
            "candidate update proposed/inactive",
            "final report is not approval",
            "skill.md does not replace artifact contract",
        ],
    )
